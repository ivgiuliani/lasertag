from sqlobject.sqlbuilder import *
from sqlobject import dberrors

from .db import TagIndex, connection, transaction
from .transformers import BaseTransformer
from .compat import is_string


# The default transformer will just return the same tags and values without
# any additional changes.
IDENTITY_TRANSFORMER = BaseTransformer()


def add_value(tags, value, transformers=None):
    transformers = transformers or [IDENTITY_TRANSFORMER]
    for transformer in transformers:
        tags, value = transformer.transform(tags, value)

    if not tags:
        raise AttributeError("Cannot add value with no tags")

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


def rename_tag(tag, to, with_value=None):
    where_stmt = "tag = '%s'" % tag
    if with_value is not None:
        where_stmt += " AND value = '%s'" % with_value

    update = Update(TagIndex.sqlmeta.table, values={"tag": to},
                    where=where_stmt)

    q = connection().sqlrepr(update)
    connection().query(q)


def replace_value(value, to):
    update = Update(TagIndex.sqlmeta.table, values={"value": to},
                    where="value = '%s'" % value)
    q = connection().sqlrepr(update)
    connection().query(q)
