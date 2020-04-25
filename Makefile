
setup:	conda-ci-setup environment

mr-clean:
	$(call print_status_noprc,Delete everything not known to git)
	git clean -fdx;
	# rm -rf $(TEST_CONDA_LOCATION) ~/.condarc