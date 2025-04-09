import asyncio

from nutrabot.practicum.repository.repository import PracticumRepository
from nutrabot.practicum.service.service import PracticumService
from nutrabot.settings import Settings
from nutrabot.telegram.service.service import TelegramService
from nutrabot.user.repository.repository import UserRepository
from nutrabot.user.service.service import UserService


async def main() -> None:
    user_service = UserService(
        repository=UserRepository(),
        admin_user_ids=Settings.TELEGRAM_ADMIN_IDS,
    )

    practicum_service = PracticumService(repository=PracticumRepository())

    telegram_service = TelegramService(
        user_service=user_service,
        practicum_service=practicum_service,
    )
    await telegram_service.start()


if __name__ == "__main__":
    asyncio.run(main=main())
