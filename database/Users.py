from sqlalchemy import Column, Integer, String, Table, MetaData

from main import db_handler


class User(db_handler.Base):
    id = Column('id', String, primary_key=True)
    name = Column('name', String, nullable=False)
    refresh_token = Column('refresh_token', String, nullable=False)
    app_folder_id = Column('app_folder_id', String, nullable=False)

    __table__ = Table(
        'users', MetaData(),
        id,
        name,
        refresh_token,
        app_folder_id,
    )
