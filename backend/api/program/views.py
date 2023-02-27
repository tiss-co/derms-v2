import ast
from http import HTTPStatus

from flask import jsonify
from sqlalchemy import or_, and_

from backend.extensions.blueprints import program
from backend.models import Program, Battery
from backend.serializers.program import ProgramSchema
from backend.api.validators.program_validator import (
    validate_create_program,
    validate_edit_program,
)


@program.route("/", methods=["POST"])
def create_program():

    data = validate_create_program()
    battery_obj = Battery.get(id=data["battery_id"])
    if not battery_obj:
        return (
            jsonify({"status": f"No battery with id {data['battery_id']}"}),
            HTTPStatus.NOT_FOUND,
        )
    program_obj = (
        Program.filter_by(battery_id=data["battery_id"])
        .filter(or_(Program.name == data["name"], Program.priority == data["priority"]))
        .first()
    )

    if program_obj:
        return (
            jsonify(
                {
                    "status": f"Program {program_obj.name} with priority {program_obj.priority} is already assigned to battery"
                }
            ),
            HTTPStatus.NOT_FOUND,
        )
    new_program = Program(**data)
    new_program.save(commit=True)

    return (""), HTTPStatus.CREATED


@program.route("/<program_id>", methods=["GET"])
def get(program_id):

    program_obj = Program.get(id=program_id)
    return ProgramSchema().dump(program_obj), HTTPStatus.OK


@program.route("/<program_id>", methods=["PUT"])
def put(program_id):

    data = validate_edit_program()

    body = ast.literal_eval(str(data))
    program_obj = Program.get(id=program_id)

    if not program_obj:
        return (
            jsonify({"status": f"No program found with id {program_id}"}),
            HTTPStatus.NOT_FOUND,
        )

    program_query = Program.filter(
        and_(Program.battery_id == program_obj.battery_id, Program.id != program_obj.id)
    )
    conditions = []
    if "priority" in data:
        conditions.append(Program.priority == data["priority"])
    if "name" in data:
        conditions.append(Program.name == data["name"])

    if conditions:
        duplicate_program = program_query.filter(or_(*conditions)).first()

        if duplicate_program:
            return (
                jsonify(
                    {
                        "status": f"Program {duplicate_program.name} with priority {duplicate_program.priority} is already assigned to battery"
                    }
                ),
                HTTPStatus.NOT_FOUND,
            )

    program_obj.update(**body)
    program_obj.save(commit=True)

    return (""), HTTPStatus.OK


@program.route("/<program_id>", methods=["DELETE"])
def delete(program_id):

    program_obj = Program.get(id=program_id)
    if not program_obj:
        return (
            jsonify({"status": f"No program found with id {program_id}"}),
            HTTPStatus.NOT_FOUND,
        )
    program_obj.delete(commit=True)

    return (""), HTTPStatus.OK
