
# Safety Manual <!-- omit in toc -->

- [Introduction](#1-introduction)
  - [Purpose of this Document](#11-purpose-of-this-document)
  - [Product Identification](#12-product-identification)
  - [Product Goals and Usage](#13-product-goals-and-usage)
  - [Tool Usage according to ISO 26262](#14-tool-usage-according-to-iso-26262)
  - [Classification Hints](#15-classification-hints)
    - [Use Cases of the tool pyTRLCConverter](#151-Use-Cases-of-the-tool-pyTRLCConverter)
    - [Tool Impact TI of potential violations](#152-Tool-Impact-TI-of-potential-violations)
    - [Tool error detection](#153-Tool-error-detection)
    - [Tool Confidence Level TCL](#154-Tool-Confidence-Level-TCL) 
  - [Qualification Hints](#16-qualification-hints)
  - [Validation of the Software Tool](#17-validation-of-the-software-tool)
- [Example Use Cases](#2-example-use-cases)
  - [Conversion TRLC files to Markdown format UC1](#21-Conversion-TRLC-files-to-Markdown-format-UC1)
  - [Conversion TRLC files to docx format using a stored userdefined document template UC2](#22-Conversion-TRLC-files-to-docx-format-using-a-stored-userdefined-document-template-UC2)
  - [Conversion TRLC files to reStructuredText format UC3](#23-Conversion-TRLC-files-to-reStructuredText-format-UC3)
  - [Dump TRLC item list to console UC4](#24-Dump-TRLC-item-list-to-console-UC4)
  - [Apply attribute name translation UC5](#25-Apply-attribute-name-translation-UC5)
- [Summary](#3-summary)
  - [Summary for using the pyTRLCConverter python tool for non-safety-relevant Requirements](31-Summary-for-using-the-pyTRLCConverter-python-tool-for-non-safety-relevant-Requirements)
  - [Summary for using the pyTRLCConverter python tool for safety-relevant Requirements](32-Summary-for-using-the-pyTRLCConverter-python-tool-for-safety-relevant-Requirements)
  
## 1 Introduction

### 1.1 Purpose of this Document

This document summarizes the qualification requirements on the ***pyTRLCConverter*** software tool according to the methodology described in ISO 26262-8:2018. Use cases relevant for the development of safety related systems are analyzed. 
For each use case, a classification of the Tool Confidence Level (TCL) is made with recommendations for the qualification methods to be used. 
Wherever relevant, requirements and assumptions regarding the context in which the tools are used that have an impact on the TCL are stated.  
This document may also serve as a Safety Manual, since hints for the qualification procedures are given.

### 1.2 Product Identification

The tool classification examples and all statements within this document apply to the latest released version of the ***pyTRLCConverter*** software tool. The ***pyTRLCConverter*** is a tool to convert TRLC files to specific formats.

### 1.3 Product Goals and Usage

The ***pyTRLCConverter*** is a command-line tool to convert TRLC (Treat Requirements Like Code) files to different output formats. 
Since the definition of TRLC types is project-specific, the built-in converters can be extended in an object-oriented manner.

Currently out of the box supported formats:
- Markdown
- docx
- reStructuredText
- dump
Find the requirements, design, test cases, coverage and etc. on the github pages https://github.com/NewTec-GmbH/pyTRLCConverter. 

### 1.4 Tool Usage according to ISO 26262

In accordance with ISO 26262-8:2018, any tool can be used in the development of safety-related ECUs. 
The tool user needs to ensure that, based on his use case, a tool classification was conducted, and that a qualification of the tool has been executed on the basis of this classification.

Tool classification and qualification must be carried out by the user of the tool, who knows his use case in detail. 
Example use cases and their corresponding hints for classification and qualification are provided in the following of this document.

### 1.5 Classification Hints

### 1.5.1 Use Cases of the tool pyTRLCConverter
For every planned use case of the tool, the tool confidence level TCL needs to be assessed according to ISO ISO 26262-8:2018 table 3.
The TCL result depends on the use cases to convert TRLC (Treat Requirements Like Code) files to different output formats.
- UC1) Conversion TRLC files to Markdown format
- UC2) Conversion TRLC files to docx format using a stored userdefined document template.
- UC3) Conversion TRLC  files to reStructuredText format
- UC4) Dump TRLC item list to console
- UC5) Apply attribute name translation 

### 1.5.2 Tool Impact TI of potential violations
The primary purpose of classification is to identify the extent to which errors resulting from the ***pyTRLCConverter*** tool can cause violations of a safety goal. 
In the case of the ***pyTRLCConverter*** tool and in a typical use case, errors may take one of the general forms during executing the tool converting process
- a) requirements or parts of it are lost
- b) requirements or parts of it are corrupted 
- c) arguments of the requirements are lost or corrupted 
- d) implementation reference to another requirement is corrupted
- e) with the possibliity to convert reuqirements to a format with using a project specific conversion files (.json and .py files). The requirment content may be deleted or corrupted.
- f) using a corrupted docx ducument template to export to the format docx, requirements or parts of it are lost or corrupted. 

It is considered likely that an error in the ***pyTRLCConverter*** tool could cause an undetected error in the requirements with an high Impact on safety or safety goal. So the Tool Impact can be considered as **TI2**. 

### 1.5.3 Tool error detection 
For all these potential violations a, b, c and d it is not possible for the user of the tool to detect these errors upon reviewing of the converted requirement because the review process of writing requirements is already finished. 
It would be necessary for the user of the software tool ***pyTRLCConverter*** to review the converted requirement document against the origin TRLC requirements. 
For all these potential violations e and f it would be necessary to  detect errors to review the project specific confersion .JSON and .py files and to review the project specific document templates (docx template).
The user has only low possibility to dected a tool error so the Tool Error Detetion is very low **TD3**.

### 1.5.4 Tool Confidence Level TCL
The tool error detection is very low (Tool error detection = TD3) and all these errors may result in a violation of a safety goal.
Therefore, ***pyTRLCConverter*** may be classified with a Tool error detection **TD3** and Tool Impact **TI3** results into a Tool confidence level **TCL3** (according to ISO 26262-8:2018 table 3)  
A confidence level of **TCL3** require tool qualification measures (typical of safety-relevant systems) defined in ISO 26262-8:2018  table 4 — Qualification of software tools classified TCL3.

### 1.6 Qualification Hints

Each main release of ***pyTRLCConverter*** needs to be qualified individually, covering all planned use cases classified TCL3. 
Qualification methods for each use case need to be chosen according to the ASIL of the product under development.
- 1a: Increased confidence from use  
- 1b: Evaluation of the tool development process 
- 1c: Validation of the software tool
- 1d: Development in accordance with a safety standard

For the qualification of ***pyTRLCConverter***, only the qualification methods 1c: Validation of the software tool or 1d: Development in accordance with a safety standard mentioned in ISO 26262-8:2018 can be considered. 
- The qualification method **1a** (increased confidence from use) cannot be considered, since the ***pyTRLCConverter*** tool has limited use in existing development projects. This method is not sufficient for ASILC and ASILD functions.
- The qualification method **1b** (Evaluation of the tool development process). This method is not sufficient for ASILC and ASILD functions. 
- the qualification method **1c** (validation of the software tool). Highly recommended for ASILC and ASILD functions. 
- The qualification method **1d** (development in accordance with a safety standard)Highly recommended for ASILC and ASILD functions. But this cannot be considered, since ***pyTRLCConverter*** was not developed in accordance with any safety standard.

To be able to use the tool in all ASIL use cases NewTec GmbH recommends the qualification method **1c validation of the software tool** for the ***pyTRLCConverter*** software tool according to ISO 26262-8:2018 11.4.9.

### 1.7 Validation of the Software Tool

The qualification method "validation of the software tool" requires that the developer provide evidence that the software tool fulfills the tool requirements as they relate to its purpose in the development context. 
This is accomplished by testing the tool against the relevant requirements. The ***pyTRLCConverter*** GitHub repository includes example test scripts which may be used or adapted for this 
qualification method. 
The ***pyTRLCConverter*** tool was developed according to the NewTec standard for Python development. 
This standard includes documentation of tool requirements and design, coding guidelines, full trace and test coverage, and the PEP 8 style guide. 

It is good practice to use a test configuration with known input data and check the corresponding output of the tool for correctness e.g. by a formal review. 
The test configuration and test data should be determined based on the planned use case. 
Where a newer version of the software is being qualified, it may be qualified in an automated way against the output of an older, previously qualified version of the software. 
Another good practice is to stimulate an error and check whether the tool can detect it as expected.

The validation of the software tool shall meet the following criteria: 
- the validation measures shall demonstrate that the software tool complies with its specified requirements 
- the malfunctions and their corresponding erroneous outputs of the software tool occurring during validation shall be analysed together with information on their possible consequences and with measures to avoid or detect them, and
- the reaction of the software tool to anomalous operating conditions shall be examined. 


## 2 Example Use Cases
The Use Cases defined in [Use Cases of the tool pyTRLCConverter](#151-Use-Cases-of-the-tool-pyTRLCConverter) are analyzed in the following to get a recommended method of qualification.  
The following tables are an example of use cases where the ***pyTRLCConverter*** tool is used for safety-relevant requirements: 


### 2.1 Conversion TRLC files to Markdown format UC1
|||
|---|---|
|**Intended Purpose**|Convert a ***TRLC file to Markdown format***. The tool requires two kinds of TRLC input sources for the conversion. These are the requirements (*.trlc) files and the model (*.tls) files. It will create a Markdown file with the same name as the requirements file (*.trlc) in the current directory, but with the Markdown extension (.md).|
|**Environmental, Functional and Process Constraints**|Operating system: Windows 10 (version 20H2, 64bit)<br>***pyTRLCConverter*** GPL-3.0.<br>|
|**Description**|Run the ***pyTRLCConverter*** python tool, using the paths of the input requirements (*.trlc) files and the model (*.tls) files.|
|**Output**| Requirement document in  Markdown format including the converted safety-relevant source requirements.|
|**Tool Impact**|**TI2 (Possibility of impact on a safety requirement)**<br>Rationale:<br><ul><li>Since the requirement which are converted to a markdown file are safety-relevant, it is possible that ***pyTRLCConverter*** may delete or corrupt requirements or part of them and thereby lead to the violation of a safety goal.</li></ul>|
|**Tool Error Detection**|**TD3 (low degree of confidence of prevention or detection)**<br>Rationale:<br><ul><li>It is not possible to detect a deleted or corrupt requirement, since the review process for the requirement is already finished.</li></ul>|
|**Tool Confidence Level**|**TCL3**|
|**Recommended Method of Qualification**|Validation of the software tool|

### 2.2 Conversion TRLC files to docx format using a stored userdefined document template UC2
|||
|---|---|
|**Intended Purpose**|Convert a ***TRLC file to docx format*** using a stored userdefined document template. The tool requires two kinds of TRLC input sources for the conversion. These are the requirements (*.trlc) files and the model (*.tls) files.  Also a document template .docx musst be stored for the conversion process. The tool will create requirement output docx file with the same name as the requirements file (*.trlc) in the current directory, but with the docx extension (.docx).|
|**Environmental, Functional and Process Constraints**|Operating system: Windows 10 (version 20H2, 64bit)<br>***pyTRLCConverter*** GPL-3.0. <br>|
|**Description**|Run the ***pyTRLCConverter*** python tool, using the paths of the input requirements (*.trlc) files and the model (*.tls) files. Also store a docx template.|
|**Output**| Requirement document in the docx format based on the document template including the converted safety-relevant source requirements.|
|**Tool Impact**|**TI2 (Possibility of impact on a safety requirement)**<br>Rationale:<br><ul><li>Since the requirement which are converted to a docx file are safety-relevant, it is possible that ***pyTRLCConverter*** may delete or corrupt requirements or part of them and thereby lead to the violation of a safety goal.</li></ul>|
|**Tool Error Detection**|**TD3 (low degree of confidence of prevention or detection)**<br>Rationale:<br><ul><li>It is not possible to detect a deleted or corrupt requirement, since the review process for the requirements is already finished. But its recomented to review the document template .docx du avoid corrupted document output files.</li></ul>|
|**Tool Confidence Level**|**TCL3**|
|**Recommended Method of Qualification**|Validation of the software tool|

### 2.3 Conversion TRLC files to reStructuredText format UC3
|||
|---|---|
|**Intended Purpose**|Convert a ***TRLC file to to reStructuredText*** format. The tool requires two kinds of TRLC input sources for the conversion. These are the requirements (*.trlc) files and the model (*.tls) files. It will create a reStructuredText file with the same name as the requirements file (*.rst) in the current directory, but with the reStructuredText extension (.rst).|
|**Environmental, Functional and Process Constraints**|Operating system: Windows 10 (version 20H2, 64bit)<br>***pyTRLCConverter*** GPL-3.0.<br>|
|**Description**|Run the ***pyTRLCConverter*** python tool, using the paths of the input requirements (*.trlc) files and the model (*.tls) files.|
|**Output**| Requirement document in the reStructuredText format including the converted safety-relevant source requirements.|
|**Tool Impact**|**TI2 (Possibility of impact on a safety requirement)**<br>Rationale:<br><ul><li>Since the requirement which are converted to a reStructuredText file are safety-relevant, it is possible that ***pyTRLCConverter*** may delete or corrupt requirements or part of them and thereby lead to the violation of a safety goal.</li></ul>|
|**Tool Error Detection**|**TD3 (low degree of confidence of prevention or detection)**<br>Rationale:<br><ul><li>It is not possible to detect a deleted or corrupt requirement, since the review process for the requirement is already finished.</li></ul>|
|**Tool Confidence Level**|**TCL3**|
|**Recommended Method of Qualification**|Validation of the software tool|

### 2.4 Dump TRLC item list to console UC4
|||
|---|---|
|**Intended Purpose**| ***Dump TRLC item list to console*** output. The tool dumpts the complete TRLC item lists to the console. The tool requires two kinds of TRLC input sources for the conversion. These are the requirements (*.trlc) files and the model (*.tls) files. It will dump all requirments directly into console output.|
|**Environmental, Functional and Process Constraints**|Operating system: Windows 10 (version 20H2, 64bit)<br>***pyTRLCConverter*** GPL-3.0.<br>|
|**Description**|Run the ***pyTRLCConverter*** python tool, using the paths of the input requirements (*.trlc) files and the model (*.tls) files.|
|**Output**| The converted safety-relevant source requirements dumpted into output console.|
|**Tool Impact**|**TI2 (Possibility of impact on a safety requirement)**<br>Rationale:<br><ul><li>Since the requirement which are dumped into console output are safety-relevant, it is possible that ***pyTRLCConverter*** may delete or corrupt requirements or part of them and thereby lead to the violation of a safety goal.</li></ul>|
|**Tool Error Detection**|**TD3 (low degree of confidence of prevention or detection)**<br>Rationale:<br><ul><li>It is not possible to detect a deleted or corrupt requirement, since the review process for the requirement is already finished.</li></ul>|
|**Tool Confidence Level**|**TCL3**|
|**Recommended Method of Qualification**|Validation of the software tool|

### 2.5 Apply attribute name translation UC5
|||
|---|---|
|**Intended Purpose**| ***Apply attribute name translation*** . The tool uses a user defined project specified translation JSON file to make the requirements better readable. The tool requires a translation JSON file to translate the attribute names.|
|**Environmental, Functional and Process Constraints**|Operating system: Windows 10 (version 20H2, 64bit)<br>***pyTRLCConverter*** GPL-3.0.<br>|
|**Description**|Run the ***pyTRLCConverter*** python tool, using the translation JSON file. Use the --translation argument to specify the translation file.|
|**Output**| Requirement document includs the attribute better readably attribute names with the safety-relevant source requirements.|
|**Tool Impact**|**TI2 (Possibility of impact on a safety requirement)**<br>Rationale:<br><ul><li>Since the requirement which are converted into a better readble text, it is possible that ***pyTRLCConverter*** may delete or corrupt requirements or part of them and thereby lead to the violation of a safety goal.</li></ul>|
|**Tool Error Detection**|**TD3 (low degree of confidence of prevention or detection)**<br>Rationale:<br><ul><li>It is not possible to detect a deleted or corrupt requirement, since the review process for the requirement is already finished.</li></ul>|
|**Tool Confidence Level**|**TCL3**|
|**Recommended Method of Qualification**|Validation of the software tool|

## 3 Summary

The user of the software tool may used the valdidated tool within its requirments, design, implementation and test cases to get the validated software tool: ***pyTRLCConverter***. 
Butif there are any tool changes or adaptions during deveopment in code the the all process relevant documents must be adapted and test cases may be reworked and reexecuted. 
The user must determine the appropriate tool classification for their own use case and the appropriate qualification method. The use case upon are only examples.

### 3.1 Summary for using the pyTRLCConverter python tool for non-safety-relevant Requirements

If the ***pyTRLCConverter*** tool is used solely for conversion of non-safety-relevant requirements, the tool can be classified with a confidence level of **TCL1** and requires no qualification for use.

### 3.2 Summary for using the pyTRLCConverter python tool for safety-relevant Requirements

If the ***pyTRLCConverter*** tool is used for conversion of safety-relevant requirements, the user of the software tool must determine the increased tool confidence level (suggested tcl3) and perform qualification via validation of the software tool.