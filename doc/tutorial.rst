Tutorial
========

Basic Script
------------

In this tutorial we will create a pyGRID script that defines a basic job to submit to the
queue manager. Here is your first pyGRID script, copy its text and save it on a file
called *basicTest.xml*.

.. code-block:: xml

    <?xml version="1.0"?>
    <simulations>
    
        <sim_element N="basicJob">
            <S>/bin/bash</S>
            <j>y</j>
            <cwd />
            <code> echo "Basic Job" </code> 
        </sim_element>
    
    </simulations>

pyGRID uses XML syntax to define jobs that you want to submit to the queue manager. 

The first line, ``<?xml ...>``, specifies the encoding and XML version and it is 
mandatory so copy and paste it on every pyGRID file you make.

The ``<simulations>`` element is also mandatory, and encloses the definition of the job 
we want to submit.

Jobs in pyGRID are defined with the ``<sim_element N="...">`` tag that requires at least
one argument, *N*, containing the name of the job we will submit to the queue manager, in
this case *basicJob* and *anotherJob*. A pyGRID file can contain as many 
job definitions as you wish and each definition will be identified by the name of the job.

Inside the ``<sim_element >`` we define the options of the job we want pyGRID to pass to
the queue manager. At the moment pyGRID supports only clusters running *SUN GRID ENGINE* 
and as such it conforms to the syntax of *qsub*. If you are already familiar with *qsub*
you will be happy to know that you can define all the options accepted by *qsub* inside
``<sim_element >``. You just have to swap the qsub's ::
    
    -OPTION_NAME_1 OPTION_VALUE
    -OPTION_NAME_2
     
notations for pyGRID's ::

    <OPTION_NAME_1> OPTION_VALUE </OPTION_NAME_1>
    <OPTION_NAME_2 />
    
Notice that *qsub* option flags gets translated to self-closing XML tags in pyGRID.

For the script introduced above the 

.. code-block:: xml
    
    <S>/bin/bash</S>
    <j>y</j>
    <cwd />
    
elements are translated by pyGRID to the *qsub* options

::

    -S /bin/bash -j y -cwd
    
If you are not familiar with *qsub* and want to know about its options visit the 
`man page <http://gridscheduler.sourceforge.net/htmlman/htmlman1/qsub.html>`_.

You may have noticed from the script above that pyGRID introduces two differences with 
respect to the *qsub* syntax. You have already encountered the first, the name of the job,
that is defined as an attribute of the ``<sim_element >`` and not as an option inside it.

The second is the code tag

.. code-block:: xml
    
    <code> echo "Basic Job" </code> 

which defines the actions that your job will execute. pyGRID will create a bash script
with the properties of a job and the code it needs to execute to submit to the queue
manager. The content of the code tag will be included verbatim at the end of the bash
script and can contain any valid bash code.
In particular this can be:

* the path of an executable to be run on the cluster
* any bash command to run a python or matlab script on the cluster, e.g. "/usr/local/bin/matlab -nojvm -nodisplay -r matlab_job"
* any amount of bash code to manipulate files, create or delete folders, print environment variables etc.

Inheritance
-----------

Post Processing
---------------