cassandradump
=============

.. image:: https://travis-ci.org/gianlucaborello/cassandradump.svg?branch=master
    :target: https://travis-ci.org/gianlucaborello/cassandradump

Description
-----------

A data exporting tool for Cassandra inspired from mysqldump, with some
additional slice and dice capabilities.

Disclaimer: most of the times, you really shouldn't be using this. It's
fragile, non-scalable, inefficient and verbose. Cassandra already offers
excellent exporting/importing tools:

-  Snapshots
-  CQL's COPY FROM/TO
-  sstable2json

However, especially during development, I frequently need to:

-  Quickly take a snapshot of an entire keyspace, and import it just as
   quickly without copying too many files around or losing too much time
-  Ability to take a very small subset of a massive production database
   (according to some CQL-like filtering) and import it quickly on my
   development environment

If these use cases sound familiar, this tool might be useful for you.

It's still missing many major Cassandra features that I don't use daily,
so feel free to open an issue pointing them out (or send a pull request)
if you need something.

Usage
-----

The help should already contain some useful information:

::

    usage: cassandradump.py [-h] [--cf CF] [--export-file EXPORT_FILE]
                            [--filter FILTER] [--host HOST] [--port PORT]
                            [--import-file IMPORT_FILE] [--keyspace KEYSPACE]
                            [--exclude-cf EXCLUDE_CF] [--no-create] [--no-insert]
                            [--password PASSWORD]
                            [--protocol-version PROTOCOL_VERSION] [--quiet]
                            [--sync] [--username USERNAME] [--ssl]
                            [--certfile CERTFILE]

    A data exporting tool for Cassandra inspired from mysqldump, with some added
    slice and dice capabilities.

    optional arguments:
      -h, --help            show this help message and exit
      --cf CF               export a column family. The name must include the
                            keyspace, e.g. "system.schema_columns". Can be
                            specified multiple times
      --export-file EXPORT_FILE
                            export data to the specified file
      --filter FILTER       export a slice of a column family according to a CQL
                            filter. This takes essentially a typical SELECT query
                            stripped of the initial "SELECT ... FROM" part (e.g.
                            "system.schema_columns where keyspace_name
                            ='OpsCenter'", and exports only that data. Can be
                            specified multiple times
      --host HOST           the address of a Cassandra node in the cluster
                            (localhost if omitted)
      --port PORT           the port of a Cassandra node in the cluster
                            (9042 if omitted)
      --import-file IMPORT_FILE
                            import data from the specified file
      --keyspace KEYSPACE   export a keyspace along with all its column families.
                            Can be specified multiple times
      --exclude-cf EXCLUDE_CF
                            when using --keyspace, specify column family to
                            exclude. Can be specified multiple times
      --no-create           don't generate create (and drop) statements
      --no-insert           don't generate insert statements
      --password PASSWORD   set password for authentication (only if
                            protocol-version is set)
      --protocol-version PROTOCOL_VERSION
                            set auth_provider version (required for
                            authentication)
      --quiet               quiet progress logging
      --sync                import data in synchronous mode (default asynchronous)
      --username USERNAME   set username for auth (only if protocol-version is
                            set)
      --ssl                 enable ssl connection to Cassandra cluster.  Must also
                            set --certfile.
      --certfile CERTFILE   ca cert file for SSL.  Assumes --ssl.

In its simplest invocation, it exports data and schemas for all
keyspaces:

::

    $ python cassandradump.py --export-file dump.cql
    Exporting all keyspaces
    Exporting schema for keyspace OpsCenter
    Exporting schema for column family OpsCenter.events_timeline
    Exporting data for column family OpsCenter.events_timeline
    Exporting schema for column family OpsCenter.settings
    Exporting data for column family OpsCenter.settings
    Exporting schema for column family OpsCenter.rollups60
    Exporting data for column family OpsCenter.rollups60
    ...

::

    $ cat dump.cql
    DROP KEYSPACE IF EXISTS "OpsCenter";
    CREATE KEYSPACE "OpsCenter" WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}  AND durable_writes = true;
    DROP TABLE IF EXISTS "OpsCenter"."events_timeline";
    CREATE TABLE "OpsCenter".events_timeline (key text, column1 bigint, value blob, PRIMARY KEY (key, column1)) WITH COMPACT STORAGE AND CLUSTERING ORDER BY (column1 ASC) AND caching = '{"keys":"ALL", "rows_per_partition":"NONE"}' AND comment = '{"info": "OpsCenter management data.", "version": [5, 1, 0]}' AND compaction = {'min_threshold': '4', 'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy', 'max_threshold': '8'} AND compression = {'sstable_compression': 'org.apache.cassandra.io.compress.LZ4Compressor'} AND dclocal_read_repair_chance = 0.0 AND default_time_to_live = 0 AND gc_grace_seconds = 864000 AND max_index_interval = 2048 AND memtable_flush_period_in_ms = 0 AND min_index_interval = 128 AND read_repair_chance = 0.25 AND speculative_retry = 'NONE';
    INSERT INTO "OpsCenter"."events_timeline" (key, column1, value) VALUES ('201501', 1419841027332869, 0x)
    INSERT INTO "OpsCenter"."events_timeline" (key, column1, value) VALUES ('201501', 1419841027352525, 0x)
    INSERT INTO "OpsCenter"."events_timeline" (key, column1, value) VALUES ('201501', 1419928979070954, 0x)
    ...

The created dump file can be directly used with ``cqlsh -f``, or there's
also a ``--import-file`` that uses asynchronous import so it goes
definitely fast.

Using ``--keyspace``, it's possible to filter for a specific set of
keyspaces

::

    $ python cassandradump.py --keyspace system --export-file dump.cql
    Exporting schema for keyspace system
    Exporting schema for column family system.peers
    Exporting data for column family system.peers
    Exporting schema for column family system.range_xfers
    Exporting data for column family system.range_xfers
    Exporting schema for column family system.schema_columns
    Exporting data for column family system.schema_columns
    ...

::

    $ cat dump.cql
    DROP KEYSPACE IF EXISTS "system";
    CREATE KEYSPACE system WITH replication = {'class': 'LocalStrategy'}  AND durable_writes = true;
    DROP TABLE IF EXISTS "system"."peers";
    CREATE TABLE system.peers (peer inet PRIMARY KEY, data_center text, host_id uuid, preferred_ip inet, rack text, release_version text, rpc_address inet, schema_version uuid, tokens set<text>) WITH bloom_filter_fp_chance = 0.01 AND caching = '{"keys":"ALL", "rows_per_partition":"NONE"}' AND comment = 'known peers in the cluster' AND compaction = {'min_threshold': '4', 'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy', 'max_threshold': '32'} AND compression = {'sstable_compression': 'org.apache.cassandra.io.compress.LZ4Compressor'} AND dclocal_read_repair_chance = 0.0 AND default_time_to_live = 0 AND gc_grace_seconds = 0 AND max_index_interval = 2048 AND memtable_flush_period_in_ms = 3600000 AND min_index_interval = 128 AND read_repair_chance = 0.0 AND speculative_retry = '99.0PERCENTILE';
    ...

Using ``--cf``, it's possible to filter for a specific set of column
families:

::

    $ python cassandradump.py --cf OpsCenter.rollups7200 --no-create --export-file dump.cql
    Exporting data for column family OpsCenter.rollups7200

::

    $ cat dump.cql
    INSERT INTO "OpsCenter"."rollups7200" (key, column1, value) VALUES ('127.0.0.1-foo', 718946047, 0x000000000000000000000000)
    INSERT INTO "OpsCenter"."rollups7200" (key, column1, value) VALUES ('127.0.0.1-foo', 718953247, 0x000000000000000000000000)
    INSERT INTO "OpsCenter"."rollups7200" (key, column1, value) VALUES ('127.0.0.1-foo', 718960447, 0x000000000000000000000000)
    INSERT INTO "OpsCenter"."rollups7200" (key, column1, value) VALUES ('127.0.0.1-foo', 718967647, 0x000000000000000000000000)
    INSERT INTO "OpsCenter"."rollups7200" (key, column1, value) VALUES ('127.0.0.1-foo', 719032447, 0x40073fc200000000437bc000)
    ...

Using ``--no-insert`` and ``--no-create`` it's possible to tweak what
CQL statements are actually included in the dump.

Most of the times, the column families in a production scenario are
huge, and you might just want a little slice of it. With ``--filter``,
it's possible to specify a set of CQL filters, and just the data that
satisfies those filters will be included in the dump:

::

    $ python cassandradump.py --filter "system.schema_columns WHERE keyspace_name='OpsCenter'" --export-file dump.cql
    Exporting data for filter "system.schema_columns where keyspace_name ='OpsCenter'"

::

    $ cat dump.cql
    INSERT INTO "system"."schema_columns" (keyspace_name, columnfamily_name, column_name, component_index, index_name, index_options, index_type, type, validator) VALUES ('OpsCenter', 'backup_reports', 'backup_id', 1, NULL, 'null', NULL, 'clustering_key', 'org.apache.cassandra.db.marshal.UTF8Type')
    INSERT INTO "system"."schema_columns" (keyspace_name, columnfamily_name, column_name, component_index, index_name, index_options, index_type, type, validator) VALUES ('OpsCenter', 'backup_reports', 'deleted_at', 4, NULL, 'null', NULL, 'regular', 'org.apache.cassandra.db.marshal.TimestampType')
