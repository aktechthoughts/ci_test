setup:	conda-ci-setup environment

SHELL := /bin/bash -o pipefail -o errexit
# Folder for all the build artefacts to be archived by CI.
artefacts_path := artefacts
# File to collect information that is posted as PR comment
pr_comment_file := $(artefacts_path)/pr-comment.md
# Blenda branch to receive updates from
CITEST_UPDATE_BRANCH := master
ENVNAME := oa$(RANDOM_SUFFIX)
TEST_CONDA_LOCATION := $(HOME)/conda_oa

mr-clean:
	$(call print_status_noprc,Delete everything not known to git)
	git clean -fdx;
	# rm -rf $(TEST_CONDA_LOCATION) ~/.condarc

conda-ci-setup:
	$(call print_status_noprc,Setup conda)
	export PATH=$(TEST_CONDA_LOCATION)/bin:$$PATH; hash -r; \
	if ! type "conda" > /dev/null; then \
		wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh; \
		bash miniconda.sh -b -p $(TEST_CONDA_LOCATION); \
		rm miniconda.sh; \
		conda config --set always_yes yes --set changeps1 no; \
		conda update -q conda; \
	else \
		echo "Speeding up"; \
	fi; \
	conda config --set always_yes yes --set changeps1 no; \
	# Useful for debugging any conda issues; \
	conda info -a
