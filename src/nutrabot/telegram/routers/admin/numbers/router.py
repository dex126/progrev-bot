import secrets
from pathlib import Path

import aiofiles
from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest

from nutrabot.telegram.middleware.admin import AdminAccessMiddleware
from nutrabot.user.service.service import UserService


class NumbersRouter(Router):
    __user_service: UserService

    def __init__(
        self,
        user_service: UserService,
        is_admin_middleware: AdminAccessMiddleware,
    ) -> None:
        super().__init__()
        self.__user_service = user_service
        self.callback_query.register(
            self.handle_numbers_command,
            F.data.in_("numbers"),
        )

        self.callback_query.middleware.register(is_admin_middleware)

    async def handle_numbers_command(
        self,
        query: types.CallbackQuery,
    ) -> None:
        await query.answer()
        numbers_file = await self.give_numbers_file()

        try:
            await query.message.answer_document(
                document=types.FSInputFile(numbers_file),
            )
        except TelegramBadRequest:
            await query.message.answer("Нет номеров в базе")

        Path.unlink(numbers_file)

    async def give_numbers_file(self) -> bytes:
        users = await self.__user_service.get_and_add()

        async with aiofiles.open(f"{secrets.token_hex(3)}.txt", "w") as file:
            async for user in users:
                if user["user_phone_number"] is not None:
                    await file.write(user["user_phone_number"] + "\n")

        return file.name
