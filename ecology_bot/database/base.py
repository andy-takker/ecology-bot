import re

from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class Base:
    __name__: str
    __verbose_name__: str
    __verbose_name_plural__: str
    __admin_endpoint__: str

    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        name_list = re.findall(r"[A-Z][a-z\d]*", cls.__name__)
        return "_".join(name_list).lower()

    def update(self, data: dict):
        for field in self.__table__.columns:
            if field.name in data:
                setattr(self, field.name, data[field.name])
