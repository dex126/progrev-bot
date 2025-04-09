from dataclasses import dataclass


@dataclass(slots=True)
class Practicum:
    first_practicum_date: str
    first_practicum_time: str
    first_practicum_link: str

    second_practicum_date: str
    second_practicum_time: str
    second_practicum_link: str

    promocode_text: str
    discount_percent: int
    upper_cost: int
