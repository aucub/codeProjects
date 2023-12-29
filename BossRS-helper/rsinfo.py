from attr import attrib, attrs


@attrs
class RsInfo:
    url: str = attrib(default="")
    id: str = attrib(default="")
    name: str = attrib(default="")
    city: str = attrib(default="")
    address: str = attrib(default="")
    guide: str = attrib(default="")
    scale: str = attrib(default="")
    update_date: str = attrib(default="")
    salary: str = attrib(default="")
    experience: str = attrib(default="")
    degree: str = attrib(default="")
    company: str = attrib(default="")
    industry: str = attrib(default="")
    fund: str = attrib(default="")
    res: str = attrib(default="")
    boss: str = attrib(default="")
    boss_title: str = attrib(default="")
    active: str = attrib(default="")
    description: str = attrib(default="")
    communicate: str = attrib(default="")
    datetime: str = attrib(default="")
