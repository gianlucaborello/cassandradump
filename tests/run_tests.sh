#!/bin/bash
set -exu

TESTDIR="$(dirname "$(readlink -f "$0")")"
APPDIR=$TESTDIR/..

python $APPDIR/cassandradump.py --import-file $TESTDIR/test_keyspace_init.cql

python $APPDIR/cassandradump.py --export-file /tmp/dump.cql --keyspace test_keyspace
diff $TESTDIR/full_export.cql.expected /tmp/dump.cql

python $APPDIR/cassandradump.py --import-file $TESTDIR/full_export.cql.expected

python $APPDIR/cassandradump.py --export-file /tmp/dump.cql --keyspace test_keyspace
diff $TESTDIR/full_export.cql.expected /tmp/dump.cql

python $APPDIR/cassandradump.py --export-file /tmp/dump.cql --cf test_keyspace.twenty_rows_composite_table
diff $TESTDIR/cf_export.cql.expected /tmp/dump.cql

python $APPDIR/cassandradump.py --export-file /tmp/dump.cql --cf test_keyspace.twenty_rows_composite_table --no-create
diff $TESTDIR/cf_export_nocreate.cql.expected /tmp/dump.cql

python $APPDIR/cassandradump.py --export-file /tmp/dump.cql --cf test_keyspace.twenty_rows_composite_table --no-insert
diff $TESTDIR/cf_export_noinsert.cql.expected /tmp/dump.cql

python $APPDIR/cassandradump.py --export-file /tmp/dump.cql --filter "test_keyspace.twenty_rows_composite_table WHERE a = 'A' AND b = '19'"
diff $TESTDIR/filter.cql.expected /tmp/dump.cql
