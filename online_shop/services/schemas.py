from dataclasses import dataclass


@dataclass
class ProfileSchema:
    fullName: str
    email: str
    phone: str
    avatar: dict[str, str]


@dataclass
class CategoriesSchema:
    id: int
    title: str
    image: dict[str, str]
