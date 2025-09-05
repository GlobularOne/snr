Installing Snr
==============

Snr can be installed on almost any Linux distribution. Snr supports python version 3.12 and above.

.. warning::
    Do not install Snr from a terminal on any Snap package (e.g Visual Studio Code from Snap.)
    Snap messes with XDG Basedir environment variables that messes up your instance so only it can be used from inside of a Snap application.

Stable Installation
-------------------

You can use our installation script:

.. code-block:: shell

    curl -sSL https://raw.githubusercontent.com/GlobularOne/snr/main/tools/get_stable.sh | bash

The above will install snr's dependencies, snr itself and will initialize it.

Installation (Beta)
-------------------

You can use our installation script for beta releases as well:

.. code-block:: shell

    curl -sSL https://raw.githubusercontent.com/GlobularOne/snr/main/tools/get_beta.sh | bash

The above will install snr's dependencies, snr itself and will initialize it.

Installation (From Source Code)
-------------------------------

If you want to contribute, you can use the development version from source code.

Clone the repository:

.. code-block:: shell

    git clone https://github.com/GlobularOne/snr.git

Snr uses poetry for packaging and dependency management, if you don't have it installed. Do so:

.. code-block:: shell

    curl -sSL https://install.python-poetry.org | python3 -


Install with Docker (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We recommend installing from source code with docker.
Snr bind mounts `/sys`, `/dev` and `/proc`, and if something goes wrong during the payload generation process, 
it may cause system instability that would be only fixable with restarting. 
Restarting your docker instance is easier than your device.

Build the docker image using:

.. code-block:: shell

    poetry run docker-build

You can now run the image using:

.. code-block:: shell

    poetry run docker-run

You could also use docker compose:

.. code-block:: shell

    docker compose run --rm globularone/snr

If you want to contribute, it might be a good idea to install the `dev` and `docs` group inside the generated docker image (from inside the docker):

.. code-block:: shell

    POETRY_VIRTUALENVS_CREATE=false poetry install --with=dev,docs

Install without Docker
^^^^^^^^^^^^^^^^^^^^^^

You need to install some packages for building snr:

* curl
* git
* make
* clang
* lld
* nasm

Snr also has some non-python runtime dependencies you need to install as well:

* fakeroot
* fakechroot
* debootstrap

Build the payloads:

.. code-block:: shell

    ./tools/build_payloads.sh

After having these installed. Install python dependencies:

.. code-block:: shell

    poetry install


**If you are getting an error about failure to open keyring, it's a bug in pip, please read the FAQ for a workaround.**

Initialize the snr project:

.. code-block:: shell

    poetry run snr --init


Now you can run it using:

.. code-block:: shell

    poetry run snr

Or you can activate the virtual environment with `poetry shell` and just use `snr`.

.. seealso::

    :doc:`quickstart`
