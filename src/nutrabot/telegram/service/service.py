from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.mongo import MongoStorage
from motor.motor_asyncio import AsyncIOMotorClient

from nutrabot.practicum.service.service import PracticumService
from nutrabot.reminder.service.service import ReminderService
from nutrabot.scheduler.service.service import SchedulerService
from nutrabot.settings import Settings
from nutrabot.telegram.middleware.admin import AdminAccessMiddleware
from nutrabot.telegram.middleware.subscriber import IsChannelSubscriberMiddleware
from nutrabot.telegram.reminder.service.service import ReminderTelegramService
from nutrabot.telegram.routers.admin.email.default_email.router import EmailRouter
from nutrabot.telegram.routers.admin.email.payment_email.router import (
    PaymentEmailRouter,
)
from nutrabot.telegram.routers.admin.numbers.router import NumbersRouter
from nutrabot.telegram.routers.admin.practicum.router import PracticumRouter
from nutrabot.telegram.routers.admin.templates.router import TemplatesRouter
from nutrabot.telegram.routers.link.router import LinkReaderRouter
from nutrabot.telegram.routers.secret.router import SecretRouter
from nutrabot.telegram.routers.start.router import StartCommandRouter
from nutrabot.telegram.routers.subscription.router import SubscriptionRouter
from nutrabot.telegram.routers.watched.router import WatchedRouter
from nutrabot.user.service.service import UserService


class TelegramService:
    __bot: Bot
    __dispatcher: Dispatcher

    def __init__(
        self,
        user_service: UserService,
        practicum_service: PracticumService,
    ) -> None:
        self.__bot = Bot(
            token=Settings.TELEGRAM_BOTAPI_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self.__dispatcher = Dispatcher(
            storage=MongoStorage(
                client=AsyncIOMotorClient(host=Settings.MONGO_CONNECTION_STRING),
            ),
        )
        self.__dispatcher.include_router(
            router=LinkReaderRouter(
                remind_service=ReminderService(
                    SchedulerService(
                        bot=self.__bot,
                        reminder_telegram_service=ReminderTelegramService(
                            bot=self.__bot,
                            user_service=user_service,
                        ),
                    ),
                    practicum_service=practicum_service,
                ),
                user_service=user_service,
                is_channel_subscriber_middleware=IsChannelSubscriberMiddleware(),
            ),
        )
        self.__dispatcher.include_router(
            router=SecretRouter(
                is_admin_middleware=AdminAccessMiddleware(user_service=user_service),
            ),
        )
        self.__dispatcher.include_router(
            router=StartCommandRouter(
                remind_service=ReminderService(
                    scheduler_service=SchedulerService(
                        bot=self.__bot,
                        reminder_telegram_service=ReminderTelegramService(
                            bot=self.__bot,
                            user_service=user_service,
                        ),
                    ),
                    practicum_service=practicum_service,
                ),
                is_channel_subscriber_middleware=IsChannelSubscriberMiddleware(),
                is_admin_middleware=AdminAccessMiddleware(user_service=user_service),
            ),
        )
        self.__dispatcher.include_router(
            router=SubscriptionRouter(
                user_service=user_service,
                remind_service=ReminderService(
                    scheduler_service=SchedulerService(
                        bot=self.__bot,
                        reminder_telegram_service=ReminderTelegramService(
                            bot=self.__bot,
                            user_service=user_service,
                        ),
                    ),
                    practicum_service=practicum_service,
                ),
                is_channel_subscriber_middleware=IsChannelSubscriberMiddleware(),
            ),
        )
        self.__dispatcher.include_router(
            router=WatchedRouter(
                bot=self.__bot,
                user_service=user_service,
                practicum_service=practicum_service,
            ),
        )
        self.__dispatcher.include_router(
            router=PracticumRouter(
                bot=self.__bot,
                practicum_service=practicum_service,
                is_admin_middleware=AdminAccessMiddleware(user_service=user_service),
            ),
        )
        self.__dispatcher.include_router(
            router=EmailRouter(
                bot=self.__bot,
                user_service=user_service,
                is_admin_middleware=AdminAccessMiddleware(user_service=user_service),
            ),
        )
        self.__dispatcher.include_router(
            router=TemplatesRouter(
                practicum_service=practicum_service,
                is_admin_middleware=AdminAccessMiddleware(user_service=user_service),
            ),
        )
        self.__dispatcher.include_router(
            router=NumbersRouter(
                user_service=user_service,
                is_admin_middleware=AdminAccessMiddleware(user_service=user_service),
            ),
        )
        self.__dispatcher.include_router(
            router=PaymentEmailRouter(
                bot=self.__bot,
                user_service=user_service,
                practicum_service=practicum_service,
                remind_service=ReminderService(
                    SchedulerService(
                        bot=self.__bot,
                        reminder_telegram_service=ReminderTelegramService(
                            bot=self.__bot,
                            user_service=user_service,
                        ),
                    ),
                    practicum_service=practicum_service,
                ),
                is_admin_middleware=AdminAccessMiddleware(user_service=user_service),
            ),
        )

    async def start(self) -> None:
        await self.__dispatcher.start_polling(self.__bot)
