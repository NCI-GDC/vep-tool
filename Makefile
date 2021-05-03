# Template Makefile for repositories with one or more Docker images

REPO = vep-tool

.PHONY: init init-*

init: init-hooks init-secrets

init-hooks:
	@echo
	pre-commit install

init-secrets:
	@echo
	detect-secrets scan --update .secrets.baseline
	detect-secrets audit .secrets.baseline

.PHONY: docker-*
docker-login:
	@echo
	docker login -u="${QUAY_USERNAME}" -p="${QUAY_PASSWORD}" quay.io

.PHONY: build
build:
	@bash build.sh build

.PHONY: publish
publish:
	@bash build.sh publish

