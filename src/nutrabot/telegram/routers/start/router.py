from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from nutrabot.reminder.service.service import ReminderService
from nutrabot.settings import Settings
from nutrabot.telegram.middleware.admin import AdminAccessMiddleware
from nutrabot.telegram.middleware.subscriber import IsChannelSubscriberMiddleware
from nutrabot.telegram.routers.admin import keyboard as adm_keyboard
from nutrabot.telegram.routers.subscription import keyboard as sub_keyboard
from nutrabot.telegram.template.template import CaseType, Template


class StartCommandRouter(Router):
    __remind_service: ReminderService

    def __init__(
        self,
        remind_service: ReminderService,
        is_channel_subscriber_middleware: IsChannelSubscriberMiddleware,
        is_admin_middleware: AdminAccessMiddleware,
    ) -> None:
        super().__init__()
        self.__remind_service = remind_service
        self.message.middleware.register(is_admin_middleware)
        self.message.middleware.register(is_channel_subscriber_middleware)
        self.message.register(
            self.check_user_privileges,
            CommandStart(deep_link=False),
        )

    async def check_user_privileges(
        self,
        message: Message,
        is_admin: bool | None,
        is_channel_subscriber: bool | None,
    ) -> None:
        if not is_admin:
            await self.send_advertisement_message(
                message=message,
                is_channel_subscriber=is_channel_subscriber,
            )
            return

        await message.answer(
            "Админ-панель\n\n",
            reply_markup=adm_keyboard.get_admin_panel_keyboard(),
        )

    async def send_advertisement_message(
        self,
        message: Message,
        is_channel_subscriber: bool | None,
    ) -> None:
        if not is_channel_subscriber:
            keyboard = sub_keyboard.get_link_inline_keyboard(
                target_channel=Settings.TELEGRAM_TARGET_CHANNEL_USERNAME,
                button_text="Подписаться",
                case_type=CaseType.LANDING,
            )
            await message.answer(
                Template.SUBSCRIPTION_TEXT.render(case_type=CaseType.LANDING),
                reply_markup=keyboard,
            )
            return

        await message.answer(
            Template.MATERIALS_TEXT.render(case_type=CaseType.LANDING),
            disable_web_page_preview=True,
        )
        await self.__remind_service.set_practicum_1_remind(user_id=message.from_user.id)
