from enum import Enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EventType(str, Enum):
    EMERGENCY = "Emergency"
    SCHEDUELD_WORK = "Scheduled work"
    UNSCHEDUELD_WORK = "Unscheduled work"
    ADS = "Ads"


class EventTarget(str, Enum):
    ALL = "all"
    AREA = "area"
    HOUSE = "house"


class BaseEvent(BaseModel):
    title: Optional[str] = None
    type: Optional[EventType] = None
    description: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    house_id: Optional[int] = None
    area: Optional[str] = None
    target: Optional[EventTarget] = None

    def __eq__(self, obj):
        return (self.title == obj.title
                and self.type == obj.type
                and self.description == obj.description
                and self.start == obj.start
                and self.end == obj.end
                and self.house_id == obj.house_id
                and self.area == obj.area
                and self.target == obj.target)

    def __repr__(self):
        return "<Event title=%s, description=%s, start=%s, end=%s, house_id=%s, area=%s, target=%s"\
            % (self.title, self.description, self.start, self.end,
               self.house_id, self.area, self.target)

    def __str__(self):
        return f"""
{self.title} - {self.type}
{self.start} - {self.end}
{self.description}
{self.target}
"""


class EventCreate(BaseEvent):
    title: str
    type: EventType
    description: str
    start: datetime
    target: EventTarget


class EventUpdate(BaseEvent):
    id: int


class BaseInDBEvent(BaseEvent):
    id: Optional[int] = None

    class Config:
        orm_mode = True

    def __eq__(self, obj):
        return super().__eq__(obj) and self.id == obj.id

    def __repr__(self):
        return "<Event id=%s, title=%s, description=%s, start=%s, end=%s, house_id=%s, area=%s, target=%s"\
            % (self.id, self.title, self.description, self.start, self.end,
               self.house_id, self.area, self.target)


class Event(BaseInDBEvent):
    pass