from nutrabot.user.core.user import User
from nutrabot.user.repository.repository import UserRepository
from nutrabot.user.service.schemas import UserAddSchema


class UserIsNotSubscriberError(Exception): ...  # ваще не нужно


class UserService:  # надо переделывать
    __admin_user_ids: list[int]
    __repository: UserRepository

    def __init__(self, repository: UserRepository, admin_user_ids: list[int]):
        self.__repository = repository
        self.__admin_user_ids = admin_user_ids

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.__admin_user_ids

    async def get_and_add(
        self,
        id_: int | None = None,
        is_channel_subscriber: bool | None = None,
    ) -> User:
        if is_channel_subscriber is not None and not is_channel_subscriber:
            raise UserIsNotSubscriberError

        return await self.__repository.get_and_add(id_=id_)

    async def add(self, user: UserAddSchema) -> User:
        return await self.__repository.add(
            user=User(
                user_id=user.id_,
                is_intensive_registered=user.is_intensive_registered,
                is_clicked_watched_button=user.is_clicked_watched_button,
            ),
        )

    async def update_intensive_register(  # апдейты кринж
        self,
        user: UserAddSchema,
        intensive_register: bool | None,
        user_phone_number: str,
    ) -> User:
        return await self.__repository.update_intensive_register(
            user=User(
                user_id=user.id_,
                is_intensive_registered=user.is_intensive_registered,
                is_clicked_watched_button=user.is_clicked_watched_button,
            ),
            intensive_register=intensive_register,
            user_phone_number=user_phone_number,
        )

    async def update_is_watched_button(
        self,
        user: UserAddSchema,
        is_watched: bool | None,
    ) -> User:
        return await self.__repository.update_is_watched_button(
            user=User(
                user_id=user.id_,
                is_intensive_registered=user.is_intensive_registered,
                is_clicked_watched_button=user.is_clicked_watched_button,
            ),
            is_watched=is_watched,
        )
