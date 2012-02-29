.PHONY: tests dist

tests:
	nosetests --with-coverage --cover-package=figs --tests=tests

dist:
	python setup.py sdist

upload:
	python setup.py sdist upload
