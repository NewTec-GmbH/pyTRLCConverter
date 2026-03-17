.. template_python documentation master file.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
   This file is written in ``reStructuredText`` syntax. Dor documentation see:
   `reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_

   ATTENTION!! If you want to edit "User Editable" sections, change `update_doc_from_src.py`
   otherwise they will be overwritten by intputs from the project during sphinx generation
 
.. figure:: _static/NewTec_Logo_Slogan.png
   :align: right
   :figwidth: 400px

.. <User editable section introduction>
.. role:: raw-html-m2r(raw)
   :format: html


pyTRLCConverter :raw-html-m2r:`<!-- omit in toc -->`
========================================================

Overview
--------


.. image:: https://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/NewTec-GmbH/pyTRLCConverter/refs/heads/main/doc/architecture/context_diagram.puml
   :target: https://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/NewTec-GmbH/pyTRLCConverter/refs/heads/main/doc/architecture/context_diagram.puml
   :alt: context


Find the requirements, test cases, coverage and etc. deployed on `github pages <https://newtec-gmbh.github.io/pyTRLCConverter>`_.

Usage
-----
.. </User editable section introduction>
.. figure:: _static/Gitterkugel_grau.png
   :align: right
   :figwidth: 300px
.. <User editable section architecture>

Software Architecture
---------------------
.. toctree::
   :maxdepth: 2

   _sw-architecture/README.md
.. </User editable section architecture>

.. <User editable section source>

Software Detailed Design
------------------------
.. autosummary::
   :toctree: _autosummary
   :template: custom-module-template.rst
   :recursive:

   abstract_converter
   base_converter
   docx_converter
   dump_converter
   item_walker
   logger
   markdown_converter
   docx_renderer
   rst_renderer
   plantuml
   render_config
   ret
   rst_converter
   translator
   trlc_helper
   __main__
.. </User editable section source> 

Testing
-------
.. <User editable section unittest>

Software Detailed Design
------------------------
.. autosummary::
   :toctree: _autosummary
   :template: custom-module-template.rst
   :recursive:

   test_cli
   test_docx
   test_dump
   test_general
   test_markdown
   test_plantuml
   test_render_cfg
   test_rst
   psc_do_nothing
   psc_simple

.. </User editable section unittest> 

PyLint
^^^^^^
.. toctree::
   :maxdepth: 2
   
   pylint.rst

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

License information
-------------------
.. toctree::
   :maxdepth: 2

   license_include
