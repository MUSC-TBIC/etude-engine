.PHONY: clean clean-pyc clean-build clean-test test test3.7 test3.5 test2.7 docs

#### Sources of inspiration and reference:
##
## - https://krzysztofzuraw.com/blog/2016/makefiles-in-python-projects.html
## - https://gist.github.com/lumengxi/0ae4645124cd4066f676

clean-pyc:
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-build:
	rm -rf src/*.egg-info

clean-test:
	rm -f .coverage
	rm -rf cov_html_py3.7
	rm -rf cov_html_py3.5
	rm -rf cov_html_py2.7

clean: clean-pyc clean-build clean-test

test: clean-pyc
	python3.7 -m pytest --cov-report html:cov_html_py3.7 tests

test3.7: test

test3.5: clean-pyc
	python3.5 -m pytest --cov-report html:cov_html_py3.5 tests

test2.7: clean-pyc
	python2.7 -m pytest --cov-report html:cov_html_py2.7 tests

## TODO
##dist: clean
##	python3.7 setup.py sdist
##	python3.7 setup.py bdist_wheel
##	ls -l dist
##
##release-test:
##	python3.7 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/etude_eval_engine-${VERSION}*
