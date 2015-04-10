# cassandradump
A data exporting tool for Cassandra inspired from mysqldump, with some added slice and dice capabilities.

Disclaimer: you really shouldn't be using this! Cassandra already offers much more robust and scalable data exporting/importing tools, such as:

- Snapshots
- CQL COPY FROM/TO commands
- sstable2json

However, especially during development, I frequently need to execute tasks such as:

- Quickly take a snapshot of an entire keyspace, and import it just as quickly without copying too many files around or losing too much time
- Ability to take a very small subset of a production database (according to some CQL-like filtering) and import it quickly on my development environment

If these use cases sound familiar, this tool might be useful for you.
