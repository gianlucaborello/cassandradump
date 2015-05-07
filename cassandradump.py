import argparse
import sys

try:
    import cassandra
except ImportError:
    sys.exit('Python Cassandra driver not installed. You might try \"pip install cassandra-driver\".')

from cassandra.auth import PlainTextAuthProvider #For protocol_version 2
from cassandra.cluster import Cluster

TIMEOUT = 120.0
FETCH_SIZE = 100
DOT_EVERY = 1000

args = None


def log_quiet(msg):
    if not args.quiet:
        sys.stdout.write(msg)
        sys.stdout.flush()


def table_to_cqlfile(session, keyspace, tablename, flt, tableval, filep):
    if flt is None:
        query = 'SELECT * FROM "' + keyspace + '"."' + tablename + '"'
    else:
        query = 'SELECT * FROM ' + flt

    rows = session.execute(query)

    cnt = 0

    for row in rows:
        values = []
        for key, value in row.iteritems():
            if tableval.columns[key].data_type.typename == 'blob':
                encoded = session.encoder.cql_encode_bytes(value)
            else:
                encoded = session.encoder.cql_encode_all_types(value)

            values.append(encoded)

        filep.write('INSERT INTO "' + keyspace + '"."' + tablename + '" (' + ', '.join(row.keys()).encode('ascii') + ') VALUES (' + ', '.join(values) + ')\n')

        cnt += 1

        if (cnt % DOT_EVERY) == 0:
            log_quiet('.')

    if cnt > DOT_EVERY:
        log_quiet('\n')


def import_data(session):
    f = open(args.import_file, 'r')

    cnt = 0

    for line in f:
        session.execute(line)

        cnt += 1

        if (cnt % DOT_EVERY) == 0:
            log_quiet('.')

    if cnt > DOT_EVERY:
        log_quiet('\n')

    f.close()


def get_keyspace_or_fail(session, keyname):
    keyspace = session.cluster.metadata.keyspaces.get(keyname)

    if not keyspace:
        sys.stderr.write('Can\'t find keyspace "' + keyname + '"\n')
        sys.exit(1)

    return keyspace


def get_column_family_or_fail(keyspace, tablename):
    tableval = keyspace.tables.get(tablename)

    if not tableval:
        sys.stderr.write('Can\'t find table "' + tablename + '"\n')
        sys.exit(1)

    return tableval


def export_data(session):
    selection_options = 0

    if args.keyspace is not None:
        selection_options += 1

    if args.cf is not None:
        selection_options += 1

    if args.filter is not None:
        selection_options += 1

    if selection_options > 1:
        sys.stderr.write('--cf, --keyspace and --filter can\'t be combined\n')
        sys.exit(1)

    f = open(args.export_file, 'w')

    keyspaces = None

    if selection_options == 0:
        log_quiet('Exporting all keyspaces\n')
        keyspaces = []
        for keyspace in session.cluster.metadata.keyspaces.keys():
            if keyspace not in ('system', 'system_traces'):
                keyspaces.append(keyspace)

    if args.keyspace is not None:
        keyspaces = args.keyspace

    if keyspaces is not None:
        for keyname in keyspaces:
            keyspace = get_keyspace_or_fail(session, keyname)

            if not args.no_create:
                log_quiet('Exporting schema for keyspace ' + keyname + '\n')
                f.write('DROP KEYSPACE IF EXISTS "' + keyname + '";\n')
                f.write(keyspace.as_cql_query() + '\n')

            for tablename, tableval in keyspace.tables.iteritems():
                if tableval.is_cql_compatible:
                    if not args.no_create:
                        log_quiet('Exporting schema for column family ' + keyname + '.' + tablename + '\n')
                        f.write('DROP TABLE IF EXISTS "' + keyname + '"."' + tablename + '";\n')
                        f.write(tableval.as_cql_query() + ';\n')

                    if not args.no_insert:
                        log_quiet('Exporting data for column family ' + keyname + '.' + tablename + '\n')
                        table_to_cqlfile(session, keyname, tablename, None, tableval, f)

    if args.cf is not None:
        for cf in args.cf:
            if '.' not in cf:
                sys.stderr.write('Invalid keyspace.column_family input\n')
                sys.exit(1)

            keyname = cf.split('.')[0]
            tablename = cf.split('.')[1]

            keyspace = get_keyspace_or_fail(session, keyname)
            tableval = get_column_family_or_fail(keyspace, tablename)

            if tableval.is_cql_compatible:
                if not args.no_create:
                    log_quiet('Exporting schema for column family ' + keyname + '.' + tablename + '\n')
                    f.write('DROP TABLE IF EXISTS "' + keyname + '"."' + tablename + '";\n')
                    f.write(tableval.as_cql_query() + ';\n')

                if not args.no_insert:
                    log_quiet('Exporting data for column family ' + keyname + '.' + tablename + '\n')
                    table_to_cqlfile(session, keyname, tablename, None, tableval, f)

    if args.filter is not None:
        for flt in args.filter:
            stripped = flt.strip()
            cf = stripped.split(' ')[0]

            if '.' not in cf:
                sys.stderr.write('Invalid input\n')
                sys.exit(1)

            keyname = cf.split('.')[0]
            tablename = cf.split('.')[1]


            keyspace = get_keyspace_or_fail(session, keyname)
            tableval = get_column_family_or_fail(keyspace, tablename)

            if not tableval:
                sys.stderr.write('Can\'t find table "' + tablename + '"\n')
                sys.exit(1)

            if not args.no_insert:
                log_quiet('Exporting data for filter "' + stripped + '"\n')
                table_to_cqlfile(session, keyname, tablename, stripped, tableval, f)

    f.close()

def getCredential(self):
    return {'username': args.username, 'password': args.password}

def setup_cluster():
    if args.host is None:
        nodes = ['localhost']
    else:
        nodes = [args.host]

    cluster = None

    if args.protocol_version is not None and args.username is not None and args.password is not None:
        if args.protocol_version == '1':
            credentials = {'username': args.username, 'password': args.password}
            cluster = Cluster(contact_points=nodes, protocol_version=1, auth_provider=getCredential, load_balancing_policy=cassandra.policies.WhiteListRoundRobinPolicy(nodes))
        elif args.protocol_version == '2':
            ap = PlainTextAuthProvider(username=args.username, password=args.password)
            cluster = Cluster(contact_points=nodes, protocol_version=2, auth_provider=ap, load_balancing_policy=cassandra.policies.WhiteListRoundRobinPolicy(nodes))
    else:
        cluster = Cluster(contact_points=nodes, load_balancing_policy=cassandra.policies.WhiteListRoundRobinPolicy(nodes))
    session = cluster.connect()

    session.default_timeout = TIMEOUT
    session.default_fetch_size = FETCH_SIZE
    session.row_factory = cassandra.query.ordered_dict_factory
    return session


def cleanup_cluster(session):
    session.cluster.shutdown()
    session.shutdown()


def main():
    global args

    parser = argparse.ArgumentParser(description='A data exporting tool for Cassandra inspired from mysqldump, with some added slice and dice capabilities.')
    parser.add_argument('--host', help='the address of a Cassandra node in the cluster (localhost if omitted)')
    parser.add_argument('--keyspace', help='export a keyspace along with all its column families. Can be specified multiple times', action='append')
    parser.add_argument('--cf', help='export a column family. The name must include the keyspace, e.g. "system.schema_columns". Can be specified multiple times', action='append')
    parser.add_argument('--filter', help='export a slice of a column family according to a CQL filter. This takes essentially a typical SELECT query stripped of the initial "SELECT ... FROM" part (e.g. "system.schema_columns where keyspace_name =\'OpsCenter\'", and exports only that data. Can be specified multiple times', action='append')
    parser.add_argument('--no-insert', help='don\'t generate insert statements', action='store_true')
    parser.add_argument('--no-create', help='don\'t generate create (and drop) statements', action='store_true')
    parser.add_argument('--import-file', help='import data from the specified file')
    parser.add_argument('--protocol_version', help='set auth_provider version (required for authentication)')
    parser.add_argument('--username', help='set username for auth (only if protocol_version is set)')
    parser.add_argument('--password', help='set password for authentication (only if protocol_version is set)')
    parser.add_argument('--export-file', help='export data to the specified file')
    parser.add_argument('--quiet', help='quiet progress logging', action='store_true')
    args = parser.parse_args()

    if args.import_file is None and args.export_file is None:
        sys.stderr.write('--import-file or --export-file must be specified\n')
        sys.exit(1)

    if args.import_file is not None and args.export_file is not None:
        sys.stderr.write('--import-file and --export-file can\'t be specified at the same time\n')
        sys.exit(1)

    if args.protocol_version is not None:
    	if args.username is None or args.password is None:
    		sys.stderr.write('--username and --password must be specified\n')
    		sys.exit(1)

    session = setup_cluster()

    if args.import_file:
        import_data(session)
    elif args.export_file:
        export_data(session)

    cleanup_cluster(session)


if __name__ == '__main__':
    main()
