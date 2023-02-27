import inspect
import warnings
from importlib import import_module
from types import ModuleType
from typing import Callable, Generator, List, Tuple

import click
from flask import Blueprint
from flask_marshmallow.schema import Schema
from flask_sqlalchemy import Model


def get_members(
    module: ModuleType, predicate: Callable[[str, object], bool]
) -> Generator[Tuple[str, object], None, None]:
    """Get all the members of a module that match a predicate.

    Like inspect.getmembers except predicate is passed both name and object.

    Parameters
    ----------
    module : ModuleType
        The module to inspect.
    predicate : Callable
        A function that takes a name and object and returns a boolean.

    Returns
    -------
    tuple
        An iterable of (name, obj) tuples for all members of the module.
    """

    for name, obj in inspect.getmembers(module):
        if predicate(name, obj):
            yield (name, obj)


def is_extension(name: str, obj: object) -> bool:
    """A predicate function to check if an object is an extension.

    Checks if the object is an extension.

    Parameters
    ----------
    name : str
        The name of the object.
    obj : object
        The object to check.

    Returns
    -------
    bool
        True if the object is an extension, False otherwise.
    """
    # we want *instantiated* extensions, not imported extension classes.

    base_classes = ()
    return (
        not inspect.isclass(obj)
        and hasattr(obj, "init_app")
        and name not in base_classes
    )


def is_blueprint(name: str, obj: object) -> bool:
    """A predicate function to check if an object is a blueprint.

    Checks if the object is a blueprint.

    Parameters
    ----------
    name : str
        The name of the object.
    obj : object
        The object to check.

    Returns
    -------
    bool
        True if the object is a blueprint, False otherwise.
    """

    base_classes = ()
    return isinstance(obj, Blueprint) and name not in base_classes


def is_click_command(name: str, obj: object) -> bool:
    """A predicate function to check if an object is a click command.

    Checks if the object is a click command.

    Parameters
    ----------
    name : str
        The name of the object.
    obj : object
        The object to check.

    Returns
    -------
    bool
        True if the object is a click command, False otherwise.
    """

    base_classes = ()
    return (
        isinstance(obj, click.Command)
        and not isinstance(obj, click.Group)
        and name not in base_classes
    )


def is_click_group(name: str, obj: object) -> bool:
    """A predicate function to check if an object is a click group.

    Checks if the object is a click group.

    Parameters
    ----------
    name : str
        The name of the object.
    obj : object
        The object to check.

    Returns
    -------
    bool
        True if the object is a click group, False otherwise.
    """

    base_classes = ()
    return isinstance(obj, click.Group) and name not in base_classes


def is_click_command_or_group(name: str, obj: object) -> bool:
    """A predicate function to check if an object is a click command or group.

    Checks if the object is a click command or group.

    Parameters
    ----------
    name : str
        The name of the object.
    obj : object
        The object to check.

    Returns
    -------
    bool
        True if the object is a click command or group, False otherwise.
    """

    base_classes = ()
    return (
        is_click_command(name=name, obj=obj)
        or is_click_group(name=name, obj=obj)
        and name not in base_classes
    )


def is_model(name: str, obj: object) -> bool:
    """A predicate function to check if an object is a model.

    Checks if the object is a model.

    Parameters
    ----------
    name : str
        The name of the object.
    obj : object
        The object to check.

    Returns
    -------
    bool
        True if the object is a model, False otherwise.
    """

    is_model_class = inspect.isclass(obj) and issubclass(obj, Model)
    base_classes = ("Model",)

    return is_model_class and name not in base_classes


def is_serializer(name: str, obj: object) -> bool:
    """A predicate function to check if an object is a serializer.

    Checks if the object is a serializer.

    Parameters
    ----------
    name : str
        The name of the object.
    obj : object
        The object to check.

    Returns
    -------
    bool
        True if the object is a serializer, False otherwise.
    """

    is_model_schema = inspect.isclass(obj) and issubclass(obj, Schema)
    base_classes = ("SQLAlchemySchema", "SQLAlchemyAutoSchema")

    return is_model_schema and name not in base_classes


def get_extensions(
    import_names: List[str],
) -> Generator[Tuple[str, object], None, None]:
    """A Helper function to get the extensions from the import_names list.

    Parameters
    ----------
    import_names : List[str], order is important
        A list of import names in the form of "module_name:instance_name"

    Returns
    -------
    tuple
        An iterable of (instance_name, extension_instance) tuples.
    """

    extension_modules = {}
    for import_name in import_names:
        module_name, extension_name = import_name.rsplit(":")

        if module_name not in extension_modules:
            module = import_module(module_name)
            extension_modules[module_name] = dict(get_members(module, is_extension))

        extension_module = extension_modules[module_name]
        if extension_name in extension_module:
            yield extension_name, extension_module[extension_name]
        else:
            warnings.warn(
                f"Could not find the {extension_name} extension in the {module_name} module (did you forget to instantiate it?)"
            )


def get_blueprints() -> Generator[Tuple[str, object], None, None]:
    """A Helper function to get the blueprints list.

    Returns
    -------
    tuple
        An iterable of (name, blueprint_instance) tuples.
    """

    from backend.extensions import blueprints

    yield from get_members(blueprints, is_blueprint)


def get_models() -> Generator[Tuple[str, object], None, None]:
    """A Helper function to get the models list.

    Returns
    -------
    tuple
        An iterable of (name, model_instance) tuples.
    """

    from backend import models

    yield from get_members(models, is_model)


def get_serializers() -> Generator[Tuple[str, object], None, None]:
    """A Helper function to get the serializers list.

    Returns
    -------
    tuple
        An iterable of (name, serializer_instance) tuples.
    """

    from backend import serializers

    yield from get_members(serializers, is_serializer)


def get_commands() -> Generator[Tuple[str, object], None, None]:
    """A Helper function to get the commands list.

    Returns
    -------
    tuple
        An iterable of (name, command_instance) tuples.
    """

    from backend import commands

    existing_group_commands = {}
    for name, group in get_members(commands, is_click_group):
        existing_group_commands.update(group.commands)
        if name not in commands.EXISTING_EXTENSION_GROUPS:
            yield (name, group)

    def _is_click_command(name: str, obj: object) -> bool:
        return (
            is_click_command(name=name, obj=obj) and name not in existing_group_commands
        )

    yield from get_members(commands, _is_click_command)
