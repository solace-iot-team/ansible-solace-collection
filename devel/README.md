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
### Upgrade pip
````bash
(venv3.6.12) ...$ python3 -m pip install --upgrade pip
````
### Install Devel Requirements in Python Virtual Env
````bash
(venv3.6.12) ...$ cd devel
(venv3.6.12) ...$ pip install -r devel.requirements.txt
(venv3.6.12) ...$ pip install -r ../requirements.txt
# check
(venv3.6.12) ...$ ansible --version
````

### Activate Ansible-Solace Collection Devel Env
````bash
(venv3.6.12) ...$ source {root}/devel/bin/asc-devel-activate
(asc-devel)(venv3.6.12) ...$ asc-devel-show

output:
env vars & links
````

### Deactivate Ansible-Solace Collection Devel Env
````bash
(asc-devel)(venv3.6.12) ...$ asc-devel-deactivate
(venv3.6.12) ...$
````

### Deactivate Python Virtual Env
````bash
(venv3.6.12) ...$ deactivate
...$
````


---
The End.
