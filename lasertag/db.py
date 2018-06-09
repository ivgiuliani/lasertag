from sqlobject import StringCol, SQLObject, DatabaseIndex
from sqlobject import sqlhub, connectionForURI

import logging


class TagIndex(SQLObject):
    tag = StringCol()
    value = StringCol()

    tags = DatabaseIndex("tag")
    values = DatabaseIndex("value")
    unique_pairs = DatabaseIndex("tag", "value", unique=True)


def make_connection(conn_string):
    assert conn_string is not None

    log = logging.getLogger("SQL")
    log.info("Log started")

    sqlhub.processConnection = connectionForURI(conn_string)


def connection():
    return sqlhub.processConnection


class ControlledTransaction(object):
    def __init__(self, connection):
        self.connection = connection
        self.transaction = None

    def __enter__(self):
        self.transaction = self.connection.transaction()
        return self.transaction

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is None:
            # no exception, commit the transaction
            self.transaction.commit()
        else:
            self.transaction.rollback()


def transaction():
    return ControlledTransaction(connection())


def migrate():
    TagIndex.createTable(ifNotExists=True)


def prepare(conn_string):
    make_connection(conn_string)
    migrate()
