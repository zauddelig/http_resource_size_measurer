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





