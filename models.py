from sqlalchemy import Column, String, Enum, Integer, Table, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base
from schemas import ResetIntervalDefinition, QuotaScope


class QuotaDefinition(Base):
    __tablename__ = 'quota_definition'
    __table_args__ = (UniqueConstraint('scope', 'feature', name='uq_scope_feature'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=True)
    description = Column(JSON, nullable=False)
    reset_interval = Column(Enum(ResetIntervalDefinition), nullable=True)
    scope = Column(Enum(QuotaScope), nullable=False)
    feature = Column(String, nullable=True)

    class Config:
        from_attributes = True


class Quota(Base):
    __tablename__ = 'quota'
    # TODO: Null values are interpreted as distinct values, see https://www.sqlite.org/nulls.html
    __table_args__ = (UniqueConstraint('scope', 'feature', 'user_id', 'course_id',  name='uq_key'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    limit = Column(Integer, nullable=False)
    used = Column(Integer, nullable=True)
    type = Column(String, nullable=True)  # TODO: Do we need type because defined in quota definition
    scope = Column(Enum(QuotaScope), nullable=False)  # TODO: Do we need scope because defined in quota definition
    feature = Column(String, nullable=True)  # TODO: Do we need feature because defined in quota definition
    user_id = Column(String, nullable=True)
    course_id = Column(String, nullable=True)
    quota_definition_id = Column(Integer, ForeignKey('quota_definition.id'), nullable=False)

    quota_definition = relationship('QuotaDefinition', backref='quota')

    class Config:
        from_attributes = True
