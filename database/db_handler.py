from sqlalchemy import create_engine, ForeignKey, DateTime, Identity
from sqlalchemy import Table, Column, Integer, String, MetaData, LargeBinary
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = Column('id', String, primary_key=True)
    name = Column('name', String, nullable=False)
    refresh_token = Column('refresh_token', String)


class Presentations(Base):
    __tablename__ = 'presentations'

    id = Column('id', String, primary_key=True)
    name = Column('name', String, nullable=False)
    owner_id = Column('owner_id', String, ForeignKey("users.id"), nullable=False)
    folder_id = Column('folder_id', String, nullable=False)
    modified_time = Column('modified_time', DateTime, nullable=False)

    child_slides = relationship('Slides', backref='presentations', cascade='delete', passive_deletes=True)


class Slides(Base):
    __tablename__ = 'slides'

    id = Column('id', Integer, Identity(start=1, increment=1), primary_key=True)
    pres_id = Column('pres_id', String, ForeignKey("presentations.id", ondelete='CASCADE'), nullable=False)
    index = Column('index', Integer, nullable=False)
    thumbnail = Column('thumbnail', LargeBinary, nullable=False)

    parent_pres = relationship('Presentations', backref='slides')
    child_links = relationship('Links', backref='slides', cascade='delete', passive_deletes=True)


class Tags(Base):
    __tablename__ = 'tags'

    id = Column('id', Integer, Identity(start=1, increment=1), primary_key=True)
    name = Column('name', String, nullable=False)
    owner_id = Column('owner_id', String, ForeignKey("users.id"), nullable=False)


class Links(Base):
    __tablename__ = 'links'

    id = Column('id', Integer, Identity(start=1, increment=1), primary_key=True)
    slide_id = Column('slide_id', Integer, ForeignKey("slides.id", ondelete='CASCADE'), nullable=False)
    tag_id = Column('tag_id', Integer, ForeignKey("tags.id"), nullable=False)
    value = Column('value', Integer)
    parent_slides = relationship('Slides', backref='links')


class DatabaseHandler:
    def __init__(self):
        self.engine = create_engine("postgresql://admin:root@localhost:5000/pres_conf_db", echo=True, future=True)
        self.Session = sessionmaker(bind=self.engine)

    def create_db(self):
        Base.metadata.create_all(self.engine)


db_handler = DatabaseHandler()
db_handler.create_db()
