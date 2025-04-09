from datetime import datetime, timedelta

from nutrabot.practicum.core.practicum import Practicum
from nutrabot.practicum.service.service import PracticumService
from nutrabot.scheduler.service.service import SchedulerService
from nutrabot.telegram.reminder import keyboard
from nutrabot.telegram.template.template import RemindType, Template


class ReminderService:
    __scheduler_service: SchedulerService
    __practicum_service: PracticumService

    def __init__(
        self,
        scheduler_service: SchedulerService,
        practicum_service: PracticumService,
    ) -> None:
        self.__scheduler_service = scheduler_service
        self.__practicum_service = practicum_service

    async def get_practicum_data_with_datetime(
        self,
    ) -> tuple[Practicum, datetime, datetime]:
        practicums_data = await self.__practicum_service.get()

        first_practicum_datetime = datetime.strptime(
            f"{practicums_data.first_practicum_date} "
            f"{practicums_data.first_practicum_time}",
            "%Y-%m-%d %H:%M:%S",
        )
        second_practicum_datetime = datetime.strptime(
            f"{practicums_data.second_practicum_date} "
            f"{practicums_data.second_practicum_time}",
            "%Y-%m-%d %H:%M:%S",
        )

        return practicums_data, first_practicum_datetime, second_practicum_datetime

    async def set_landing_remind(self, user_id: int) -> None:
        await self.__scheduler_service.set_remind_message(
            user_id=user_id,
            run_date=(datetime.now() + timedelta(hours=1)),
            text=Template.REMIND_TEXT.render(type_=RemindType.LANDING_1H),
            remind_type=RemindType.LANDING_1H,
        )
        await self.__scheduler_service.set_remind_message(
            user_id=user_id,
            run_date=(datetime.now() + timedelta(hours=3)),
            text=Template.REMIND_TEXT.render(type_=RemindType.LANDING_3H),
            remind_type=RemindType.LANDING_3H,
            markup=await keyboard.get_sign_keyboard(
                bot=self.__scheduler_service.return_bot_init(),
            ),
        )

    async def set_video_remind(self, user_id: int) -> None:
        await self.__scheduler_service.set_remind_message(
            user_id=user_id,
            run_date=(datetime.now() + timedelta(hours=1)),
            text=Template.REMIND_TEXT.render(type_=RemindType.VIDEO_1H),
            remind_type=RemindType.VIDEO_1H,
            markup=await keyboard.get_sign_keyboard(
                bot=self.__scheduler_service.return_bot_init(),
            ),
        )

    async def set_practicum_1_remind(self, user_id: int) -> None:
        practicum_data = await self.get_practicum_data_with_datetime()

        await self.__scheduler_service.set_remind_message(
            user_id=user_id,
            run_date=(practicum_data[1] - timedelta(days=1)),
            text=Template.REMIND_TEXT.render(
                type_=RemindType.PRACTICUM_1_1D,
                first_practicum_time=practicum_data[0].first_practicum_time[:-3],
            ),
            remind_type=RemindType.PRACTICUM_1_1D,
        )
        await self.__scheduler_service.set_remind_message(
            user_id=user_id,
            run_date=(practicum_data[1] - timedelta(hours=1)),
            text=Template.REMIND_TEXT.render(
                type_=RemindType.PRACTICUM_1_1H,
                first_practicum_link=practicum_data[0].first_practicum_link,
            ),
            remind_type=RemindType.PRACTICUM_1_1H,
        )
        await self.__scheduler_service.set_remind_message(
            user_id=user_id,
            run_date=(practicum_data[1] - timedelta(minutes=5)),
            text=Template.REMIND_TEXT.render(
                type_=RemindType.PRACTICUM_1_5M,
                first_practicum_link=practicum_data[0].first_practicum_link,
            ),
            remind_type=RemindType.PRACTICUM_1_5M,
        )

        await self.set_practicum_2_remind(
            user_id=user_id,
            practicum_data=practicum_data,
        )

    async def set_practicum_2_remind(
        self,
        user_id: int,
        practicum_data: tuple[Practicum, datetime, datetime],
    ) -> None:
        await self.__scheduler_service.set_remind_message(
            user_id=user_id,
            run_date=(practicum_data[2] - timedelta(days=1)),
            text=Template.REMIND_TEXT.render(type_=RemindType.PRACTICUM_2_1D),
            remind_type=RemindType.PRACTICUM_2_1D,
        )
        await self.__scheduler_service.set_remind_message(
            user_id=user_id,
            run_date=(practicum_data[2] - timedelta(hours=1)),
            text=Template.REMIND_TEXT.render(
                type_=RemindType.PRACTICUM_2_1H,
                second_practicum_link=practicum_data[0].second_practicum_link,
            ),
            remind_type=RemindType.PRACTICUM_2_1H,
        )
        await self.__scheduler_service.set_remind_message(
            user_id=user_id,
            run_date=(practicum_data[2] - timedelta(minutes=5)),
            text=Template.REMIND_TEXT.render(
                type_=RemindType.PRACTICUM_2_5M,
                second_practicum_link=practicum_data[0].second_practicum_link,
            ),
            remind_type=RemindType.PRACTICUM_2_5M,
        )

    async def set_practicum_payment_remind(
        self,
        user_id: int,
    ) -> None:
        practicum_data = await self.get_practicum_data_with_datetime()
        nightmare = f"{int(practicum_data[0].upper_cost):,}".replace(",", " ")

        await self.__scheduler_service.set_remind_message(
            user_id=user_id,
            run_date=(datetime.now() + timedelta(seconds=1)),
            text=Template.REMIND_TEXT.render(
                type_=RemindType.PRACTICUM_PAYMENT_1D,
                discount_percent=practicum_data[0].discount_percent,
                promocode=practicum_data[0].promocode_text,
            ),
            remind_type=RemindType.PRACTICUM_PAYMENT_1D,
        )

        await self.__scheduler_service.set_remind_message(
            user_id=user_id,
            run_date=(datetime.now() + timedelta(seconds=2)),
            text=Template.REMIND_TEXT.render(
                type_=RemindType.PRACTICUM_PAYMENT_2D,
                discount_percent=practicum_data[0].discount_percent,
                promocode=practicum_data[0].promocode_text,
                upper_payment_cost=nightmare,
            ),
            remind_type=RemindType.PRACTICUM_PAYMENT_2D,
        )
