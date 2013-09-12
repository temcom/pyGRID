#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name="pyGRID",
      version="0.1",
      license="GPLv2",
      keywords="scientific/engineering simulation",
      platforms="OS Independent",
      description="""Python utilities to interface with SUN GRID ENNGINE and allow to run
                    simulations that span a parameter space""",
      long_description=""" pyGRID """,
      author="Jacopo Sabbatini",
      author_email="sabbatini@physics.uq.edu.au",
      packages=find_packages(),
      classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
      ],
      entry_points={
        'console_scripts': [
            'pyGRID = pyGRID:main',
            ],
      },
      )