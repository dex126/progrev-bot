from aiogram import Router, filters
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from nutrabot.reminder.service.service import ReminderService
from nutrabot.settings import Settings
from nutrabot.telegram.middleware.subscriber import IsChannelSubscriberMiddleware
from nutrabot.telegram.routers.link.state import PhoneNumberState
from nutrabot.telegram.routers.subscription import keyboard
from nutrabot.telegram.template.template import CaseType, Template
from nutrabot.user.service.service import UserAddSchema, UserService


class LinkReaderRouter(Router):
    __user_service: UserService
    __remind_service: ReminderService

    def __init__(
        self,
        user_service: UserService,
        remind_service: ReminderService,
        is_channel_subscriber_middleware: IsChannelSubscriberMiddleware,
    ) -> None:
        super().__init__()
        self.__remind_service = remind_service
        self.__user_service = user_service
        self.message.middleware.register(is_channel_subscriber_middleware)
        self.message.register(
            self.handle_start_link,
            filters.CommandStart(deep_link=True),
        )
        self.message.register(
            self.handle_phone_number,
            filters.StateFilter(PhoneNumberState.waiting_for_number),
        )

    async def handle_start_link(
        self,
        message: Message,
        is_channel_subscriber: bool | None,
        state: FSMContext,
    ) -> None:
        link_content = message.text.split()[1]

        if link_content == "register_from_intensive":
            await self.register_user_to_intensive(message=message, state=state)
            return

        if link_content == "video":
            await self.send_case_type_message(
                message=message,
                is_channel_subscriber=is_channel_subscriber,
                case_type=CaseType.VIDEO,
            )
            return

        if link_content == "landing":
            await self.send_case_type_message(
                message=message,
                is_channel_subscriber=is_channel_subscriber,
                case_type=CaseType.LANDING,
            )
            return

    async def register_user_to_intensive(
        self,
        message: Message,
        state: FSMContext,
    ) -> None:
        await message.answer(
            "Для регистрации на практикум введите номер в формате +7",
        )
        await state.set_state(PhoneNumberState.waiting_for_number)

    async def handle_phone_number(self, message: Message, state: FSMContext) -> None:
        correct_phone_len = 12

        user_info = await self.__user_service.get_and_add(
            id_=message.from_user.id,
            is_channel_subscriber=True,
        )

        if user_info.is_intensive_registered:
            await message.answer("Вы уже записаны на практикум")
            await state.clear()
            return

        if (
            (message.text[1:]).isdigit()
            and message.text.startswith("+7")
            and len(message.text) == correct_phone_len
        ):
            await self.__user_service.update_intensive_register(
                user=UserAddSchema(
                    id_=message.from_user.id,
                    is_intensive_registered=user_info.is_intensive_registered,
                    is_clicked_watched_button=user_info.is_clicked_watched_button,
                ),
                intensive_register=True,
                user_phone_number=message.text,
            )
            await message.answer("<b>Вы записаны на практикум!</b>")
            await self.__remind_service.set_practicum_1_remind(
                user_id=message.from_user.id,
            )
            await state.clear()

            return

        await message.answer("Введите номер телефона в формате +7")

    async def send_case_type_message(
        self,
        message: Message,
        is_channel_subscriber: bool | None,
        case_type: CaseType,
    ) -> None:
        if not is_channel_subscriber:
            keyboard_ = keyboard.get_link_inline_keyboard(
                target_channel=Settings.TELEGRAM_TARGET_CHANNEL_USERNAME,
                button_text="Подписаться",
                case_type=case_type,
            )

            await message.answer(
                Template.SUBSCRIPTION_TEXT.render(case_type=case_type),
                reply_markup=keyboard_,
                disable_web_page_preview=True,
            )
            return

        if case_type != CaseType.VIDEO:
            await message.answer(
                Template.MATERIALS_TEXT.render(case_type=case_type),
                disable_web_page_preview=True,
            )
            await self.__remind_service.set_landing_remind(user_id=message.from_user.id)
            return

        await message.answer_video(
            video=Settings.TELEGRAM_VIDEO_FILE_ID,
            caption=Template.MATERIALS_TEXT.render(case_type=case_type),
            reply_markup=keyboard.get_watched_button(case_type=case_type),
        )
        await self.__remind_service.set_video_remind(user_id=message.from_user.id)
