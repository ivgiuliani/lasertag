from sqlobject.sqlbuilder import *
from sqlobject import dberrors

from .db import TagIndex, connection, transaction
from .compat import is_string

def add_value(tags, value):
    try:
        with transaction() as t:
            for tag in tags:
                insert = Insert(TagIndex.sqlmeta.table, values={
                    "tag": tag,
                    "value": value
                })
                t.query(t.sqlrepr(insert))
    except dberrors.DuplicateEntryError:
        raise AttributeError("Duplicate detected for %s:%s" % (tags, value))

    return True


def query(tags=None):
    tags = tags or []
    if not tags:
        raise AttributeError("Cannot specify an empty query")

    if is_string(tags):
        tags = [tags]

    template = "SELECT DISTINCT value FROM tag_index WHERE tag = '%s'"
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
