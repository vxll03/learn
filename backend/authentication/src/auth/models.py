from datetime import date, datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.db import Base


class Role(PyEnum):
    USER = 'User'
    ADMIN = 'Admin'


class UserGroup(Base):
    __tablename__ = 'users_groups'
    user: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    group: Mapped[int] = mapped_column(ForeignKey('groups.id'), primary_key=True)


class Group(Base):
    __tablename__ = 'groups'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    users: Mapped[list['User']] = relationship('User', secondary='users_groups', back_populates='groups')


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(String(40), unique=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))

    role: Mapped['Role'] = mapped_column(Enum(Role), default=Role.USER)
    groups: Mapped[list['Group']] = relationship('Group', secondary='users_groups', back_populates='users')

    latest_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    latest_password_change: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)