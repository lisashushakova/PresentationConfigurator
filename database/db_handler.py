from sqlalchemy import create_engine, ForeignKey, DateTime, Identity
from sqlalchemy import Table, Column, Integer, String, MetaData, LargeBinary
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DatabaseHandler:
    def __init__(self):
        self.engine = create_engine("postgresql://admin:root@localhost:5000/pres_conf_db", echo=True, future=True)

    meta = MetaData()

    users = Table(
        'users', meta,
        Column('id', String, primary_key=True),
        Column('name', String, nullable=False),
        Column('refresh_token', String, nullable=False),
        Column('app_folder_id', String, nullable=False),
    )
    presentations = Table(
        'presentations', meta,
        Column('id', String, primary_key=True),
        Column('name', String, nullable=False),
        Column('owner_id', String, ForeignKey("users.id"), nullable=False),
        Column('modified_time', DateTime, nullable=False),
    )
    slides = Table(
        'slides', meta,
        Column('id', Integer, Identity(start=1, increment=1), primary_key=True),
        Column('pres_id', String, ForeignKey("presentations.id"), nullable=False),
        Column('thumbnail', LargeBinary, nullable=False),
    )
    tags = Table(
        'tags', meta,
        Column('id', Integer, Identity(start=1, increment=1), primary_key=True),
        Column('name', String, nullable=False),
        Column('owner_id', String, ForeignKey("users.id"), nullable=False),
    )
    links = Table(
        'links', meta,
        Column('id', Integer, Identity(start=1, increment=1), primary_key=True),
        Column('slide_id', Integer, ForeignKey("slides.id"), nullable=False),
        Column('tag_id', Integer, ForeignKey("tags.id"), nullable=False),
        Column('value', Integer),
    )

    def create_db(self):
        self.meta.create_all(self.engine)


db_handler = DatabaseHandler()
db_handler.create_db()
