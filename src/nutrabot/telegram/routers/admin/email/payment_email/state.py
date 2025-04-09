from aiogram.fsm.state import State, StatesGroup


class PaymentEmailState(StatesGroup):
    waiting_for_confirmation = State()
