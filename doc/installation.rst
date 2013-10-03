Installation
============

If you don't have root privileges on the cluster, you'll have to install *pyGRID* in your
home directory.

For this follow these steps:

* Create the path ``~/lib/python2.6/site-packages`` (assuming you installed python version 2.6) in your home directory.
* Create the ``~/bin`` path.
* Add ``export PYTHONPATH=~/lib/python2.6/site-packages:$PYTHONPATH`` and ``export PATH=~/bin:$PATH`` to your .bashrc file (and run ``. ~/.bashrc``).
* Install *pyGRID* using ::

    easy_install --prefix=~ pyGRID

If you have root privilegies instead and you want to install *pyGRID* for every user
simply type ::

    easy_install pyGRID
