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
* any bash command to run a python or matlab script on the cluster, e.g. *"/usr/local/bin/matlab -nojvm -nodisplay -r matlab_job"*
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
    * ``-c`` : scan the output sctream of finished jobs and detect the crashed ones. The *JOB_ID* and *TASK_ID* of the crashed job is saved in an auxilliary file with extension ``.grid``.
    * ``-r`` : resubmit crashed jobs.

To review this options from the command line type ``pyGRID --help`` in the terminal.

Parameter Space
---------------

Some simulations require to span a parameter space and submitting jobs for every
combination of parameters in *qsub* can be tedious. *pyGRID* streamlines the process and
automatically submit for you a job for each combination of the parameters.

Let's look at the following script:

.. code-block:: xml

    <?xml version="1.0"?>
    <simulations>
    
        <sim_element N="parSpace">
            <S>/bin/bash</S>
            <j>y</j>
            <cwd />
               
            <parameters>
                <parameter name="omega"> 1:3:10 </parameter>
                <parameter name="Amp"> 1.0 2.0:3:6.0 10.0 </parameter>
            </parameters>
            <code>
                echo "Parameter space example"
                echo $omega
                echo $Amp 
            </code>
            <o>$JOB_NAME.$JOB_ID.$PAR_omega.$PAR_Amp</o>
        </sim_element>
        
    </simulations>
    
We introduced a few new things in this script. The most important is the ``<parameters>``
element which contains the definition of the parameters we need in the simulation.

Each parameter is defined with a ``<parameter name="...">`` element that requires a 
``name`` attribute identifying it. Inside the *parameter* element we define the values
we want it to assume. At the moment *pyGRID* accepts two notations for this:

* ``A:N:B`` which produces *N* evenly distributed values in the *A-B* interval.
* ``A B C``, a simple list of values.

The two notations can easily be mixed as you see in 

.. code-block:: xml

    <parameter name="Amp"> 1.0 2.0:3:6.0 10.0 </parameter>
    
from the script above.

While submitting a job, *pyGRID* pass the current combination of parameter values to the
queue manager as *ENVIRONMENT VARIABLES* whose value can be accessed through the name
``$<parameter_name>``. In the example above

.. code-block:: xml

    <code>
        echo "Parameter space example"
        echo $omega
        echo $Amp 
    </code>
    
the code will access the current values of the parameters for this job and output it.

Finally, the values of the paramater can also be used in the filename for the output and
error streams of the job. These values can be accessed with the syntax
``$PAR_<parameter_name>``. By specifying

.. code-block:: xml

    <o>$JOB_NAME.$JOB_ID.$PAR_omega.$PAR_Amp</o>

*pyGRID* will tell *qsub* to create output file names where ``$PAR_omega`` and 
``$PAR_Amp`` is substituted with the values of the parameter for a job.

Advanced Topics
---------------

Inheritance
+++++++++++

In order to avoid to redefine the same options over and over for every job *pyGRID*
allows a job to inherit its options from another job.

Consider the script

.. code-block:: xml

    <?xml version="1.0"?>
    <simulations>
    
        <sim_element N="basicJob">
            <S>/bin/bash</S>
            <j>y</j>
            <cwd />
            <code> echo "Basic Job" </code> 
        </sim_element>
        
        <sim_element N="inheritedJob" inherit="basicJob">
            <j> n </j>
            <t> 1-10 </t> 
        </sim_element>
    
    </simulations>

In ``<sim_element N="inheritedJob" inherit="basicJob">`` we have introduced the attribute
**inherit** which tells *pyGRID* to load the options of *basicJob* first and then add or
overwrite them with the options of *inheritedJob*. 

In case *inheritedJob* will overwrite the *j* option from *basicJob* and add the *t* 
option which has the effect to make it an array job.

Post Processing
+++++++++++++++

Sometimes when running array jobs or simulations that span a parameter space waiting for
all the jobs to finish before doing the data analysis is tedious. For this reason *pyGRID*
make it easy to define dependencies between jobs so that when a group of simulations
finishes another job is automatically executed.

Look at the script

.. code-block:: xml

    <?xml version="1.0"?>
    <simulations>
    
        <sim_element N="parSpace" post_processing="postProcJob">
            <S>/bin/bash</S>
            <j>y</j>
            <cwd />
               
            <parameters>
                <parameter name="omega"> 1:3:10 </parameter>
                <parameter name="Amp"> 1.0 2.0:3:6.0 10.0 </parameter>
            </parameters>
            <code>
                echo "Parameter space example"
                echo $omega
                echo $Amp 
            </code>
            <o>$JOB_NAME.$JOB_ID.$PAR_omega.$PAR_Amp</o>
        </sim_element>
        
        <sim_element N="postProcJob">
            <cwd />
            <S>/bin/bash</S>
            <j>y</j>
            <code> echo "All of the parSpace jobs have finished" </code>
        </sim_element>
        
    </simulations>
    
where we have introduced the attribute **post_processing**, containing the name of
another *sim_element* in the script. When you specify **post_processing** *pyGRID* will
submit all the jobs for *parSpace* first and then submit the *postProcJob* telling
*qsub* not to execute it until all the *parSpace* jobs have finished.

.. warning::

    The post_processing job will not execute if any of the jobs it depends on exits because of an error.