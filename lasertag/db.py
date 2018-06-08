from sqlobject import StringCol, SQLObject, DatabaseIndex

import logging
import sys

# TODO: move this out of here
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class TagIndex(SQLObject):
    tag = StringCol()
    value = StringCol()

    tagIndex = DatabaseIndex("tag")
    valueIndex = DatabaseIndex("value")


def make_connection(path=None):
    from sqlobject import sqlhub, connectionForURI
    if not path:
        # Default to in-memory database
        path = "sqlite:/:memory:?debug=1&logger=SQL&loglevel=info"

    log = logging.getLogger("SQL")
    log.info("Log started")

    sqlhub.processConnection = connectionForURI(path)


def migrate():
    TagIndex.createTable(ifNotExists=True)


def prepare():
    make_connection()
    migrate()
