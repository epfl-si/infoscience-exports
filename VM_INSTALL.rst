Setup of a new CentOS 7 VM
==========================

1. Install Docker
-----------------

.. code-block:: bash

    yum install -y yum-utils
    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    yum install -y docker-ce
    systemctl enable docker.service
    systemctl start docker.service

You can check the correct intallation with

.. code-block:: bash

    $ docker --version
    Docker version 17.12.0-ce, build xxx

2. Install docker-compose (requires Python)
-------------------------------------------

.. code-block:: bash

    yum groupinstall -y development
    yum install -y https://centos7.iuscommunity.org/ius-release.rpm
    yum install -y python36u
    yum install -y python36u-pip
    yum install -y python36u-devel

    pip3.6 install docker-compose 

You can check the correct intallation with

.. code-block:: bash

    $ python3.6 --version
    Python 3.6.4
    $ pip3.6 --version
    pip 9.0.1 from /usr/lib/python3.6/site-packages (python 3.6)

    $ docker-compose --version
    docker-compose version 1.19.0, build xxx

3. Install sysadmin account
---------------------------

.. code-block:: bash

    adduser infoscience-exports
    passwd infoscience-exports
    usermod -aG wheel infoscience-exports

    mkdir .ssh
    chmod 700 .ssh/

You can check the correct intallation with

.. code-block:: bash

    $ ls -laG /home/infoscience-exports/
    total 16
    drwx------. 3 infoscience-exports  90 Feb 21 13:15 .
    drwxr-xr-x. 3 root                 32 Feb 21 13:06 ..
    -rw-------. 1 infoscience-exports 519 Feb 21 13:15 .bash_history
    -rw-r--r--. 1 infoscience-exports  18 Sep  6 18:25 .bash_logout
    -rw-r--r--. 1 infoscience-exports 193 Sep  6 18:25 .bash_profile
    -rw-r--r--. 1 infoscience-exports 231 Sep  6 18:25 .bashrc
    drwx------. 2 infoscience-exports  28 Feb 21 13:14 .ssh

4. Do not forget to add you public key
--------------------------------------

.. code-block:: bash

    echo "your key" > .ssh/authorized_keys
    chmod 600 .ssh/authorized_keys

You can check the correct intallation from your host

.. code-block:: bash

    $ ssh infoscience-exports@vm
    not prompting password

5. Checkout code and run
------------------------

.. code-block:: bash

    git clone git@github.com:epfl-idevelop/infoscience-exports.git

and continue the reading with DOCKER_INSTALL.rst
