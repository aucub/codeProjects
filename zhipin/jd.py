from attr import attrib, attrs
from datetime import date, datetime


@attrs
class JD:
    id: str = attrib(default=None)
    url: str = attrib(default="")
    name: str = attrib(default="")
    city: str = attrib(default="")
    address: str = attrib(default="")
    guide: str = attrib(default="")
    scale: str = attrib(default="")
    update_date: date = attrib(default=None)
    salary: str = attrib(default="")
    experience: str = attrib(default="")
    degree: str = attrib(default="")
    company: str = attrib(default="")
    industry: str = attrib(default="")
    fund: str = attrib(default="")
    res: date = attrib(default=None)
    boss: str = attrib(default="")
    boss_title: str = attrib(default="")
    active: str = attrib(default="")
    description: str = attrib(default="")
    communicated: bool = attrib(default=False)
    checked_date: datetime = attrib(default=None)
