from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PracticumAddSchema:
    first_practicum_date: str
    first_practicum_time: str
    first_practicum_link: str

    second_practicum_date: str
    second_practicum_time: str
    second_practicum_link: str

    promocode_text: str | None = None
    discount_percent: int | None = None
    upper_cost: int | None = None
