all: init docs test

init:
	python setup.py develop
	pip install tox coverage Sphinx

test:
	coverage erase
	tox
	coverage html

picky:
	flake8 --max-line-length=100 --max-complexity=10 --statistics --benchmark badgekit_webhooks

docs: documentation

documentation:
	python setup.py build_sphinx
