from typing import Any

from aiogram import BaseMiddleware, Bot
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.types import TelegramObject

from nutrabot.settings import Settings
from nutrabot.telegram.middleware.types_ import Handler


class IsChannelSubscriberMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Handler,
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:  # noqa: ANN401
        bot: Bot = data["bot"]
        chat_member = await bot.get_chat_member(
            chat_id=Settings.TELEGRAM_TARGET_CHANNEL_USERNAME,
            user_id=data["event_from_user"].id,
        )
        data["is_channel_subscriber"] = chat_member.status in (
            ChatMemberStatus.CREATOR,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.MEMBER,
        )
        return await handler(event, data)
