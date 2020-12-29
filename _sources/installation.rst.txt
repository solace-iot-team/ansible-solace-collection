Installation
============

Installation & Dependencies
---------------------------

Prerequisites:
  - install python >=3.6

Install Python dependencies:
:download:`requirements <../../requirements.txt>`:

.. literalinclude:: ../../requirements.txt


Install:

.. code-block:: bash

  # upgrade to latest pip3
  $ python3 -m pip install --upgrade pip
  $ pip install -r requirements.txt
  $ pip install ansible

Install the Solace PubSub+ Ansible Collection::

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

Set the Python interpreter::

   # manually
  $ export ANSIBLE_PYTHON_INTERPRETER={path-to-your-python-3-bin}
   # dynamically
  $ export ANSIBLE_PYTHON_INTERPRETER=$(python3 -c "import sys; print(sys.executable)")


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
        $ pyenv install 3.6.12 # or another version
        # bin: ~/.pyenv/versions/3.6.12/bin/python3
        $ pip3 install virtualenv

        # install the virtual env
        $ mkdir my-project
        $ cd my-project
        $ mkdir venvs
        $ cd venvs

        # create virtual env
        $ virtualenv -p ~/.pyenv/versions/3.6.12/bin/python3 venv3.6.12
        # activate virtual env
        source venv3.6.12/bin/activate
        # check
        (venv3.6.12) ...$ python -V
        # upgrade pip
        (venv3.6.12) ...$ python -m pip install --upgrade pip

        # ansible
        $ pip install ansible
        # check install
        $ ansible --version
        $ ansible-playbook --version
        # check install info
        $ pip show ansible

        # collection dependencies & collection
        $ pip install -r requirements.txt
        $ ansible-galaxy collection install solace.pubsub_plus -p venv3.6.12/lib/python3.6/site-packages/ansible_collections/
        # [WARNING]: The specified collections path '{root}/my-project/venvs/venv3.6.12/lib/python3.6/site-packages/ansible_collections' is not part ...
        # add install path to ANSIBLE_COLLECTIONS_PATH
        export ANSIBLE_COLLECTIONS_PATH={root}/my-project/venvs/venv3.6.12/lib/python3.6/site-packages/ansible_collections
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

**Ansible & Collection**

.. code-block:: bash

  $ sudo pip install ansible
  $ pip show ansible
  $ ansible --version

  # collection dependencies & collection
  $ sudo pip install -r requirements.txt
  $ ansible-galaxy collection install solace.pubsub_plus
  # check install path
  $ ansible-galaxy collection list
