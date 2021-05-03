#!/bin/bash

set -eo pipefail

function build {
	make -C $1 build
}

function publish {
	make -C $1 publish
}

case "$1" in
	build)
		for version in *; do
			if [ -d "${version}" ]; then
				echo "Building $version"
				build $version
			fi
		done
	;;
	publish)
		for version in *; do
			if [ -d "${version}" ]; then
				echo "Publishing: $version"
				publish $version
			fi
		done
	;;
esac
