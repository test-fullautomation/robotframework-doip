.. Copyright 2020-2026 Robert Bosch GmbH

.. Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

.. http://www.apache.org/licenses/LICENSE-2.0

.. Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Package Description
-------------------

**RobotFramework_DoIP** is a Robot Framework library specifically designed for interacting with Electronic Control Units (ECUs) using the Diagnostics over Internet Protocol (DoIP).

At its core, DoIP serves as a communication bridge between external diagnostic tools and a vehicle's ECUs. This library, **RobotFramework_DoIP**, 
provides a set of keywords that enable users to perform diagnostic operations and engage with ECUs, facilitating automated testing processes and interaction with vehicles through the DoIP protocol.

How to install
--------------

The **RobotFramework_DoIP** library can be installed in two different ways.

1. Installation via PyPi (recommended for users)

   .. code::

      pip install robotframework-doip

   `RobotFramework_DoIP in PyPi <https://pypi.org/project/robotframework-doip/>`_

2. Installation via GitHub (recommended for developers)

   * Clone the **robotframework-doip** repository to your machine.

     .. code::

        git clone https://github.com/test-fullautomation/robotframework-doip.git

     `RobotFramework_DoIP in GitHub <https://github.com/test-fullautomation/robotframework-doip>`_

   * Use the following command to install **RobotFramework_DoIP** (executed in repository main folder):

     .. code::

        python -m pip install .

     Or:

     .. code::

        python -m pip install --proxy <proxy> .

     This command will also download and install all dependencies that are required to work with the source files in the current repository.
     After the initial installation of **RobotFramework_DoIP** is done, you have the following two possibilities:

     1. *Clean the previous installation*:

        .. code::

           python "./cleanup_installation.py"

        ``cleanup_installation.py`` explicitly deletes all files and folders within the component installation folder under
        ``site-packages`` and also deletes local build artefacts.

     2. *Render the component documentation*:

        .. code::

           python "./genpackagedoc.py"

        This would e.g. be required in case of changes in the interface of **RobotFramework_DoIP**.

        The documentation is rendered by a separate application called **GenPackageDoc**, that is part
        of the build dependencies and runtime dependencies of **RobotFramework_DoIP**.

        **GenPackageDoc** needs to be configured. Details about how to do this, can be found in the
        `README.rst <https://github.com/test-fullautomation/python-genpackagedoc/blob/develop/README.rst>`_
        (sections *Install dependencies* and *Configure dependencies*).

   * Use the following command to build **RobotFramework_DoIP** (executed in repository main folder):

     .. code::

        python -m build .

     Or:

     .. code::

        python -m pip config set global.proxy <proxy>
        python -m build .



Package Documentation
---------------------

A detailed documentation of the **RobotFramework_DoIP** can be found
here:
`RobotFramework_DoIP.pdf <https://github.com/test-fullautomation/robotframework-doip/blob/develop/RobotFramework_DoIP/RobotFramework_DoIP.pdf>`_

Feedback
--------

To give us a feedback, you can send an email to `Thomas Pollerspöck <mailto:Thomas.Pollerspoeck@de.bosch.com>`_

In case you want to report a bug or request any interesting feature, please don't
hesitate to raise a ticket.

About
-----

Maintainers
------------

`Thomas Pollerspöck <mailto:Thomas.Pollerspoeck@de.bosch.com>`_

Contributors
------------

`Thomas Pollerspöck <mailto:Thomas.Pollerspoeck@de.bosch.com>`_

`Hua Van Thong <mailto:thong.huavan@vn.bosch.com>`_

`Mai Minh Tri <mailto:tri.maiminh@vn.bosch.com>`_

License
-------

Copyright 2020-2026 Robert Bosch GmbH

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
