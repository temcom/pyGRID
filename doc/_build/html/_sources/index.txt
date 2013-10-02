pyGRID
******

.. module:: pyGRID

**pyGRID** is a collection of Python utilities to help interface with *Sun Grid Engine*.

*pyGRID* is based on `PySGE <https://github.com/jiahao/PySGE>`_. It allows the user
to define to submit jobs to a queue manager from a Python script or an externally defined
file.

*pyGRID* tries to conform to the *qsub* options syntax as much as possbile, making the
transition easy. It extends the features of *qsub* to provide features like:

* Job options inheritance
* Simplified workflow for the submission of jobs that explore a parameter space
* Easy detection and resubmission of crashed jobs
* Easy definition of dependencies between jobs, useful for automatic data analysis after jobs execution

User Guide
==========

.. toctree::
   :maxdepth: 3

   installation
   tutorial