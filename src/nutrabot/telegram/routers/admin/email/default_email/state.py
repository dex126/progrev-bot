from dataclasses import asdict, dataclass

from aiogram.fsm.state import State, StatesGroup


class EmailState(StatesGroup):
    waiting_for_email_text = State()
    waiting_for_confirmation = State()


@dataclass(slots=True, kw_only=True)
class EmailStateData:
    email_text: str

    def as_dict(self) -> dict:
        return asdict(self)
