from sqlobject import StringCol, SQLObject, DatabaseIndex
from sqlobject import sqlhub, connectionForURI

import logging
import sys

# TODO: move this out of here
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class TagIndex(SQLObject):
    tag = StringCol()
    value = StringCol()

    tags = DatabaseIndex("tag")
    values = DatabaseIndex("value")
    unique_pairs = DatabaseIndex("tag", "value", unique=True)


def make_connection(path=None):
    if not path:
        # Default to in-memory database
        path = "sqlite:/:memory:?debug=1&logger=SQL&loglevel=info"

    log = logging.getLogger("SQL")
    log.info("Log started")

    sqlhub.processConnection = connectionForURI(path)


def connection():
    return sqlhub.processConnection


def transaction():
    return connection().transaction()


def migrate():
    TagIndex.createTable(ifNotExists=True)


def prepare(conn_string):
    make_connection(path=conn_string)
    migrate()
