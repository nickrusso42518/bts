[![Build Status](https://app.travis-ci.com/nickrusso42518/bts.svg?branch=master)](
https://app.travis-ci.com/nickrusso42518/bts)

# BGP Traffic Server (BTS) Traffic Engineering Automation

BGP server implementations using `exabgp` to complete
the architecture described [here.](http://njrusmc.net/pub/bts_leaf_spine.pdf)

> Contact information:\
> Email:    njrusmc@gmail.com\
> Twitter:  @nickrusso42518

There are two API implementations in this repository:

1. __Flask/HTTP__: This uses Python `flask` as a front-end to build a simple
   HTTP API (not RESTful) for announcing and withdrawing routes. 
   This includes a Postman collection and corresponding environment to
   simplify adoption/testing.

2. __gRPC__: This uses a custom protobuf services file to define various
   RPCs supported by the API. It also includes a compilation script
   for Python source code.
