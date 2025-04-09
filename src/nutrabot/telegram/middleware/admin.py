from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from nutrabot.telegram.middleware.types_ import Handler
from nutrabot.user.service.service import UserService


class AdminAccessMiddleware(BaseMiddleware):
    __user_service: UserService

    def __init__(self, user_service: UserService):
        self.__user_service = user_service

    async def __call__(
        self,
        handler: Handler,
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:  # noqa: ANN401
        data["is_admin"] = self.__user_service.is_admin(
            user_id=str(data["event_from_user"].id),
        )

        return await handler(event, data)
