LINTER_DIRS := tests
APOLO_COMMAND=apolo --verbose --show-traceback --color=no
TMP_DIR := $(shell mktemp -d)
VERSION_FILE := version.txt

.PHONY: setup init
setup init:
	pip install -r requirements/dev.txt
	pipx install apolo-all
	pre-commit install

.PHONY: get-version
get-version: $(VERSION_FILE)
	cat $(VERSION_FILE)

.PHONY: update-version
update-version:
	echo "v`date +"%y.%m.%d"`" > $(VERSION_FILE)

.PHONY: lint
lint: format
	 mypy $(LINTER_DIRS)

.PHONY: format
format:
	pre-commit run --all-files --show-diff-on-failure

.PHONY: test
test:
	 export TMP_DIR=$$(mktemp -d) && \
	   cookiecutter --no-input --config-file ./tests/cookiecutter.yaml --output-dir $$TMP_DIR . && \
	   ls -d "$$TMP_DIR/test flow/.apolo/"
	 pytest -v -n auto tests/unit
	 pytest -v -n auto tests/e2e
	 @echo -e "OK\n"

.PHONY: changelog-draft
changelog-draft: update-version $(VERSION_FILE)
	towncrier --draft --name "Apolo Platform Flow Template" --version `cat version.txt`

.PHONY: changelog
changelog: update-version $(VERSION_FILE)
	towncrier --name "Apolo Platform Flow Template" --version `cat version.txt` --yes
