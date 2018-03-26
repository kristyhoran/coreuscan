
CoreuScan
=========
**A tool to download Core Genome MLST schemes for bacterial genomics**

    Installation and workflow to follow

**Author:** Kristy Horan


## Main functions
1. Find a database for a species and particular scheme
2. Download an existing cgMLST scheme (or 7 gene MLST) from a database

```
usage: coreuscan.py [-h] [-s SEARCH] [-l] [-L, --list-db] [-d] [-sp SPECIES]
                    [-db DB] [-o OUTPATH] [-st SCHEMA_TYPE]

Download MLST schema

optional arguments:
  -h, --help            show this help message and exit
  -s SEARCH, --search SEARCH
                        Search for a species and scheme type. Only possible to
                        search for one species at a time. Accepted strings are
                        one of genus, first letter of genus immediately
                        followed by species (no spaces or punctuation) or
                        species only
  -l, --list            show a list species for which schema are currently
                        available of all available shema. No input required
  -L, --list-db         list all available databases
  -d, --download        Download a MLST scheme.
  -sp SPECIES, --species SPECIES
                        REQUIRED if -d selected. The species for which the
                        MLST scheme is to be downloaded.
  -db DB, --database DB
                        OPTIONAL The location of the MLST database, if known.
                        For use with, list, search and download
  -o OUTPATH, --output OUTPATH
                        OPTIONAL An output path to save the .fasta files to.
                        Default is under pwd <species>_schema/
  -st SCHEMA_TYPE, --schema_type SCHEMA_TYPE
                        The type of schema, available options are cg or trad
  ```
## List databases

``` bash
coreuscan.py -L
```

```
======================================================>
Databases available through CoreuScan are:
======================================================>

Core genome schemes are available from:
------------------------------------------------------->
Enterobase
cgMLST
Pasteur Institute

7 gene MLST schemes are also available from:
------------------------------------------------------->
Enterobase
pubMLST
Pasteur Institute
```
