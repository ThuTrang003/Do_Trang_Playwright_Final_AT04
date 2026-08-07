from dataclasses import dataclass

@dataclass
class Profile:

    avatar: str | None = None
    name: str | None = None
    phone: str | None = None
    division: str | None = None
    ward: str | None = None
    address: str | None = None
    email: str | None = None
    old_password: str | None = None
    password: str | None = None
    confirm_password: str | None = None