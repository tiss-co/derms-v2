## supported distros: Ubuntu/Debian/Mint
VERSION = v0.1.0

## constants
# (help: https://stackoverflow.com/a/5947802)
# red, green, yellow & no color
RC = \e[1;31m
GC = \e[1;32m
YC = \e[1;33m
NC = \e[0m
PYTHON_VERSION = `head -1 .python-version`

##  export common variable into shell
# (help: https://stackoverflow.com/a/8942216)
export PATH := ${HOME}/.pyenv/bin:${HOME}/.local/bin:$(PATH)

# (help: https://stackoverflow.com/a/2122723)
_PYTHON_VERSION := $(shell head -1 .python-version || echo "3.8.12" > .python-version)

## Makefile help recipe
# (help: https://stackoverflow.com/a/64996042)
help:	## show helps.
	@echo '                                                                             '
	@echo ' --------------------------------------------------------------------        '
	@echo ' The Distributed Energy Resource Management System (DERMS) is battery        '
	@echo ' management system to determine the optimal daily dispatch of batteries      '
	@echo ' (i.e., the amount of charging and discharging power of batteries)           '
	@echo ' --------------------------------------------------------------------        '
	@echo '                                                                             '
	@echo ' Usage: make <command> (supported distros: Ubuntu/Debian/Mint)               '
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-30s\033[0m %s\n", $$1, $$2}'
	@echo '                                                                             '

## Makefile main recipe
pkgs-update:	## update system packages using apt package manager.
	# grant memoryless `sudo` privilege.
	sudo -k apt-get update --yes --fix-missing || true
	sudo -k apt-get upgrade --yes --fix-missing || true

prerequisites: pkgs-update	## install dependencies using apt package manager.
	# grant memoryless `sudo` privilege.
	sudo -k apt-get install make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git python3 python3-pip python3-wheel python3-setuptools python3-venv --yes --fix-missing

poetry-core: prerequisites  ## install the poetry python dependency manager.
	python3 -m pip install --upgrade pip --verbose
	python3 -m pip install virtualenv --verbose
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python3 -
	poetry self update
	poetry config virtualenvs.in-project true
	echo "" >> ${HOME}/.bashrc; printf '\n# poetry\n. <(poetry completions bash)' >> ${HOME}/.bashrc
	echo "" >> ${HOME}/.zshrc; printf '\n# poetry\n. <(poetry completions zsh)' >> ${HOME}/.zshrc

pyenv-core: prerequisites	## install the pyenv python version manager.
	curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
	pyenv update
	echo "" >> ${HOME}/.profile; cat ${HOME}/.profile > ${HOME}/.profile.bak; printf '# pyenv environment variables\nexport PYENV_ROOT="${HOME}/.pyenv"\nexport PATH="$$PYENV_ROOT/bin:${HOME}/.local/bin:$$PATH"\n\n' > ${HOME}/.profile; cat ${HOME}/.profile.bak >> ${HOME}/.profile
	echo "" >> ${HOME}/.bash_profile; cat ${HOME}/.bash_profile > ${HOME}/.bash_profile.bak; printf '# pyenv environment variables\nexport PYENV_ROOT="${HOME}/.pyenv"\nexport PATH="$$PYENV_ROOT/bin:${HOME}/.local/bin:$$PATH"\n\n' > ${HOME}/.bash_profile; cat ${HOME}/.bash_profile.bak >> ${HOME}/.bash_profile
	echo "" >> ${HOME}/.zprofile; cat ${HOME}/.zprofile > ${HOME}/.zprofile.bak; printf '# pyenv environment variables\nexport PYENV_ROOT="${HOME}/.pyenv"\nexport PATH="$$PYENV_ROOT/bin:${HOME}/.local/bin:$$PATH"\n\n' > ${HOME}/.zprofile; cat ${HOME}/.zprofile.bak >> ${HOME}/.zprofile
	printf '\n\n# pyenv\neval "$$(pyenv init --path)"' >> ${HOME}/.profile
	printf '\n\n# pyenv\neval "$$(pyenv init --path)"' >> ${HOME}/.bash_profile
	printf '\n\n# pyenv\neval "$$(pyenv init --path)"' >> ${HOME}/.zprofile
	echo "" >> ${HOME}/.bashrc; printf '\n# pyenv\neval "$$(pyenv init -)"' >> ${HOME}/.bashrc
	echo "" >> ${HOME}/.zshrc; printf '\n# pyenv\neval "$$(pyenv init -)"' >> ${HOME}/.zshrc

pyenv: pyenv-core	## install the pyenv python version manager with the required python version.
	pyenv install ${PYTHON_VERSION} --verbose
	pyenv global ${PYTHON_VERSION}
	. ${HOME}/.profile || true; python -m pip install --upgrade pip --verbose
	. ${HOME}/.profile || true; python -m pip install virtualenv --verbose
	pyenv global system

dev: poetry-core pyenv	## setup the development environment (extends `poetry-core` && `pyenv`).
	printf "\n${GC}Done! ${YC}The system ${RC}must restart${YC} for these changes to take effect...\n\n${NC}"
	. ${HOME}/.profile || true
	exec "$$SHELL" || true

venv:	## setup the python virtual environment with poetry for production purposes.
	pyenv local ${PYTHON_VERSION}
	poetry env use ${PYTHON_VERSION}
	poetry install --no-dev

activate: venv	## activate the production python virtual environment shell (extends `venv`).
	poetry update --no-dev
	poetry shell

venv-dev:	## setup the python virtual environment with poetry for development purposes.
	pyenv local ${PYTHON_VERSION}
	poetry env use ${PYTHON_VERSION}
	poetry install

activate-dev: venv-dev	## activate the development python virtual environment shell (extends `venv-dev`).
	poetry update
	poetry shell

export: activate	## export the python virtual environment installed packages to the `requirements.txt` file.
	poetry export -f requirements.txt --output requirements.txt --without-hashes

build: activate	## build the project with poetry.
	poetry build

py-build: activate	## build the project with python setuptools.
	python setup.py build
	python setup.py bdist_wheel

docker-build:	## build the Dockerfile.
	docker build --no-cache=true --tag tiss-co/notification-service:${VERSION} --file Dockerfile .

docker-run:	docker-build	## run the built image.
	docker rm notification-service || true
	docker run --interactive --tty --name notification-service tiss-co/notification-service:${VERSION}

docker-debug: docker-run	## debug the running container.
	docker exec --interactive --tty --user root notification-service bash