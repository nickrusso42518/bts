[![Build Status](https://app.travis-ci.com/nickrusso42518/bts.svg?branch=master)](
https://app.travis-ci.com/nickrusso42518/bts)

# BGP Traffic Server (BTS) Traffic Engineering Automation

BGP server implementations using `exabgp` to complete
the architecture described [here.](http://njrusmc.net/pub/bts_leaf_spine.pdf)

The exabgp design uses `flask` as a front-end to built a simple API for
announcing and withdrawing routes. CI testing has been applied, too.

At some point, the announcement and withdrawal of routes will be
automatically controlled via SNMP/telemetric monitoring.
