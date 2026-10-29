# Data directory

No real market data is included. The current experiment generates a synthetic price path from a geometric Brownian motion model.

For a future empirical study, document:
- source and retrieval timestamp;
- instrument and contract specification;
- time zone and timestamp alignment;
- missing-data handling;
- pool and position identifiers;
- fee-accounting methodology;
- exchange funding, spread, depth, and fee data;
- license and redistribution permissions.

Do not treat pool-wide swaps or volume as position-specific fee income without reconstructing the position's actual fee entitlement.
