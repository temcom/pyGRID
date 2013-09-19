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

The syntax for the xml file used by pyGRID is documented in `pyGRID/examples/basicExample.xml` but in short pyGRID conforms to the syntax used by `qsub` to specify job options.

pyGRID command line options can be divided in three groups:
* XML file option. This option is *Required*.
    * `-f`, specifies the path of the file to load.
* Simulation options. These are mutually *exlusive* and at least one is *Required*.
    * `-s`, specifies the name of the simulation to load from the XML file.
    * `-a`, loads all the simulations in the file.
* Action options. Tell pyGRID which action to perform woth the specified simulation. These are mutually *exclusive*.
    * `-w`, write the shell script for the simulation. 
    * `-b`, write the shell script and submit a job for every combination of the parameters of the simulation
    * `-c`, scan the output sctream of finished jobs and detect the crashed ones. The `JOB_ID` and `TASK_ID` of the crashed job is saved in the `.grid` auxilliary file.    
    * `-r`, resubmit crashed jobs.
    
To invoke the documentation for pyGRID command line option type `pyGRID --help`. 

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
