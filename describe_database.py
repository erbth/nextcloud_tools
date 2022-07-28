#!/usr/bin/python3
import getpass
import os
import re
import sys
import pymysql
import pymysql.cursors

MYSQL_USER = 'nextcloud'
MYSQL_DB = 'nextcloud'


def main():
    passwd = os.getenv('MYSQL_PASSWORD', None)
    if passwd is None:
        passwd = getpass.getpass("Password for '%s': " % MYSQL_USER)

    conn = pymysql.connect(
        host='localhost',
        user=MYSQL_USER,
        password=passwd,
        database=MYSQL_DB,
        cursorclass=pymysql.cursors.SSDictCursor)

    table_descs = []
    with conn:
        with conn.cursor() as cur:
            # List tables
            cur.execute('show tables;')
            tables = [list(v.values())[0] for v in cur.fetchall()]
            tables.sort()

        for table in tables:
            if not re.fullmatch(r'[0-9a-zA-Z_]+', table):
                raise RuntimeError("Invalid table name '%s'" % table)

            # Analyse table
            # Get columns
            with conn.cursor() as cur:
                cur.execute('show columns from `%s`;' % table)
                columns = [v['Field'] for v in cur.fetchall()]

                # Try to get sample data for each column
                cur.execute('select * from `%s`;' % table)
                def datasets():
                    while True:
                        buf = cur.fetchmany(25)
                        if not buf:
                            break

                        for ds in buf:
                            yield ds

                sample_data = {c: None for c in columns}
                for v in datasets():
                    for c in columns:
                        if sample_data[c] is None and v[c] is not None:
                            sample_data[c] = v[c]

                    if any(sample_data[c] is None for c in columns):
                        break

                table_descs.append((table, columns, sample_data))

        conn.rollback()

    # Print information
    max_col_len = max(max(len(c) for c in cs) for _,cs,_ in table_descs)
    max_col_len = min(max_col_len, 50)

    first = True
    for t,cs,sd in table_descs:
        if first:
            first = False
        else:
            print("\n")

        print("Table: '%s'" % t)
        print(80 * '-')
        for c in cs:
            s = str(sd[c])
            if len(s) > 20:
                s = s[:20] + '...'

            pad = ' ' * max(0, max_col_len - len(c))
            print("%s:%s e.g. %s" % (c, pad, s))


if __name__ == '__main__':
    main()
    sys.exit(0)
