import base64
import re
from datetime import datetime
import enum
import os
from threading import Lock

from sqlalchemy import create_engine, ForeignKey, DateTime, Identity, text, update, select, asc, Boolean, Enum
from sqlalchemy import Table, Column, Integer, String, MetaData, LargeBinary
from sqlalchemy.orm import declarative_base, relationship, scoped_session
from sqlalchemy.orm import sessionmaker

from app.definitions import SERVER_ROOT
from app.server.main.utils import utils

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = Column('id', String, primary_key=True)
    name = Column('name', String, nullable=False)


class Folders(Base):
    __tablename__ = 'folders'

    id = Column('id', String, primary_key=True)
    name = Column('name', String, nullable=False)
    parent = Column('parent', String)
    mark = Column('mark', Boolean, nullable=False)
    owner_id = Column('owner_id', String, ForeignKey("users.id"), nullable=False)


class Presentations(Base):
    __tablename__ = 'presentations'

    id = Column('id', String, primary_key=True)
    name = Column('name', String, nullable=False)
    owner_id = Column('owner_id', String, ForeignKey("users.id"), nullable=False)
    modified_time = Column('modified_time', DateTime, nullable=False)

    child_slides = relationship('Slides', backref='presentations', cascade='all, delete', passive_deletes=True)
    child_links = relationship('PresentationLinks', backref='presentations', cascade='delete', passive_deletes=True)

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'owner_id': self.owner_id,
            'modified_time': str(self.modified_time)
        }


class Slides(Base):
    __tablename__ = 'slides'

    class Ratio(enum.Enum):
        WIDESCREEN_16_TO_9 = 'WIDESCREEN_16_TO_9',
        STANDARD_4_TO_3 = 'STANDARD_4_TO_3'

    id = Column('id', Integer, Identity(start=1, increment=1), primary_key=True)
    pres_id = Column('pres_id', String, ForeignKey("presentations.id", ondelete='CASCADE'), nullable=False)
    index = Column('index', Integer, nullable=False)
    thumbnail = Column('thumbnail', LargeBinary, nullable=False)
    text = Column('text', String, nullable=False)
    ratio = Column('ratio', Enum(Ratio), nullable=True)

    parent_pres = relationship('Presentations', backref='slides', cascade='all, delete')
    child_links = relationship('SlideLinks', backref='slides', cascade='delete', passive_deletes=True)

    def json(self):
        return {
            'id': self.id,
            'pres_id': self.pres_id,
            'index': self.index,
            'thumbnail': base64.b64encode(self.thumbnail),
            'text': self.text,
            'ratio': self.ratio.value
        }


class Tags(Base):
    __tablename__ = 'tags'

    id = Column('id', Integer, Identity(start=1, increment=1), primary_key=True)
    name = Column('name', String, nullable=False)
    owner_id = Column('owner_id', String, ForeignKey("users.id"), nullable=False)

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'owner_id': self.owner_id
        }


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
    def __init__(self, user, password, host, db, pool, echo=True):
        self.engine = create_engine(
            f"postgresql://{user}:{password}@{host}/{db}",
            echo=echo,
            future=True)
        self.Session = sessionmaker(bind=self.engine)
        self.pool = pool
        self.lock_mutex = Lock()
        self.sync_query = {}

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
        session.commit()
        session.close()

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

    def get_slides_index_asc(self, pres_id):
        session = self.Session()
        pres = self.read(Presentations, pres_id)
        if pres is not None:
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

    def sync_folders(self, user_id, actual_folders):
        synced_folders = []
        for folder in actual_folders:
            _, db_folder = self.create(
                Folders,

                id=folder.get('id'),
                name=folder.get('name'),
                mark=False,
                owner_id=user_id
            )
            synced_folders.append(db_folder)

        db_folders = self.findall(Folders, Folders.owner_id == user_id)

        for db_folder in db_folders:
            if len([folder for folder in actual_folders if folder.get('id') == db_folder.id]) == 0:
                self.delete(Folders, db_folder.id)

        return synced_folders

    def sync_presentations(self, user_id, actual_presentations):
        synced_presentations = []

        db_presentations = self.findall(Presentations, Presentations.owner_id == user_id)
        for db_pres in db_presentations:
            removed = True
            for actual_pres in actual_presentations:
                if db_pres.id == actual_pres.get('id'):
                    removed = False
                    break
            if removed:
                self.delete(Presentations, db_pres.id)

        # Presentation data which require download to sync
        created_presentations = []
        modified_presentations = []

        for actual_pres in actual_presentations:
            created, db_pres = self.create(
                Presentations,

                id=actual_pres.get('id'),
                name=actual_pres.get('name'),
                owner_id=user_id,
                modified_time=actual_pres.get('modifiedTime')
            )

            if created:
                synced_presentations.append(actual_pres)
                created_presentations.append(actual_pres)
            else:
                if datetime.strptime(actual_pres.get('modifiedTime'), '%Y-%m-%dT%H:%M:%S.%fZ') > db_pres.modified_time:
                    self.update(
                        Presentations,

                        obj_id=db_pres.id,

                        id=actual_pres.get('id'),
                        name=actual_pres.get('name'),
                        owner_id=user_id,
                        modified_time=actual_pres.get('modifiedTime')
                    )
                    synced_presentations.append(actual_pres)
                    modified_presentations.append(actual_pres)

        self.set_sync_query(user_id, (created_presentations, modified_presentations))

        return synced_presentations, (created_presentations, modified_presentations)

    def __sync_created_presentation(self, presentation, presentation_ratio, presentation_text, user_id, max_slides=100):
        for i in range(max_slides):
            try:
                with open(os.path.join(SERVER_ROOT,
                   f'presentation_processing/temp/{presentation.get("id")}/images/Слайд{i + 1}.png'), "rb") as image:
                    img_bytes = image.read()

                    self.create(
                        Slides,

                        pres_id=presentation.get('id'),
                        index=i,
                        thumbnail=img_bytes,
                        text=presentation_text[i],
                        ratio=presentation_ratio
                    )

            except FileNotFoundError:
                break
        self.lock_mutex.acquire()
        self.sync_query[user_id]['created'] = [pres for pres in self.sync_query[user_id]['created'] if
                                                pres.get('id') != presentation.get('id')]
        self.lock_mutex.release()

    def __sync_modified_presentation(self, presentation, presentation_ratio, presentation_text, user_id, max_slides=100):

        mdf_thumbnails = []

        for i in range(max_slides):
            try:
                with open(os.path.join(SERVER_ROOT,
                   f'presentation_processing/temp/{presentation.get("id")}/images/Слайд{i + 1}.png'), "rb") as image:
                    mdf_thumbnails.append(image.read())

            except FileNotFoundError:
                break

        db_slides = self.get_slides_index_asc(presentation.get('id'))
        db_thumbnails = [slide.thumbnail for slide in db_slides]

        upd_eq_count = [0] * len(mdf_thumbnails)

        for i, db_thumb in enumerate(db_thumbnails):
            pair = []
            for j, upd_thumb in enumerate(mdf_thumbnails):
                if utils.img_eq(db_thumb, upd_thumb):
                    pair.append((j, upd_thumb))

            # Совпадений нет - слайд удален
            if len(pair) == 0:
                self.delete(Slides, db_slides[i].id)

            # Одно совпадение - слайд остался в презентации
            # Если i == j - слайд остался на той же позиции
            # Иначе его переместили на позицию j
            elif len(pair) == 1:
                j, _ = pair[0]
                if i != j:
                    self.update(
                        Slides,
                        obj_id=db_slides[i].id,
                        index=j
                    )
                upd_eq_count[j] += 1

            # Больше одного совпадения - в презентации несколько копий одного слайда
            # TODO
            else:
                pass

        for i, occurrences in enumerate(upd_eq_count):
            # Если при сравнении со старой презентацией (из БД)
            # не было ни одного совпадения со слайдом из новой презентации, то
            # этот слайд был добавлен
            if occurrences == 0:
                self.create(
                    Slides,

                    pres_id=presentation.get('id'),
                    index=i,
                    thumbnail=mdf_thumbnails[i],
                    text=presentation_text[i],
                    ratio=presentation_ratio
                )
        self.lock_mutex.acquire()
        self.sync_query[user_id]['modified'] = [pres for pres in self.sync_query[user_id]['modified'] if pres.get('id') != presentation.get('id')]
        self.lock_mutex.release()


    def sync_presentation_slides(self, presentations, presentations_delta, presentations_ratio, presentations_text, user_id):
        created, modified = presentations_delta

        created_args = []
        modified_args = []
        for pres, ratio, text in zip(presentations, presentations_ratio, presentations_text):
            if pres in created:
                created_args.append((pres, ratio, text, user_id))
            elif pres in modified:
                modified_args.append((pres, ratio, text, user_id))

        self.pool.starmap(self.__sync_created_presentation, created_args)
        self.pool.starmap(self.__sync_modified_presentation, modified_args)

    def set_folder_mark(self, user_id, folder_id, value):
        folder = self.read(Folders, folder_id)
        if folder.owner_id == user_id:
            self.update(
                Folders,
                folder_id,
                mark=value
            )

    def get_slide_links(self, slide_id, user_id):
        links = self.findall(SlideLinks, SlideLinks.slide_id == slide_id)
        res = []
        for link in links:
            tag = self.find(Tags, Tags.id == link.tag_id, Tags.owner_id == user_id)
            res.append({
                'link_id': link.id,
                'slide_id': link.slide_id,
                'tag_id': tag.id,
                'tag_name': tag.name,
                'value': link.value
            })
        return res

    def create_slide_link(self, slide_id, tag_name, value, user_id):
        tag_created, tag = self.find_or_create(
            Tags,
            Tags.owner_id == user_id, Tags.name == tag_name,
            name=tag_name,
            owner_id=user_id
        )

        link_created, link = self.find_or_create(
            SlideLinks,
            SlideLinks.slide_id == slide_id, SlideLinks.tag_id == tag.id,
            slide_id=slide_id,
            tag_id=tag.id,
            value=value
        )

        if not link_created:
            self.update(SlideLinks, link.id, value=value)

    def remove_slide_link(self, slide_id, tag_name, user_id):
        tag = self.find(Tags, Tags.owner_id == user_id, Tags.name == tag_name)
        link = self.find(SlideLinks, SlideLinks.slide_id == slide_id, SlideLinks.tag_id == tag.id)
        if tag and link:
            self.delete(SlideLinks, link.id)
        slide_links_with_tag = self.findall(SlideLinks, SlideLinks.tag_id == tag.id)
        pres_links_with_tag = self.findall(PresentationLinks, PresentationLinks.tag_id == tag.id)
        if len(slide_links_with_tag) == len(pres_links_with_tag) == 0:
            self.delete(Tags, tag.id)

    def get_presentation_links(self, presentation_id, user_id):
        links = self.findall(PresentationLinks, PresentationLinks.pres_id == presentation_id)
        res = []
        for link in links:
            tag = self.find(Tags, Tags.id == link.tag_id, Tags.owner_id == user_id)
            res.append({
                'link_id': link.id,
                'presentation_id': link.pres_id,
                'tag_id': tag.id,
                'tag_name': tag.name,
                'value': link.value
            })
        return res

    def create_presentation_link(self, presentation_id, tag_name, value, user_id):
        tag_created, tag = self.find_or_create(
            Tags,
            Tags.owner_id == user_id, Tags.name == tag_name,
            name=tag_name,
            owner_id=user_id
        )

        link_created, link = self.find_or_create(
            PresentationLinks,
            PresentationLinks.pres_id == presentation_id, PresentationLinks.tag_id == tag.id,
            pres_id=presentation_id,
            tag_id=tag.id,
            value=value
        )

        if not link_created:
            self.update(PresentationLinks, link.id, value=value)

    def remove_presentation_link(self, presentation_id, tag_name, user_id):
        tag = self.find(Tags, Tags.owner_id == user_id, Tags.name == tag_name)
        link = self.find(PresentationLinks,
                         PresentationLinks.pres_id == presentation_id,
                         PresentationLinks.tag_id == tag.id)
        if tag and link:
            self.delete(PresentationLinks, link.id)
        slide_links_with_tag = self.findall(SlideLinks, SlideLinks.tag_id == tag.id)
        pres_links_with_tag = self.findall(PresentationLinks, PresentationLinks.tag_id == tag.id)
        if len(slide_links_with_tag) == len(pres_links_with_tag) == 0:
            self.delete(Tags, tag.id)

    def get_presentations_by_tag_query(self, query, user_id):
        tag_names = re.findall('[a-z]+[a-z0-9]*', query)
        tag_names = [tag.strip() for tag in tag_names if tag.strip() not in ['and', 'or', 'not']]

        links_and_tags = self.get_links_and_tags(PresentationLinks, user_id, tag_names)

        pres_tags_values = {}
        for link, tag in links_and_tags:
            if pres_tags_values.get(link.pres_id) is None:
                pres_tags_values[link.pres_id] = {key: False for key in tag_names}

            if link.value is not None:
                pres_tags_values[link.pres_id][tag.name] = link.value
            else:
                pres_tags_values[link.pres_id][tag.name] = True

        filtered_pres = []

        for pres_id in pres_tags_values.keys():
            eval_query = query
            for tag in pres_tags_values[pres_id].keys():
                eval_query = re.sub(rf"(^{tag}\s+)|( +{tag}\s+)|(\s+{tag}$)|({tag})",
                                    f" {str(pres_tags_values[pres_id][tag])} ", eval_query)
            try:
                if eval(eval_query):
                    filtered_pres.append(pres_id)
            except:
                filtered_pres = []

        found_presentations = self.findall(Presentations, Presentations.id.in_(filtered_pres))

        return [pres.json() for pres in found_presentations]

    def get_slides_by_tag_query(self, query, user_id):
        tag_names = re.findall('[a-z]+[a-z0-9]*', query)
        tag_names = [tag.strip() for tag in tag_names if tag.strip() not in ['and', 'or', 'not']]

        links_and_tags = self.get_links_and_tags(SlideLinks, user_id, tag_names)

        slide_tags_values = {}
        for link, tag in links_and_tags:
            if slide_tags_values.get(link.slide_id) is None:
                slide_tags_values[link.slide_id] = {key: False for key in tag_names}

            if link.value is not None:
                slide_tags_values[link.slide_id][tag.name] = link.value
            else:
                slide_tags_values[link.slide_id][tag.name] = True

        filtered_slides = []

        for slide_id in slide_tags_values.keys():
            eval_query = query
            for tag in slide_tags_values[slide_id].keys():
                eval_query = re.sub(rf"(^{tag}\s+)|( +{tag}\s+)|(\s+{tag}$)|({tag})",
                                    f" {str(slide_tags_values[slide_id][tag])} ", eval_query)
            try:
                if eval(eval_query):
                    filtered_slides.append(slide_id)
            except:
                filtered_slides = []

        found_slides = self.findall(Slides, Slides.id.in_(filtered_slides))

        return found_slides

    def get_user_tags_list(self, user_id):
        tags = self.findall(Tags, Tags.owner_id == user_id)
        presentations_tags = []
        slides_tags = []
        for tag in tags:
            presentation_link = self.find(PresentationLinks, PresentationLinks.tag_id == tag.id)
            if presentation_link is not None:
                presentations_tags.append(tag.json())

            slide_link = self.find(SlideLinks, SlideLinks.tag_id == tag.id)
            if slide_link is not None:
                slides_tags.append(tag.json())

        return presentations_tags, slides_tags

    def get_slides_by_filters(self, presentations, tag_query, text_phrase, ratio, user_id):

        presentation_ids = [pres.id for pres in presentations]
        slides = self.findall(Slides, Slides.pres_id.in_(presentation_ids))

        # Filter by tag query
        if tag_query != '':
            filtered_by_tag = self.get_slides_by_tag_query(tag_query, user_id)
            filtered_ids = [slide.id for slide in filtered_by_tag]
            slides = [slide for slide in slides if slide.id in filtered_ids]

        # Filter by text
        if text_phrase != '':
            slides = [slide for slide in slides if text_phrase.lower() in slide.text.lower()]

        # Filter by ratio
        if ratio != 'auto':
            if ratio == 'widescreen_16_to_9':
                search_ratio = Slides.Ratio.WIDESCREEN_16_TO_9
            elif ratio == 'standard_4_to_3':
                search_ratio = Slides.Ratio.STANDARD_4_TO_3
            else:
                raise AttributeError('Unknown slide ratio')
            slides = [slide for slide in slides if slide.ratio == search_ratio]

        res_slides = []

        for slide in slides:
            res_slide = slide.json()

            # Adding label
            presentation = self.find(Presentations, Presentations.id == slide.pres_id)
            label = f"{presentation.name} {slide.index + 1}"
            res_slide['label'] = label

            # Converting ratio
            if slide.ratio == Slides.Ratio.WIDESCREEN_16_TO_9:
                res_slide['ratio'] = 'widescreen_16_to_9'
            elif slide.ratio == Slides.Ratio.STANDARD_4_TO_3:
                res_slide['ratio'] = 'standard_4_to_3'

            res_slides.append(res_slide)

        return sorted(res_slides, key=lambda slide: (slide.get('pres_id'), slide.get('id')))

    def pres_sync_uploaded(self, pres, pres_text, pres_thumbs, ratio, slides_from, user_id):

        self.create(
            Presentations,
            id=pres.get('id'),
            name=pres.get('name'),
            owner_id=user_id,
            modified_time=pres.get('modifiedTime'),
        )

        for i, (text, thumb) in enumerate(zip(pres_text, pres_thumbs)):
            _, slide = self.create(
                Slides,
                pres_id=pres.get('id'),
                index=i,
                thumbnail=thumb,
                text=text,
                ratio=Slides.Ratio.WIDESCREEN_16_TO_9 if ratio == 'widescreen_16_to_9' else Slides.Ratio.STANDARD_4_TO_3
            )
            self.migrate_tags(slides_from[i], slide)

    def migrate_tags(self, slide_from, slide_to):
        slide_from_links = self.findall(SlideLinks, SlideLinks.slide_id == slide_from.id)
        for link in slide_from_links:
            self.find_or_create(
                SlideLinks,
                SlideLinks.slide_id == slide_to.id, SlideLinks.tag_id == link.tag_id,
                slide_id=slide_to.id,
                tag_id=link.tag_id,
                value=link.value
            )

    def set_sync_query(self, user_id, delta):
        self.sync_query[user_id] = {
            'created': delta[0],
            'modified': delta[1],
        }

    def get_sync_query(self, user_id):
        if user_id in self.sync_query:
            return self.sync_query[user_id]