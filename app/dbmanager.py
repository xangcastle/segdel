from collections import namedtuple

from django.db import connection, connections


def local_sql_exec(strsql):
    cursor = connection.cursor()
    cursor.execute(strsql)
    results = namedtuplefetchall(cursor)
    return  results


def sql_exec(strsql, sqlconection):
    cursor = connections[sqlconection].cursor()
    cursor.execute(strsql)
    results = namedtuplefetchall(cursor)
    return  results


def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]