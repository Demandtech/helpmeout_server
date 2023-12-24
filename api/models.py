from sqlalchemy import Column, String, Integer, LargeBinary, Boolean, ForeignKey, Float
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from .database import Base


class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True, nullable=False)
    video_url = Column(String, nullable=False)
    video_path = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    blob_id = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    duration = Column(Float, nullable=False, server_default=text('0.0'))
    status = Column(String, nullable=False)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    email = Column(String, nullable=False, unique=True)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_verified = Column(Boolean, nullable=False, server_default=text('False'))
    verification_token = Column(String, unique=True)
    is_social_user = Column(Boolean, server_default=text('False'))
