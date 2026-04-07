.. figure:: ../../../doc/images/NewTec_Logo_Slogan.png
   :align: right
   :figwidth: 350px
 
.. container:: clearboth
  
  .. image alignment: Comment needed for clearboth container to work, otherwise the image overlaps with the text 

SW-Detailed Design
------------------

This section provides a developer-focused view of the internal design of
``pyTRLCConverter``. All API pages are generated automatically from the source
code and docstrings by `sphinx-autoapi <https://sphinx-autoapi.readthedocs.io>`_.

The implementation follows a pipeline-oriented structure:

1. Input files and CLI options are collected and validated.
2. TRLC model elements are traversed and normalised.
3. A selected converter renders project-specific output.
4. Optional translation and tracing information is applied.

API Reference
^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 3

   api/pyTRLCConverter/index
