#!/bin/bash


# set -o errtrace -o nounset -o pipefail -o errexit

# # Change the next two lines for version update
# EXAPLUS_VERSION="6.0.15"
# EXAPLUS_SHA1SUM="eb946d117eaf34c0ec2e76c8fb65fa7d2ddc93d3"

# EXAPLUS_URL="https://www.exasol.com/support/secure/attachment/79638/EXAplus-${EXAPLUS_VERSION}.tar.gz"
# BUILD_FOLDER="$(dirname "${BASH_SOURCE[0]}")/../.build"

# temp_file=$(mktemp)
# trap 'rm -f $temp_file' 0 2 3 1
# echo "${EXAPLUS_SHA1SUM} ${HOME}/exaplus-${EXAPLUS_VERSION}.tar.gz" > "${temp_file}"

# echo "### Check if EXAplus is already correctly downloaded"
# if [ -f "${HOME}/exaplus-${EXAPLUS_VERSION}.tar.gz" ]; then
# 	sha1sum -c "${temp_file}" || rm -f "${HOME}/exaplus-${EXAPLUS_VERSION}.tar.gz"
# fi

# echo "### Download and check EXAplus if required"
# if [ ! -f "${HOME}/exaplus-${EXAPLUS_VERSION}.tar.gz" ]; then
# 	wget "${EXAPLUS_URL}" -O "${HOME}/exaplus-${EXAPLUS_VERSION}.tar.gz"
# 	sha1sum -c "${temp_file}"
# fi
# rm -f "${temp_file}"

# echo "### Check if EXAplus is already extracted"
# if [ -f "${BUILD_FOLDER}/exaplus/exaplus" ]; then
# 	echo "EXAplus is already installed in ${BUILD_FOLDER}/exaplus, speeding up."
# 	exit 0
# fi

# echo "### Extract EXAplus"
# mkdir -p "${BUILD_FOLDER}/exaplus"
# tar -xzvf "${HOME}/exaplus-${EXAPLUS_VERSION}.tar.gz" --strip-components=1 -C "${BUILD_FOLDER}/exaplus"

# echo "Done"
