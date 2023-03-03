import base64

import cv2
import numpy as np
from sqlalchemy import create_engine, ForeignKey, DateTime, Identity, text, update, select, asc
from sqlalchemy import Table, Column, Integer, String, MetaData, LargeBinary
from sqlalchemy.orm import declarative_base, relationship, scoped_session
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = Column('id', String, primary_key=True)
    name = Column('name', String, nullable=False)


class Folders(Base):
    __tablename__ = 'folders'

    id = Column('id', String, primary_key=True)
    name = Column('name', String, nullable=False)
    owner_id = Column('owner_id', String, ForeignKey("users.id"), nullable=False)


class FolderPreferences(Base):
    __tablename__ = 'folder_preferences'
    id = Column('id', Integer, Identity(start=1, increment=1), primary_key=True)
    owner_id = Column('owner_id', String, ForeignKey("users.id"), nullable=False)
    folder_id = Column('folder_id', String, ForeignKey("folders.id"), nullable=False)


class Presentations(Base):
    __tablename__ = 'presentations'

    id = Column('id', String, primary_key=True)
    name = Column('name', String, nullable=False)
    owner_id = Column('owner_id', String, ForeignKey("users.id"), nullable=False)
    folder_id = Column('folder_id', String, nullable=False)
    modified_time = Column('modified_time', DateTime, nullable=False)

    child_slides = relationship('Slides', backref='presentations', cascade='all, delete', passive_deletes=True)
    child_links = relationship('PresentationLinks', backref='presentations', cascade='delete', passive_deletes=True)

class Slides(Base):
    __tablename__ = 'slides'

    id = Column('id', Integer, Identity(start=1, increment=1), primary_key=True)
    pres_id = Column('pres_id', String, ForeignKey("presentations.id", ondelete='CASCADE'), nullable=False)
    index = Column('index', Integer, nullable=False)
    thumbnail = Column('thumbnail', LargeBinary, nullable=False)
    text = Column('text', String, nullable=False)
    ratio = Column('ratio', Integer, nullable=True)

    parent_pres = relationship('Presentations', backref='slides', cascade='all, delete')
    child_links = relationship('SlideLinks', backref='slides', cascade='delete', passive_deletes=True)

    def json(self):
        return {
            'id': self.id,
            'pres_id': self.pres_id,
            'index': self.index,
            'thumbnail': base64.b64encode(self.thumbnail),
            'text': self.text,
            'ratio': self.ratio
        }

class Tags(Base):
    __tablename__ = 'tags'

    id = Column('id', Integer, Identity(start=1, increment=1), primary_key=True)
    name = Column('name', String, nullable=False)
    owner_id = Column('owner_id', String, ForeignKey("users.id"), nullable=False)


class SlideLinks(Base):
    __tablename__ = 'slide_links'

    id = Column('id', Integer, Identity(start=1, increment=1), primary_key=True)
    slide_id = Column('slide_id', Integer, ForeignKey("slides.id", ondelete='CASCADE'), nullable=False)
    tag_id = Column('tag_id', Integer, ForeignKey("tags.id"), nullable=False)
    value = Column('value', Integer)
    parent_slides = relationship('Slides', backref='slide-links')


class PresentationLinks(Base):
    __tablename__ = 'presentation_links'

    id = Column('id', Integer, Identity(start=1, increment=1), primary_key=True)
    pres_id = Column('pres_id', String, ForeignKey("presentations.id", ondelete='CASCADE'), nullable=False)
    tag_id = Column('tag_id', Integer, ForeignKey("tags.id"), nullable=False)
    value = Column('value', Integer)
    parent_slides = relationship('Presentations', backref='pres-links')


class DatabaseHandler:
    def __init__(self):
        self.engine = create_engine(
            "postgresql://admin:root@localhost:5000/pres_conf_db",
            echo=True,
            future=True)
        self.Session = sessionmaker(bind=self.engine)

    def create_db(self):
        Base.metadata.create_all(self.engine)

    def clear_db(self):
        session = self.Session()
        session.execute('''TRUNCATE TABLE users CASCADE''')
        session.execute('''TRUNCATE TABLE presentations CASCADE''')
        session.execute('''TRUNCATE TABLE slides CASCADE''')
        session.execute('''TRUNCATE TABLE tags CASCADE''')
        session.execute('''TRUNCATE TABLE presentation_links CASCADE''')
        session.execute('''TRUNCATE TABLE slide_links CASCADE''')
        session.execute('''TRUNCATE TABLE folders CASCADE''')
        session.execute('''TRUNCATE TABLE folder_preferences CASCADE''')
        session.commit()
        session.close()

    @staticmethod
    def row_to_dict(row):
        d = {}
        for column in row.__table__.columns:
            d[column.name] = str(getattr(row, column.name))
        return d

    # GENERAL CRUD
    def create(self, table, **kwargs):
        session = self.Session()
        obj = self.read(table, kwargs.get('id'))
        if obj is None:
            obj = table(**kwargs)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            session.close()
            created = True
        else:
            created = False
        return created, obj

    def find_or_create(self, table, *criterion, **kwargs):
        session = self.Session()
        obj = self.find(table, *criterion)
        if obj is None:
            session.add(table(**kwargs))
            session.commit()
            session.close()
            obj = self.find(table, *criterion)
            return True, obj
        return False, obj

    def read(self, table, obj_id):
        session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=self.engine))
        obj = session.query(table).get(obj_id)
        session.close()
        return obj

    def update(self, table, obj_id, **kwargs):
        session = self.Session()
        obj = session.query(table).filter(table.id == obj_id).first()
        if obj is None:
            updated = False
        else:
            for kwarg, value in kwargs.items():
                setattr(obj, kwarg, value)
            session.commit()
            session.close()
            updated = True
        return updated

    def delete(self, table, obj_id):
        session = self.Session()
        session.query(table).filter(table.id == obj_id).delete()
        session.commit()
        session.close()

    def findall(self, table, *criterion):
        session = self.Session()
        result = session.query(table).where(*criterion).all()
        session.close()
        return result

    def find(self, table, *criterion):
        session = self.Session()
        result = session.query(table).where(*criterion).first()
        session.close()
        return result

    # SPECIFIED METHODS
    def get_slides_by_text(self, user_id, search_phrase):
        session = self.Session()
        stmt = select(Slides.__table__).join(Presentations)\
            .where(
                Presentations.owner_id == user_id,
                Slides.text.like(f'%{search_phrase.lower()}%'))
        slides = session.execute(stmt).all()
        session.close()
        return slides

    def get_slides_index_asc(self, user_id, pres_id):
        session = self.Session()
        pres = self.read(Presentations, pres_id)
        if pres is not None and pres.owner_id == user_id:
            slides = session.query(Slides)\
                .filter(Slides.pres_id == pres.id)\
                .order_by(Slides.index)\
                .all()
            session.close()
            return slides
        else:
            session.close()
            return None

    def get_links_and_tags(self, table, user_id, tag_names):
        session = self.Session()
        links_and_tags = session.query(table, Tags) \
            .filter(Tags.name.in_(tag_names), Tags.owner_id == user_id) \
            .filter(table.tag_id == Tags.id) \
            .all()
        session.close()
        return links_and_tags

    def get_slide_thumb_by_index(self, user_id, pres_id, index):
        session = self.Session()
        pres = self.read(Presentations, pres_id)
        if pres is not None and pres.owner_id == user_id:
            slide = session.query(Slides) \
                .filter(Slides.pres_id == pres.id, Slides.index == index) \
                .first()
            session.close()
            return slide.thumbnail
        else:
            session.close()
            return None

if __name__ == "__main__":
    db_handler = DatabaseHandler()
    db_handler.create_db()
