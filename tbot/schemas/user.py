from enum import Enum
from typing import Optional

from pydantic import BaseModel

from .house import BaseHouse, BaseInDBHouse, House

user_aliases = {
    "Username": ["name"],
    "Phone number": ["phone"],
    "Flat number": ["flat"],
    "Language": ["lang"],
    "Street": ["house", "street"],
    "Area": ["house", "area", "name"],
    "House number": ["house", "number"],
}


class Lang(Enum):
    RU = "ru"
    EN = "en"


def get_valid_user_fields():
    return ", ".join(user_aliases.keys())


class BaseUser(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    house: Optional[BaseHouse] = None
    flat: Optional[int] = None
    lang: Optional[str] = Lang.RU.value

    def __eq__(self, obj):
        return (self.name == obj.name and self.phone == obj.phone and self.house == obj.house and self.flat == obj.flat)

    def __repr__(self):
        return "<User name='%s', phone='%s', house=%s, flat=%s, language=%s>"\
            % (self.name, self.phone, repr(self.house), self.flat, self.lang)

    def __str__(self):
        result = ""
        for key, alias in user_aliases.items():
            import operator
            getter = operator.attrgetter(".".join(alias))
            value = getter(self)
            result += "\n<i>{key}</i>: <b>{value}</b>".format(key=key, value=value)
        return result


class BaseInDBUser(BaseUser):
    id: Optional[int] = None
    house: Optional[BaseInDBHouse] = None

    class Config:
        orm_mode = True

    def to_base(self):
        return BaseUser(**self.dict())

    def __repr__(self):
        return "<User id=%s name='%s', phone='%s', house=%s, flat=%s>"\
            % (self.id, self.name, self.phone, repr(self.house), self.flat)

    def __eq__(self, obj):
        return super().__eq__(obj) and self.id == obj.id


# return via api
class User(BaseInDBUser):
    house: Optional[House] = None
