from sqlobject.sqlbuilder import *

from .db import TagIndex, connection, transaction


def add_value(tags, value):
    with transaction() as t:
        for tag in tags:
            q = t.sqlrepr(Insert(TagIndex.sqlmeta.table, values={
                "tag": tag,
                "value": value
            }))
            t.query(q)

    return True


def query(tags):
    template = """
    SELECT DISTINCT value
      FROM tag_index
      WHERE tag = '%s'
    """
    q = " INTERSECT ".join([
        template % tag for tag in tags
    ])
    return [t[0] for t in connection().queryAll(q)]


def tags(value):
    select = Select(["tag"],
                    staticTables=[TagIndex.sqlmeta.table],
                    where=TagIndex.q.value == value)
    q = connection().sqlrepr(select)
    return [t[0] for t in connection().queryAll(q)]
