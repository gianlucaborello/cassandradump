TESTDIR=${PWD}
APPDIR=${TESTDIR}/..

t1:
	python ${APPDIR}/cassandradump.py --import-file ${TESTDIR}/test_keyspace_init.cql --sync

t2:
	python ${APPDIR}/cassandradump.py --export-file /tmp/dump.cql --keyspace test_keyspace
	bash compare.sh ${TESTDIR}/full_export.cql.expected /tmp/dump.cql

t3:
	python ${APPDIR}/cassandradump.py --import-file ${TESTDIR}/full_export.cql.expected

t4:
	python ${APPDIR}/cassandradump.py --export-file /tmp/dump.cql --keyspace test_keyspace
	bash compare.sh ${TESTDIR}/full_export.cql.expected /tmp/dump.cql

t5:
	python ${APPDIR}/cassandradump.py --import-file ${TESTDIR}/full_export.cql.expected --sync

t6:
	python ${APPDIR}/cassandradump.py --export-file /tmp/dump.cql --keyspace test_keyspace
	bash compare.sh ${TESTDIR}/full_export.cql.expected /tmp/dump.cql

t7:
	python ${APPDIR}/cassandradump.py --export-file /tmp/dump.cql --cf test_keyspace.twenty_rows_composite_table
	bash compare.sh ${TESTDIR}/cf_export.cql.expected /tmp/dump.cql

t8:
	python ${APPDIR}/cassandradump.py --export-file /tmp/dump.cql --cf test_keyspace.twenty_rows_composite_table --no-create
	bash compare.sh ${TESTDIR}/cf_export_nocreate.cql.expected /tmp/dump.cql

t9:
	python ${APPDIR}/cassandradump.py --export-file /tmp/dump.cql --cf test_keyspace.twenty_rows_composite_table --no-insert
	bash compare.sh ${TESTDIR}/cf_export_noinsert.cql.expected /tmp/dump.cql

t10:
	python ${APPDIR}/cassandradump.py --export-file /tmp/dump.cql --filter "test_keyspace.twenty_rows_composite_table WHERE a = 'A' AND b = '19'"
	bash compare.sh ${TESTDIR}/filter.cql.expected /tmp/dump.cql

tests: t1 t2 t3 t4 t5 t6 t7 t8 t9 t10
