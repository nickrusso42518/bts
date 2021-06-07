# BGP Traffic Server (BTS) Traffic Engineering Automation

BGP server implementations using `exabgp` and `gobgp` to implement
the architecture described [here.](http://njrusmc.net/pub/bts_leaf_spine.pdf)

The exabgp design uses `flask` as a front-end to built a simple API for
announcing and withdrawing routes.

The gobgp design (coming soon) uses gRPC instead.

At some point, the announcement and withdrawal of routes will be
automatically controlled via SNMP/telemetric monitoring.
