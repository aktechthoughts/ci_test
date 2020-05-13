setup:	conda-ci-setup environment
full-ci:	info git-size-metrics lint-tests test check-clean success

SHELL := /bin/bash -o pipefail -o errexit
# Folder for all the build artefacts to be archived by CI.
artefacts_path := artefacts
# File to collect information that is posted as PR comment
pr_comment_file := $(artefacts_path)/pr-comment.md
# A branch to receive updates from
CITEST_UPDATE_BRANCH := master
ENVNAME := ci_test$(RANDOM_SUFFIX)
TEST_CONDA_LOCATION := $(HOME)/ci_test

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

post-ci-clean:
	export PATH=$(TEST_CONDA_LOCATION)/bin:$$PATH; hash -r; \
	conda init bash; \	
	conda deactivate; \
	conda env remove -n $(ENVNAME) || true


conda-full-ci:
	$(call print_status_noprc,Activating conda environment)
	export PATH=$(TEST_CONDA_LOCATION)/bin:$$PATH; hash -r; \
	source activate $(ENVNAME); \
	make full-ci 2>&1 | tee -a $(artefacts_path)/console.log

environment:	install-exaplus
	$(call print_status,Creating environment)
	export PATH=$(TEST_CONDA_LOCATION)/bin:$$PATH; hash -r; \
	conda config --set always_yes yes --set changeps1 no; \
	conda env create --name $(ENVNAME) --file .ci/environment.yml --force

install-exaplus:
	$(call print_status_noprc,Installing EXAplus)
	bash .ci/get_exaplus.sh

info:
	$(call print_status_noprc,Print/collect environment information)
	conda info -a || true
	pip list --format=columns || true
	pip list --outdated || true
	conda env export --file $(artefacts_path)/environment.yaml
	(cd .ci/spotless && bash ./gradlew dependencyUpdate || true)

git-size-metrics:
	$(call print_status,Checking git size metrics)
	printf "\n\`\`\`\n" >> $(pr_comment_file)
	git-sizer --no-progress 2>&1 | tee -a $(pr_comment_file)
	printf "\`\`\`\n\n" >> $(pr_comment_file)

lint-tests:
	$(call print_status,Linting test code with pylint/flake8/spotless)
	PACKAGES=$$(python -c "from setuptools import find_packages; print(' '.join({p.split('.')[0] + '/' for p in find_packages()}))"); \
	pylint --rcfile=".ci/pylintrc" --output-format=parseable tests/ 2>&1 | tee $(artefacts_path)/pylint.log
	printf "\n\`\`\`" >> $(pr_comment_file)
	cat $(artefacts_path)/pylint.log >> $(pr_comment_file)
	flake8 --config=.ci/flake8 tests/ 2>&1 | tee $(artefacts_path)/flake8.log
	cat $(artefacts_path)/flake8.log >> $(pr_comment_file)
	(cd .ci/spotless && bash ./gradlew spotlessGroovyCheck)
	printf "\`\`\`\n\n" >> $(pr_comment_file)

test:
	$(call print_status,Testing)
	export PATH=.build/exaplus:$$PATH; hash -r; \
	printf "\n\`\`\`\n" >> $(pr_comment_file); \
	python -m pytest --junit-xml="artefacts/test-report.xml" --html="artefacts/test-report.html" --self-contained-html --show-capture=all . 2>&1 | tee -a $(pr_comment_file)
	printf "\`\`\`\n\n" >> $(pr_comment_file)		

check-clean:
	$(call print_status_noprc,Check for clean worktree)
	@GIT_STATUS="$$(git status --porcelain)"; \
  if [ ! "x$$GIT_STATUS" = "x"  ]; then \
    echo "Your worktree is not clean, there is either uncommitted code or \
    there are untracked files:"; \
    echo "$${GIT_STATUS}"; \
    exit 1; \
  fi


style:
	$(call print_status,Styling with black/beautysh/spotless)
	find . -name "*.py" -exec black {} +
	find . -name "*.sh" -exec beautysh --tab {} +
	(cd .ci/spotless && bash ./gradlew spotlessGroovyApply)

style-sql:
	$(call print_status,Styling SQL with spotless/DBeaver)
	(cd .ci/spotless && ln -s ../../ddl src && bash ./gradlew spotlessSqlApply)

success:
	$(call print_status,Success)  

define print_status
	$(call print_status_noprc, $(1))
	@echo "* $(1)" >> $(pr_comment_file)
endef

define print_status_noprc
	@echo "############################################"; \
	echo "#"; \
	echo "#    "$(1); \
	echo "#"; \
	echo "############################################"
	@mkdir -p $(artefacts_path)
endef	