pyGRID
======

Python suite to manage jobs on a Sun Grid Engine computing cluster. Based on [pySGE](https://github.com/jiahao/PySGE), it adds the ability to span a parameter space.

Create Package
---------------------

pyGRID uses setuptoos to create an installer to be distributed. Type
```
python setup.py sdist
```
in the repository directory in order to create a package. You can grab the archived file produced by setuptools in the `dist` subdirectory of the repository to distribute pyGRID.

Installation
---------------

If you don't have root privileges on the cluster and you want to install pyGRID in your home directory follow these steps first:
* Create the path `~/lib/python2.6/site-packages` (assuming you installed python version 2.6) in your home directory.
* Create the `~/bin` path.
* Add `export PYTHONPATH=~/lib/python2.6/site-packages:$PYTHONPATH` and `export PATH=~/bin:$PATH` to your `.bashrc` file (and run `. ~/.bashrc`).

Transfer the pyGRID archive file on the cluster and from a terminal run
```
$ tar -xzvf pyGRID-0.1.2.tar.gz
$ cd pyGRID-0.1.2
$ python setup.py develop --prefix=~
```
where `0.1.2` is the current version number of pyGRID.

From now on you can run pyGRID by simply typing `pyGRID` from anywhere in the cluster.

Usage
-----

pyGRID accepts the path of an xml file as input and the name of simulation defined within it as a `sim_element` xml tag. The `sim_element` xml tag specifies the options of the job you want to run and is used by pyGRID to 
* write a bash file to pass to qsub for running the job
* pass options to qsub, included the values of parameters as environment variables
* create an auxilliary xml file, with extentsion `.grid`, holding the properties of a submitted job
* detect crashed jobs and resubmit them

The syntax for the xml file used by pyGRID is documented in the `pyGRID/examples/basicExample.xml` file in the repository but in short pyGRID conforms to the syntax used by `qsub` to specify job options.

Tests
-----

I have created some tests for pyGRID in order to ensure that basic functions are not broken during development but they are by no mean exhaustive.

In particular tests have to be written for:
* Submission of jobs. At the moment the tests only check that the arguments defined in the xml file are parsed correctly and are represented in the pyGRID object.
* Detection and resubmission of crashed jobs.

Both these tasks require some sort of system in place to emulate `qsub` and its responses.

TODO
----

* Extend the syntax to define the values of the parameters to include the ability to specify the increment not only the number of steps.
