import sys
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
from config import BOT_TOKEN, WEBHOOK_URL, PORT
from handlers.menu import start, show_menu, rekap_handler, test_reminders_handler
from handlers.inspection import (
    select_type, select_unit, show_checklist,
    toggle_item, checklist_done,
    receive_photo, skip_photo,
    receive_notes, skip_notes,
    MENU, SELECT_UNIT, CHECKLIST, PHOTO, NOTES,
)
from handlers.qr import generate_qr
from scheduler import setup_scheduler

# -- Build conversation handler --
conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("start", start),
        CommandHandler("test_reminders", test_reminders_handler),
    ],
    states={
        MENU: [
            CallbackQueryHandler(select_type, pattern=r"^inspect_"),
            CallbackQueryHandler(rekap_handler, pattern=r"^rekap$"),
            CallbackQueryHandler(generate_qr, pattern=r"^gen_qr$"),
            CallbackQueryHandler(lambda u, c: u.callback_query.answer(), pattern=r"^noop$"),
        ],
        SELECT_UNIT: [
            CallbackQueryHandler(select_unit, pattern=r"^unit_\d+$"),
            CallbackQueryHandler(show_menu, pattern=r"^back_menu$"),
        ],
        CHECKLIST: [
            CallbackQueryHandler(toggle_item, pattern=r"^t_\d+$"),
            CallbackQueryHandler(checklist_done, pattern=r"^checklist_done$"),
            CallbackQueryHandler(show_menu, pattern=r"^back_menu$"),
        ],
        PHOTO: [
            MessageHandler(filters.PHOTO, receive_photo),
            CallbackQueryHandler(skip_photo, pattern=r"^skip_photo$"),
        ],
        NOTES: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_notes),
            CallbackQueryHandler(skip_notes, pattern=r"^skip_notes$"),
        ],
    },
    fallbacks=[CommandHandler("start", start)],
    allow_reentry=True,
)


async def run_webhook():
    """Run bot in webhook mode for production (Render.com)."""
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(conv_handler)

    await app.initialize()
    await app.start()
    setup_scheduler(app.job_queue)

    # Set Telegram webhook
    webhook_path = "/webhook"
    full_url = f"{WEBHOOK_URL}{webhook_path}"
    await app.bot.set_webhook(full_url)
    print(f"Webhook set: {full_url}")

    # aiohttp web server
    async def handle_webhook(request):
        data = await request.json()
        update = Update.de_json(data, app.bot)
        await app.process_update(update)
        return web.Response(status=200)

    async def health(request):
        return web.Response(text="OK")

    webapp = web.Application()
    webapp.router.add_post(webhook_path, handle_webhook)
    webapp.router.add_get("/health", health)
    webapp.router.add_get("/", health)

    runner = web.AppRunner(webapp)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Server running on port {PORT}")

    # Keep alive
    await asyncio.Event().wait()


def run_polling():
    """Run bot in polling mode for local development."""
    print("Initializing Application...")
    app = Application.builder().token(BOT_TOKEN).build()
    print("Adding handlers...")
    app.add_handler(conv_handler)
    print("Setting up scheduler...")
    setup_scheduler(app.job_queue)
    print("Bot starting polling...")
    app.run_polling(drop_pending_updates=True)


def main():
    if "--local" in sys.argv:
        run_polling()
    else:
        asyncio.run(run_webhook())


if __name__ == "__main__":
    main()
