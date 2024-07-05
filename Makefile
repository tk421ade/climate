#
# Install dependencies
# apt install make virtualenvwrapper -y

clean:
	rm -rf venv
	find . -name '*.pyc ' -delete

prepare:clean
	set -ex
	virtualenv venv -p /usr/bin/python3
	venv/bin/pip3 install -r requirements.txt
	#venv/bin/pip install .

test:prepare
	venv/bin/pip3 install mock nose
	venv/bin/python3 setup.py nosetests

migrate:
	venv/bin/python3 manage.py makemigrations
	venv/bin/python3 manage.py migrate

update:
	venv/bin/python3 climate/climate/botrss.py