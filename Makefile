WITH_ENV = env `cat .env 2>/dev/null | xargs`

compile-deps:
	@[ -n "$(VIRTUAL_ENV)" ] || (echo 'out of virtualenv'; exit 1)
	@$(WITH_ENV) pip3 install -U pip setuptools wheel
	@$(WITH_ENV) pip3 install -U pip-tools
	@$(WITH_ENV) pip-compile -U requirements.in
	@$(WITH_ENV) pip-compile -U requirements.in requirements-test.in --output-file=requirements-dev.txt

install-deps:
	@[ -n "$(VIRTUAL_ENV)" ] || (echo 'out of virtualenv'; exit 1)
	@$(WITH_ENV) pip3 install -U pip setuptools wheel
	@$(WITH_ENV) pip3 install -r requirements-dev.txt

clean:
	@rm -f dist/*
	@find . -name '*.pyc' -or -name '*.pyo' -or -name '__pycache__' -type f -delete
	@find . -type d -empty -delete

lint:
	@[ -n "$(VIRTUAL_ENV)" ] || (echo 'out of virtualenv'; exit 1)
	@$(WITH_ENV) flake8

dist: clean
	@[ -n "$(VIRTUAL_ENV)" ] || (echo 'out of virtualenv'; exit 1)
	@$(WITH_ENV) python3 ./setup.py bdist_wheel
