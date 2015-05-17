#!/bin/bash
set -exu

TESTDIR="$(dirname "$(readlink -f "$0")")"
APPDIR=$TESTDIR/..

python $APPDIR/cassandradump.py --import-file $TESTDIR/test_keyspace_init.cql
python $APPDIR/cassandradump.py --export-file /tmp/export1.cql --keyspace test_keyspace
python $APPDIR/cassandradump.py --import-file /tmp/export1.cql
python $APPDIR/cassandradump.py --export-file /tmp/export2.cql --keyspace test_keyspace
diff /tmp/export1.cql /tmp/export2.cql
