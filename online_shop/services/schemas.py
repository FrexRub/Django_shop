from dataclasses import dataclass


@dataclass
class ProfileSchema:
    fullName: str
    email: str
    phone: str
    avatar: dict[str, str]
