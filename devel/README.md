# Development

Setup the development environment.

## MacOS
### Install Python Version(s)

````bash
# upgrade to latest pip3
python3 -m pip install --upgrade pip

brew install pyenv

pip3 install virtualenv

pyenv install 3.8.10
# bin: ~/.pyenv/versions/3.8.10/bin/python3

````

### Install & Activate Python Virtual Env

````bash
mkdir ./venvs
cd venvs
# create virtual env
virtualenv -p ~/.pyenv/versions/3.8.10/bin/python3 venv3.8.10
# activate virtual env
source venv3.8.10/bin/activate
# check
(venv3.8.10) ...$ python3 -V

````
### Upgrade pip
````bash
(venv3.8.10) ...$ python3 -m pip install --upgrade pip
````
### Install Ansible Version Required
````bash
# install the devel version required
(venv3.8.10) ...$ pip install "ansible>=5.1.0,<6.0.0" # this is 2.12
# check
(venv3.8.10) ...$ ansible --version
````

### Install Devel Requirements in Python Virtual Env
````bash
(venv3.8.10) ...$ cd devel
(venv3.8.10) ...$ pip install -r devel.requirements.txt
(venv3.8.10) ...$ pip install -r ../src/ansible_collections/solace/pubsub_plus/requirements.txt
````

### Activate Ansible-Solace Collection Devel Env
````bash
(venv3.8.10) ...$ source {root}/devel/bin/asc-devel-activate
(asc-devel)(venv3.8.10) ...$ asc-devel-show

output:
env vars & links
````

### Deactivate Ansible-Solace Collection Devel Env
````bash
(asc-devel)(venv3.8.10) ...$ asc-devel-deactivate
(venv3.8.10) ...$
````

### Deactivate Python Virtual Env
````bash
(venv3.8.10) ...$ deactivate
...$
````

## Tests

### ansible-test
````bash
cd src/ansible_collections/solace/pubsub_plus
# single module
ansible-test sanity {module_name}
# project
ansible-test sanity
````

**See also [sanity ignore file(s)](../src/ansible_collections/solace/pubsub_plus/tests/sanity)**.


### docs
````bash
pip3 install ansible-doc-extractor
# check make version
make --version
  GNU Make 3.81 # <- min version
````

#### Create the rst file:
````bash
cd src/ansible_collections/solace/pubsub_plus/docs
ansible-doc-extractor --template source/_templates/module.rst.j2 source/modules ../plugins/modules/{module}.py
# check generated rst
ls source/modules/{module}.rst
````
#### Create the html:
````bash
cd src/ansible_collections/solace/pubsub_plus/docs
make html
# point browser to
{your-path}/src/ansible_collections/solace/pubsub_plus/docs/build/html/index.html
{your-path}/src/ansible_collections/solace/pubsub_plus/docs/build/html/modules/{module}.html
````

#### Check the links:
````bash
cd src/ansible_collections/solace/pubsub_plus/docs
make linkcheck
# output in
{your-path}/src/ansible_collections/solace/pubsub_plus/docs/build/linkcheck/output.txt
````

#### Create all project docs:
````bash
cd src/ansible_collections/solace/pubsub_plus/docs
./make.sh
````

---
The End.
