# Package Description

RobotFramework DoIP is a Robot Framework library specifically designed for interacting with Electronic Control Units (ECUs) using the Diagnostics over Internet Protocol (DoIP).

At its core, DoIP serves as a communication bridge between external diagnostic tools and a vehicle's ECUs. This library, RobotFrameworkDoIP, 
provides a set of keywords that enable users to perform diagnostic operations and engage with ECUs, facilitating automated testing processes and interaction with vehicles through the DoIP protocol.


## How to install
1.  Installation via GitHub (recommended for developers)

    -   Clone the **RobotFramework-DoIP** repository to your machine.

        ``` 
        git clone https://github.com/test-fullautomation/robotframework-doip.git
        ```

        [RobotFramework-DoIP in
        GitHub](https://github.com/test-fullautomation/robotframework-doip)

    -   Install dependencies

        **RobotFramework-DoIP** requires some additional Python libraries.
        Before you install the cloned repository sources you have to
        install the dependencies manually. The names of all related
        packages you can find in the file `requirements.txt` in the
        repository root folder. Use pip to install them:

        ``` 
        pip install -r ./requirements.txt
        ```

        Additionally install **LaTeX** (recommended: TeX Live). This is
        used to render the documentation.

    -   Configure dependencies

        The installation of **RobotFramework-DoIP** includes to generate
        the documentation in PDF format. This is done by an application
        called **GenPackageDoc**, that is part of the installation
        dependencies (see `requirements.txt`).

        **GenPackageDoc** uses **LaTeX** to generate the documentation
        in PDF format. Therefore **GenPackageDoc** needs to know where
        to find **LaTeX**. This is defined in the **GenPackageDoc**
        configuration file

        ``` 
        packagedoc\packagedoc_config.json
        ```

        Before you start the installation you have to introduce the
        following environment variable, that is used in
        `packagedoc_config.json`:

        -   `GENDOC_LATEXPATH` : path to `pdflatex` executable

    -   Use the following command to install **RobotFramework-DoIP**:

        ``` 
        setup.py install
        ```

## Package Documentation

A detailed documentation of the **RobotFramework_DoIP** can be found
here:
[RobotFramework_DoIP.pdf](https://github.com/test-fullautomation/robotframework-doip/blob/develop/RobotFramework_DoIP/RobotFramework_DoIP.pdf)

## Feedback

To give us a feedback, you can send an email to [Thomas
Pollerspöck](mailto:Thomas.Pollerspoeck@de.bosch.com) or
[RBVH-ECM-Automation_Test_Framework-Associates](mailto:RBVH-ENG2-CMD-Associates@bcn.bosch.com)

## About

### Maintainers

[Thomas Pollerspöck](mailto:Thomas.Pollerspoeck@de.bosch.com)

### Contributors

[Thomas Pollerspöck](mailto:Thomas.Pollerspoeck@de.bosch.com)  
[Hua Van Thong](mailto:thong.huavan@vn.bosch.com)  
[Mai Minh Tri](mailto:tri.maiminh@vn.bosch.com)  


## License

Copyright 2020-2023 Robert Bosch GmbH

Licensed under the Apache License, Version 2.0 (the \"License\"); you
may not use this file except in compliance with the License. You may
obtain a copy of the License at

> <http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an \"AS IS\" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
