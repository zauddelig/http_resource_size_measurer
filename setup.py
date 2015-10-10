#!/usr/bin/env python3
from distutils.core import setup
__doc__ = """
Usage:
------

```python3 measure.py url [-p number of processes per pool] [-T]```

Per Default it will calculate the entire size of the http resource going
down the iframes tree, it will also calculate
the harmonic mean of the resources speed, this always includes the connection making time.

If `-T` is specified it will print to stdout a nice scheme of the resources tree.

If `-p N` the script will pool `N` processes for parsing sub resources tree, note that this option is not fully tested, consider it an experiment.

Versions
-----------

0.6 - alpha *somewhat stable* release

RoadMap
--------

* 0.7 - The mean will be calculated as if the connections were recycled.
* 0.8 - `-c --csv` parameter will write a csv file out of the resources tree.
* 0.9 - `-j --json` parameter will write to stdout a json object reppresenting the structure.
* 1.0 - The Link parser will be fully compliant to [rfc1808](http://www.ietf.org/rfc/rfc1808.txt)

Open Points
===========
I have yet to decide if  I should use requests or urllib3 or just leave it like it is and use only stdlib.
"""

setup(
    name='http_resource_measurer',
    version='0.6',
    url='https://github.com/zauddelig/http_resource_size_measurer',
    license='BSD',
    author='Fabrizio Ettore Messina',
    author_email='zauddelig@gmail.com',
    description='A simple script to get the resource lenght',
    long_description=__doc__,
    install_requires=[
    ],
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python > 3.2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)