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

.PHONY: build build-*

.PHONY: build build-*
build: build-vep-tool

build-%:
	@echo
	@echo -- Building docker --
	@make -C $* build-docker NAME=$*

.PHONY: publish-staging publish-staging-% publish-release publish-release-%

publish-staging: publish-staging-vep-tool
publish-staging-%:
	@echo
	@make -C $* publish-staging

publish-release: publish-release-vep-tool
publish-release-%:
	@echo
	@make -C $* publish-release
