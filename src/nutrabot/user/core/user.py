from dataclasses import dataclass


@dataclass(slots=True)
class User:
    user_id: int
    user_phone_number: str | None = None
    is_intensive_registered: bool | None = None
    is_clicked_watched_button: bool | None = None
