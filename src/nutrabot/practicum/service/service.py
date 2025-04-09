from nutrabot.practicum.core.practicum import Practicum
from nutrabot.practicum.repository.repository import PracticumRepository
from nutrabot.practicum.service.schemas import PracticumAddSchema


class PracticumService:
    __repository: PracticumRepository

    def __init__(self, repository: PracticumRepository):
        self.__repository = repository

    async def get(self) -> Practicum:
        return await self.__repository.get()

    async def add(
        self,
        practicum: PracticumAddSchema,
    ) -> Practicum:
        return await self.__repository.add(
            practicum=Practicum(
                first_practicum_date=practicum.first_practicum_date,
                first_practicum_time=practicum.first_practicum_time,
                first_practicum_link=practicum.first_practicum_link,
                second_practicum_date=practicum.second_practicum_date,
                second_practicum_time=practicum.second_practicum_time,
                second_practicum_link=practicum.second_practicum_link,
                promocode_text=practicum.promocode_text,
                discount_percent=practicum.discount_percent,
                upper_cost=practicum.upper_cost,
            ),
        )
