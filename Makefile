WITH_ENV = env `cat .env 2>/dev/null | xargs`

compile-deps:
	@[ -n "$(VIRTUAL_ENV)" ] || (echo 'out of virtualenv'; exit 1)
	@$(WITH_ENV) pip install -U pip setuptools wheel
	@$(WITH_ENV) pip install -U pip-tools
	@$(WITH_ENV) pip-compile -U requires/requirements.in requires/postgres.in requires/redis.in requires/dev.in --output-file requirements.txt

install-deps:
	@[ -n "$(VIRTUAL_ENV)" ] || (echo 'out of virtualenv'; exit 1)
	@$(WITH_ENV) pip install -U pip setuptools wheel
	@$(WITH_ENV) pip install -U pip-tools
	@$(WITH_ENV) pip-sync requirements.txt

clean:
	@rm -rf dist/*
	@rm -rf build/*
	@rm -rf tornado_widgets.egg-info/*
	@find . -name '*.pyc' -or -name '*.pyo' -or -name '__pycache__' -type f -delete
	@find . -type d -empty -delete

lint:
	@[ -n "$(VIRTUAL_ENV)" ] || (echo 'out of virtualenv'; exit 1)
	@$(WITH_ENV) flake8

dist: clean
	@[ -n "$(VIRTUAL_ENV)" ] || (echo 'out of virtualenv'; exit 1)
	@$(WITH_ENV) python setup.py bdist_wheel
