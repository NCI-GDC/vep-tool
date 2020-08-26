# Makefile for developing an individual Docker image

VERSION = 1.0
DOCKER_REPO = vep-tool

GIT_SHORT_HASH:=$(shell git rev-parse --short HEAD)
COMMIT_HASH:=$(shell git rev-parse HEAD)

DOCKER_URL := quay.io/ncigdc
DOCKER_IMAGE_COMMIT := ${DOCKER_URL}/${DOCKER_REPO}:${COMMIT_HASH}
DOCKER_IMAGE_LATEST := ${DOCKER_URL}/${DOCKER_REPO}:latest
DOCKER_IMAGE_STAGING := ${DOCKER_URL}/${DOCKER_REPO}:staging
DOCKER_IMAGE := ${DOCKER_URL}/${DOCKER_REPO}:${VERSION}

.PHONY: version version-* name
name:
	@echo ${NAME}

version:
	@echo --- VERSION: ${VERSION} ---

version-docker:
	@echo ${DOCKER_IMAGE_COMMIT}
	@echo ${DOCKER_IMAGE}

.PHONY: docker-*
docker-login:
	@echo
	docker login -u=${QUAY_USERNAME} -p=${QUAY_PASSWORD} quay.io

.PHONY: run run-*
run:
	@echo "Running command!"

run-docker:
	# Docker should have:
	# ENTRYPOINT ["make"]
	# RUN ["run"]
	# Add other commands as make targets if needed
	@docker run --rm ${DOCKER_IMAGE_LATEST}

.PHONY: build build-*

build: build-docker

build-docker:
	@echo
	@echo -- Building docker --
	docker build . \
		--file ./Dockerfile \
		--build-arg NAME=${NAME} \
		-t "${DOCKER_IMAGE_COMMIT}" \
		-t "${DOCKER_IMAGE}" \
		-t "${DOCKER_IMAGE_LATEST}"

.PHONY: publish publish-staging publish-release

publish: docker-login
	docker push ${DOCKER_IMAGE_COMMIT}

publish-staging: docker-login publish
	docker tag ${DOCKER_IMAGE_LATEST} ${DOCKER_IMAGE_STAGING}
	docker push ${DOCKER_IMAGE_STAGING}

publish-release: docker-login publish
	docker tag ${DOCKER_IMAGE_LATEST} ${DOCKER_IMAGE}
	docker push ${DOCKER_IMAGE_LATEST}
	docker push ${DOCKER_IMAGE}
