from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum

engine = create_engine('sqlite:///./tmp/test.db')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class Match:
    id = Column(Integer, primary_key=True, index=True)
    teamA = Column(String(255), index=True)
    teamB = Column(String(255), index=True)
    game_mode = Column(String(255), index=True)
    game = Column(String(255), index=True)
    map = Column(String(255), index=True)


class MatchPage(Base, Match):
    __tablename__ = 'match'
    size = Column(Float, index=True)
    unit = Column(String(2), index=True)


class Demo(Base, Match):
    __tablename__ = 'demo'
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
    gm_g_size = 1
    manual = 2


def init_db():
    Base.metadata.create_all(bind=engine)
