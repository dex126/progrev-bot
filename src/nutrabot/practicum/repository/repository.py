from dataclasses import asdict

from motor.motor_asyncio import AsyncIOMotorClient

from nutrabot.practicum.core.practicum import Practicum
from nutrabot.settings import Settings


class ModelNotFoundError(Exception): ...


class PracticumMapper:
    def add_info_about_practicum(self, entity: Practicum) -> Practicum:
        return asdict(entity)

    def extract_info_about_practicum(self, record: dict) -> Practicum:
        return Practicum(
            first_practicum_date=record["first_practicum_date"],
            first_practicum_time=record["first_practicum_time"],
            first_practicum_link=record["first_practicum_link"],
            second_practicum_date=record["second_practicum_date"],
            second_practicum_time=record["second_practicum_time"],
            second_practicum_link=record["second_practicum_link"],
            promocode_text=record["promocode_text"],
            discount_percent=record["discount_percent"],
            upper_cost=record["upper_cost"],
        )


class PracticumRepository:
    __mapper: PracticumMapper = PracticumMapper()
    __client: AsyncIOMotorClient = AsyncIOMotorClient(
        host=Settings.MONGO_CONNECTION_STRING,
        connect=False,
    )

    async def get(self) -> dict:
        if record := await self.__client.nutrabot.practicums.find_one():
            return self.__mapper.extract_info_about_practicum(record=record)

        raise ModelNotFoundError

    async def add(self, practicum: Practicum) -> Practicum:
        await self.truncate()
        await self.__client.nutrabot.practicums.insert_one(
            document=self.__mapper.add_info_about_practicum(entity=practicum),
        )
        return practicum

    async def truncate(self) -> bool:
        await self.__client.nutrabot.practicums.drop()
        return True
