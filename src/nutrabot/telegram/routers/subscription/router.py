from aiogram import Router, types

from nutrabot.reminder.service.service import ReminderService
from nutrabot.telegram.middleware.subscriber import IsChannelSubscriberMiddleware
from nutrabot.telegram.routers.subscription import keyboard
from nutrabot.telegram.routers.subscription.keyboard import SubscriptionCallbackInfo
from nutrabot.telegram.template.template import CaseType, Template
from nutrabot.user.service.service import UserService


class SubscriptionRouter(Router):
    __user_service: UserService
    __remind_service: ReminderService

    def __init__(
        self,
        user_service: UserService,
        remind_service: ReminderService,
        is_channel_subscriber_middleware: IsChannelSubscriberMiddleware,
    ) -> None:
        super().__init__()
        self.__user_service = user_service
        self.__remind_service = remind_service
        self.callback_query.middleware.register(is_channel_subscriber_middleware)
        self.callback_query.register(
            self.check_subscribe_query,
        )
        self.callback_query.filter(SubscriptionCallbackInfo.filter())

    async def check_subscribe_query(
        self,
        query: types.CallbackQuery,
        callback_data: SubscriptionCallbackInfo,
        is_channel_subscriber: bool | None,
    ) -> None:
        await query.answer()

        if not is_channel_subscriber:
            await query.message.answer(
                "<b>Не вижу твоей подписки :(</b>\n"
                'Подпишись и нажми кнопку "готово", чтобы забрать бонус',
            )
            return

        await query.message.delete()

        await self.__user_service.get_and_add(
            id_=query.message.from_user.id,
            is_channel_subscriber=None,
        )

        if callback_data.case_type != CaseType.VIDEO:
            await query.message.answer(
                Template.MATERIALS_TEXT.render(case_type=callback_data.case_type),
                disable_web_page_preview=True,
            )
            await self.__remind_service.set_landing_remind(
                user_id=query.message.chat.id,
            )
            return

        await query.message.answer_video(
            video=types.FSInputFile("video.mp4"),
            caption=Template.MATERIALS_TEXT.render(case_type=callback_data.case_type),
            reply_markup=keyboard.get_watched_button(case_type=callback_data.case_type),
        )
        await self.__remind_service.set_video_remind(user_id=query.message.chat.id)
