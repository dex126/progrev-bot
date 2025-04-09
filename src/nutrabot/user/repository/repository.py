from dataclasses import asdict

from motor.motor_asyncio import AsyncIOMotorClient

from nutrabot.settings import Settings
from nutrabot.user.core.user import User


class ModelNotFoundError(Exception): ...


class UserMapper:
    def add_info_about_user(self, entity: User) -> User:
        return asdict(entity)

    def extract_info_from_user(self, record: dict) -> User:
        return User(
            user_id=record["user_id"],
            is_intensive_registered=record["is_intensive_registered"],
            is_clicked_watched_button=record["is_clicked_watched_button"],
        )


class UserRepository:
    __mapper: UserMapper = UserMapper()
    __client: AsyncIOMotorClient = AsyncIOMotorClient(
        host=Settings.MONGO_CONNECTION_STRING,
        connect=False,
    )

    async def get_and_add(self, id_: str | None) -> dict:
        if id_ is None:
            return self.__client.nutrabot.users.find({})

        if record := await self.__client.nutrabot.users.find_one(
            filter={"user_id": id_},
        ):
            return self.__mapper.extract_info_from_user(record=record)

        return await self.add(
            user=User(
                user_id=id_,
                is_intensive_registered=False,
                is_clicked_watched_button=False,
            ),
        )

    async def add(self, user: User) -> User:
        await self.__client.nutrabot.users.insert_one(
            document=self.__mapper.add_info_about_user(entity=user),
        )
        return user

    async def update_intensive_register(
        self,
        user: User,
        intensive_register: bool | None,
        user_phone_number: str | None,
    ) -> User:
        await self.__client.nutrabot.users.update_one(
            {"user_id": user.user_id},
            {
                "$set": {
                    "is_intensive_registered": intensive_register,
                    "user_phone_number": user_phone_number,
                },
            },
        )

        return user

    async def update_is_watched_button(
        self,
        user: User,
        is_watched: bool | None,
    ) -> User:
        await self.__client.nutrabot.users.update_one(
            {"user_id": user.user_id},
            {"$set": {"is_clicked_watched_button": is_watched}},
        )

        return user
