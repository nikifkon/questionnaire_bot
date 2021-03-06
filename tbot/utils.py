from contextlib import contextmanager
from operator import attrgetter
from typing import List, Optional, Tuple

from babel.support import LazyProxy

from tbot import schemas
from tbot.db import Session
from tbot.models import Event, House, User


def concat_lazy(*args, sep="", enable_cache=False):
    return LazyProxy(concat, *args, sep=sep, enable_cache=enable_cache)


def concat(*args, sep=""):
    res = sep.join([str(arg) for arg in args])
    return res


def deep_setter(obj, aliases: list, value):
    if not isinstance(aliases, list):
        raise TypeError("Alias must be a list")
    if len(aliases) < 1:
        raise ValueError("Alias list must be longer then 0")
    if any(["." in el for el in aliases]):
        raise ValueError("Elements can not contain dots")

    if len(aliases) > 1:
        last = aliases.pop()
        dot_view = '.'.join(aliases)
        get_penult = attrgetter(dot_view)
        setattr(get_penult(obj), last, value)
    else:
        setattr(obj, aliases[0], value)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:  # noqa E722
        session.rollback()
        raise
    finally:
        session.close()


def save_or_update_user(user: schemas.User) -> None:
    with session_scope() as session:
        if session.query(User).filter_by(id=user.id).first() is None:
            save_user(user)
        else:
            update_user(user)


def save_user(user: schemas.User) -> None:
    with session_scope() as session:
        obj = User.from_schema(user)
        session.add(obj)


def update_user(user: schemas.User) -> None:
    with session_scope() as session:
        obj = session.query(User).filter_by(id=user.id).first()
        obj.update_from_schema(user)
        session.add(obj)


def get_user(user_id: int) -> Optional[schemas.User]:
    with session_scope() as session:
        user = session.query(User).filter_by(id=user_id).first()
        if user is None:
            return None
        return schemas.User.from_orm(user)


def delete_user_by_id(user_id: int) -> bool:
    with session_scope() as session:
        user = session.query(User).filter_by(id=user_id).first()
        if user is None:
            return False
        session.delete(user)
        return True


def list_relevant_users_for_event(event: Event = None) -> List[schemas.User]:
    target = schemas.EventTarget.ALL
    if event:
        target = event.target

    with session_scope() as session:
        users = []
        if target == schemas.EventTarget.ALL:
            users = session.query(User).all()

        elif target == schemas.EventTarget.AREA:
            for house in session.query(House).filter_by(
                    area=event.area):
                users.extend(house.users)  # TODO: use sql query

        elif target == schemas.EventTarget.HOUSE:
            for house in session.query(House).filter_by(
                    id=event.house_id):
                users.extend(house.users)  # TODO: use sql query

        return [schemas.User.from_orm(user) for user in users]


def list_user() -> Tuple[List[schemas.House], int]:
    with session_scope() as session:
        return [schemas.User.from_orm(user)
                for user in session.query(User).all()], 200


def list_house() -> Tuple[List[schemas.House], int]:
    with session_scope() as session:
        return [schemas.House.from_orm(house)
                for house in session.query(House).all()], 200


def list_event() -> Tuple[List[schemas.Event], int]:
    with session_scope() as session:
        return [schemas.Event.from_orm(event)
                for event in session.query(Event).all()], 200


def create_event(event: schemas.EventCreate
                 ) -> Tuple[Optional[schemas.Event], int]:
    with session_scope() as session:
        obj = Event(**event.dict())
        session.add(obj)
        session.flush()
        data = schemas.Event.from_orm(obj).dict()
        return data, 201


def update_event(event: schemas.EventUpdate
                 ) -> Tuple[Optional[schemas.Event], int]:
    with session_scope() as session:
        obj = session.query(Event).filter_by(id=event.id).first()
        if obj is None:
            return {}, 404

        for key, value in event.dict().items():
            if value is not None:
                setattr(obj, key, value)
        data = schemas.Event.from_orm(obj).dict()
        return data, 200


def delete_event(id: int) -> int:
    with session_scope() as session:
        obj = session.query(Event).filter_by(id=id).first()
        if obj is None:
            return 404
        session.delete(obj)
        return 204
