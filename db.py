from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum

engine = create_engine('sqlite:///./tmp/test.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class Match(Base):
    __tablename__ = 'match'
    id = Column(Integer, primary_key=True, index=True)
    size = Column(Float, index=True)
    unit = Column(String(2), index=True)


class Demo(Base):
    __tablename__ = 'demo'
    id = Column(Integer, primary_key=True, index=True)
    size = Column(Integer, index=True)
    path = Column(String(255))


class DemoMatch(Base):
    __tablename__ = 'demo_match'
    id = Column(Integer, primary_key=True, index=True)
    demo_id = Column(Integer, ForeignKey('demo.id'), index=True)
    match_id = Column(Integer, ForeignKey('match.id'), index=True)
    type = Column(Integer, index=True)  # enum


class DemoMatchAssocType(Enum):
    size = 0


def init_db():
    Base.metadata.create_all(bind=engine)
