Tutorial
========

Basics
------

In this tutorial you will create a basic pyGRID script that defines a basic job to submit
to the queue manager. This doc will first describe the structure of a script from an
example and then provides instructions on how to submit the job using pyGRID. 

The script
++++++++++

Here is your first pyGRID script, copy its text and save it on a file
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
with the properties of a job to submit to the queue manager. The content of the code tag 
will be included verbatim at the end of the bash script and can contain any valid bash code.
In particular this can be:

* the path of an executable to be run on the cluster
* any bash command to run a python or matlab script on the cluster, e.g. "/usr/local/bin/matlab -nojvm -nodisplay -r matlab_job"
* any amount of bash code to manipulate files, create or delete folders, print environment variables etc.

The submission process
++++++++++++++++++++++

In order to submit the job we have just defined just type

::

    pyGRID -f basicTest.xml -s basicJob -b

in the terminal in the same folder of the *basicTest.xml* file. The job will be submitted 
by pyGRID to the queue manager. You can check its status with ``qstat`` which list your
currently active or queued jobs. Once *basicJob* finishes its output and error files will
be written in the current directory.

pyGRID command line options can be divided in three groups:

* XML file option. This option is Required.
    * ``-f <file_path>`` : specifies the path of the file to load.
* Simulation options. These are mutually exlusive and at least one is Required.
    * ``-s <job_name>`` : specifies the name of the simulation to load from the XML file.
    * ``-a`` : loads all the simulations in the file.
* Action options. Tell pyGRID which action to perform woth the specified simulation. These are mutually exclusive.
    * ``-w`` : write the shell script for the simulation.
    * ``-b`` : write the shell script and submit a job for every combination of the parameters of the simulation
    * ``-c`` : scan the output sctream of finished jobs and detect the crashed ones. The JOB_ID and TASK_ID of the crashed job is saved in the .grid auxilliary file.
    * ``-r`` : resubmit crashed jobs.

To review this options from the command line type ``pyGRID --help`` in the terminal.

Parameter Space
---------------

**Documentation coming soon.**

Advanced Topics
---------------

**Documentation coming soon.**

Inheritance
+++++++++++

Post Processing
+++++++++++++++