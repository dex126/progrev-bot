from aiogram import F, Router, types

from nutrabot.telegram.middleware.admin import AdminAccessMiddleware


class SecretRouter(Router):
    def __init__(self, is_admin_middleware: AdminAccessMiddleware) -> None:
        super().__init__()
        self.message.middleware.register(is_admin_middleware)
        self.message.register(
            self.send_video,
            F.text.in_("ведос)))"),
        )

    async def send_video(self, message: types.Message) -> None:
        video = await message.answer_video(types.FSInputFile("video.mp4"))
        await message.answer(f"<code>{video.video.file_id}</code>")
