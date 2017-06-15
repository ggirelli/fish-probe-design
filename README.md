fish-probe-design
===

Suit to select set of oligomers as FISH probes from databases of locus-specific hybridizing oligomers. Every database is expected to be a folder with one txt file per chromosome, containing the starting location of each oligo. The length of the oligo is encoded in the folder name.

The `extract_database.py` script can be used to convert a sqlite3 database into single-chromosome txt files in the aforementioned format.

A web-interface to interact with the `query_database.py` script is available on request.

## How-to

0. Create `mkdir ../db/` and `mkdir ../query/`.
1. Run `extract_database.py db_path table_name --outdir ../db/` to generate the database.
2. Run `query_database.py` to identify probes. For more details, check [the documentation](docs/query_database.md).

## @TODO

* Specify expected database folder name format.
