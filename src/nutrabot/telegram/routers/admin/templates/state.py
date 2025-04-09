from dataclasses import asdict, dataclass

from aiogram.fsm.state import State, StatesGroup


class PromocodeState(StatesGroup):
    waiting_for_new_promocode = State()
    waiting_for_new_discount_percent = State()
    waiting_for_new_cost = State()

    waiting_for_confirmation = State()


@dataclass(slots=True, kw_only=True)
class PromocodeStateData:
    promocode: str | None = None
    discount_percent: int | None = None
    upper_cost: int | None = None

    def as_dict(self) -> dict:
        return asdict(self)
