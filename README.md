# cassandradump

## Description

A data exporting tool for Cassandra inspired from mysqldump, with some added slice and dice capabilities.

Disclaimer: you really shouldn't be using this! This is fragile, non-scalable, inefficient and verbose! Cassandra already offers excellent exporting/importing tools:

- Snapshots
- CQL COPY FROM/TO commands
- sstable2json

However, especially during development, I frequently need to execute tasks such as:

- Quickly take a snapshot of an entire keyspace, and import it just as quickly without copying too many files around or losing too much time
- Ability to take a very small subset of a massive production database (according to some CQL-like filtering) and import it quickly on my development environment

If these use cases sound familiar, this tool might be useful for you.

It's still missing many major Cassandra features that I don't use daily, so feel free to open an issue pointing them out (or send a pull request) if you need something.

## Usage

The help should already contain some useful information:

```
$ python cassandradump.py --help
usage: cassandradump.py [-h] [--host HOST] [--keyspace KEYSPACE] [--cf CF]
                        [--predicate PREDICATE] [--no-insert] [--no-create]
                        [--import-file IMPORT_FILE]
                        [--export-file EXPORT_FILE] [--quiet]

A data exporting tool for Cassandra inspired from mysqldump, with some added
slice and dice capabilities.

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           the address of a Cassandra node in the cluster
                        (localhost if omitted)
  --keyspace KEYSPACE   export a keyspace along with all its column families.
                        Can be specified multiple times
  --cf CF               export a column family. The name must include the
                        keyspace, e.g. "system.schema_columns". Can be
                        specified multiple times
  --predicate PREDICATE
                        export a slice of a column family according to a CQL
                        filter. This takes essentially a typical SELECT query
                        stripped of the initial "SELECT ... FROM" part (e.g.
                        "system.schema_columns where keyspace_name
                        ='OpsCenter'", and exports only that data. Can be
                        specified multiple times
  --no-insert           don't generate insert statements
  --no-create           don't generate create (and drop) statements
  --import-file IMPORT_FILE
                        import data from the specified file
  --export-file EXPORT_FILE
                        export data to the specified file
  --quiet               quiet progress logging
```

In its simplest invocation, it exports all the schemas and data:

```
gianluca@sid:~$ python cassandradump.py --export-file dump.cql
```
