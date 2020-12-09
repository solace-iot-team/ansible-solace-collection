# Development

Setup the development environment.

## MacOS

### Install Python Version(s)

````bash
# upgrade to latest pip3
python3 -m pip install --upgrade pip

brew install pyenv

pip3 install virtualenv

pyenv install 3.6.12
# bin: ~/.pyenv/versions/3.6.12/bin/python3

````

### Install & Activate Python Virtual Env

````bash
mkdir ./venvs
cd venvs
# create virtual env
virtualenv -p ~/.pyenv/versions/3.6.12/bin/python3 venv3.6.12
# activate virtual env
source venv3.6.12/bin/activate
# check
(venv3.6.12) ...$ python3 -V

````

### Install Ansible Components in Python Virtual Env
````bash
(venv3.6.12) ...$ python3 -m pip install --upgrade pip
(venv3.6.12) ...$ pip install ansible
(venv3.6.12) ...$ pip install docker-compose

# check
(venv3.6.12) ...$ ansible --version
````

### Install Solace Collection Requirements in Python Virtual Env
````bash

pip install -r {root}/requirements.txt

````

### Activate Ansible-Solace Devel Env
````
(venv3.6.12) ...$ source {root}/devel/bin/asc-devel-activate
(asc-devel)(venv3.6.12) ...$ asc-devel-show

output:
env vars & links
````

### Deactivate Ansible-Solace Devel Env
````
(asc-devel)(venv3.6.12) ...$ asc-devel-deactivate
(venv3.6.12) ...$
````

### Deactivate Python Virtual Env
````
(venv3.6.12) ...$ deactivate
...$
````

---
The End.
