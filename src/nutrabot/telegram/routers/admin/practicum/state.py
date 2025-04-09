from dataclasses import asdict, dataclass

from aiogram.fsm.state import State, StatesGroup


class PracticumAddState(StatesGroup):
    waiting_for_date_first_practicum = State()
    waiting_for_time_first_practicum = State()
    waiting_for_link_first_practicum = State()

    waiting_for_date_second_practicum = State()
    waiting_for_time_second_practicum = State()
    waiting_for_link_second_practicum = State()

    waiting_for_confirmation = State()


@dataclass(slots=True, kw_only=True)
class PracticumAddStateData:
    date_first_practicum: str | None = None
    time_first_practicum: str | None = None
    link_first_practicum: str | None = None

    date_second_practicum: str | None = None
    time_second_practicum: str | None = None
    link_second_practicum: str | None = None

    def as_dict(self) -> dict:
        return asdict(self)
