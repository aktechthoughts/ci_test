
setup:	conda-ci-setup environment

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
