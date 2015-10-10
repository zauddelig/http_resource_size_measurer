Usage:
python3 measure.py url [-p numberr of processes per pool] [-T]
Per Default it will calculate the entire size of the http resource going 
down the iframes tree, it will also calculate
the harmonic mean of the resources speed, this always includes the connection making time.

This script is used to measure the *weight* of a http resource in terms of data a
nd the mean speed using the harmonic mean.

The speed is calculate considering a chain of syncronous calls 
without recicling the connection as the HTTP1/1 would allow,
if urllib3, or requests, is going to be used this mean 
will most probably change (has the connection could be reused) and at that point
the manual pooling will be useless.

In the `HTML` case it will calculate the entire resource Tree, including css, scripts and iframe. 
This is recursive, i.e. if an iframe is encountered it will calculate all the sub resources tree.

