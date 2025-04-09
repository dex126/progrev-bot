from dataclasses import asdict, dataclass

from aiogram.fsm.state import State, StatesGroup


class PhoneNumberState(StatesGroup):
    waiting_for_number = State()


@dataclass(slots=True, kw_only=True)
class PhoneNumberStateData:
    number: str

    def as_dict(self) -> dict:
        return asdict(self)
