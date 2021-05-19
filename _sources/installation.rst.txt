Installation
============

.. important::
  Supported ansible versions: 'ansible>=2.10.3,<2.11'

Installation & Dependencies
---------------------------

Prerequisites
+++++++++++++

  - install python >=3.8

Python dependencies:
:download:`requirements <../../requirements.txt>`:

.. literalinclude:: ../../requirements.txt


Install dependencies:

.. code-block:: bash

  # upgrade to latest pip3
  $ python3 -m pip install --upgrade pip
  $ pip install -r requirements.txt
  $ pip install ansible

Install the Solace PubSub+ Ansible Collection
+++++++++++++++++++++++++++++++++++++++++++++

.. code-block:: bash

  $ ansible-galaxy collection install solace.pubsub_plus

.. note::

   ``ansible-galaxy`` command will not overwrite the existing collection if it
   is already installed. We can change this default behavior by adding a
   ``--force`` command line switch::

      $ ansible-galaxy collection install --force solace.pubsub_plus

The official Ansible documentation contains more information about the
installation options in the `Using collections`_ document.

.. _Using collections:
   https://docs.ansible.com/ansible/latest/user_guide/collections_using.html#installing-collections

Set the Python interpreter
++++++++++++++++++++++++++

.. note::

  Ansible-Solace only works with Python version >=3.6. Most systems come with a Python version 2.x pre-installed in `/usr/bin/python`.

  By setting the environment variable `ANSIBLE_PYTHON_INTERPRETER="path-to-python3"` we can tell Ansible which Python interpreter to use.

.. code-block:: bash

  # manually
  $ export ANSIBLE_PYTHON_INTERPRETER={path-to-your-python-3-bin}
  # dynamically
  $ export ANSIBLE_PYTHON_INTERPRETER=$(python3 -c "import sys; print(sys.executable)")

**Ansible Playbook Error when using Python 2.x:**

.. code-block::

  fatal: [local_broker]: FAILED! => {
      "msg": "Unable to import ('ansible_collections', 'solace', 'pubsub_plus', 'plugins', 'module_utils', 'solace_api') due to invalid syntax"
  }

Solution: set the `ANSIBLE_PYTHON_INTERPRETER={path-to-your-python-3-bin}`

Example Installation: MacOs
---------------------------

Sequence:
  - Homebrew
  - Python - choose between **Native** or a **Virtual Environment**
  - Ansible
  - Collection
  - Docker Desktop

.. code-block:: bash

  # Homebrew
  # https://brew.sh/
  $ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
  # check if it was installed correctly
  $ brew help

  # Python
  $ brew install python
  $ brew info python
  $ brew update && brew upgrade python
  $ python3 -V

  # upgrade pip
  $ python3 -m pip install --upgrade pip
  $ pip3 -V

.. content-tabs::

  .. tab-container:: native
    :title: Native

    .. code-block:: bash

      # ansible
      $ pip3 install ansible
      # check install
      $ ansible --version
      $ ansible-playbook --version
      # check install info
      $ pip3 show ansible

      # collection dependencies & collection
      $ pip3 install -r requirements.txt
      $ ansible-galaxy collection install solace.pubsub_plus
      # check install path
      $ ansible-galaxy collection list

  .. tab-container:: virtualenv
      :title: Virtual Env

      .. code-block:: bash

        $ brew install pyenv
        # download a Python version
        $ pyenv install 3.8.6 # or another version
        # bin: ~/.pyenv/versions/3.6.12/bin/python3
        $ pip3 install virtualenv

        # install the virtual env
        $ mkdir my-project
        $ cd my-project
        $ mkdir venvs
        $ cd venvs

        # create virtual env
        $ virtualenv -p ~/.pyenv/versions/3.8.6/bin/python3 venv3.8.6
        # activate virtual env
        source venv3.8.6/bin/activate
        # check
        (venv3.8.6) ...$ python -V
        # upgrade pip
        (venv3.8.6) ...$ python -m pip install --upgrade pip

        # ansible
        $ pip install ansible
        # check install
        $ ansible --version
        $ ansible-playbook --version
        # check install info
        $ pip show ansible

        # collection dependencies & collection
        $ pip install -r requirements.txt
        $ ansible-galaxy collection install solace.pubsub_plus -p venv3.8.6/lib/python3.8/site-packages/ansible_collections/
        # [WARNING]: The specified collections path '{root}/my-project/venvs/venv3.8.6/lib/python3.8/site-packages/ansible_collections' is not part ...
        # add install path to ANSIBLE_COLLECTIONS_PATH
        export ANSIBLE_COLLECTIONS_PATH={root}/my-project/venvs/venv3.8.6/lib/python3.8/site-packages/ansible_collections
        # check install path
        $ ansible-galaxy collection list


.. important::

    Don't forget to set ANSIBLE_PYTHON_INTERPRETER={path-to-your-python-3-bin}



`Install Docker Desktop`_ if you want to use Solace Broker Services locally.

.. _Install Docker Desktop:
  https://www.docker.com/products/docker-desktop


Example Installation: Ubuntu
----------------------------

**Python 3**

.. code-block:: bash

  $ sudo apt update
  $ sudo apt -y upgrade
  $ sudo apt update

  $ sudo apt install python3
  $ python3 -V

  $ sudo apt install python3-pip
  $ sudo python -m pip install --upgrade pip
  $ pip -V

**Ansible & Solace Collection**

.. code-block:: bash

  $ sudo pip install ansible
  $ pip show ansible
  $ ansible --version

  # collection dependencies & collection
  $ sudo pip install -r requirements.txt
  $ ansible-galaxy collection install solace.pubsub_plus
  # check install path
  $ ansible-galaxy collection list


Example Installation: Centos7
-----------------------------

**Python 3**

.. code-block:: bash

  $ sudo yum install python3
  $ sudo yum install libselinux-python3

  $ sudo python -m pip install --upgrade pip
  $ pip -V

**Ansible & Solace Collection**

.. code-block:: bash

  $ sudo pip install ansible
  $ pip show ansible
  $ ansible --version

  # collection dependencies & collection
  $ sudo pip install -r requirements.txt
  $ ansible-galaxy collection install solace.pubsub_plus
  # check install path
  $ ansible-galaxy collection list
