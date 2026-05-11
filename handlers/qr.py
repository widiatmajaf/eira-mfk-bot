import io
import qrcode
from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
from checklists import CHECKLISTS


async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate QR codes for all inspectable units."""
    q = update.callback_query
    await q.answer("⏳ Generating QR codes...")

    bot_info = await context.bot.get_me()
    bot_username = bot_info.username
    media_group = []

    for key, cl in CHECKLISTS.items():
        for unit in range(1, cl["units"] + 1):
            deep_link = f"https://t.me/{bot_username}?start={key}_{unit}"
            unit_label = f" #{unit}" if cl["units"] > 1 else ""
            caption = f"{cl['name']}{unit_label}"

            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(deep_link)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            buf.name = f"qr_{key}_{unit}.png"

            media_group.append(InputMediaPhoto(media=buf, caption=caption))

    # Telegram max 10 media per group — send in batches
    await q.edit_message_text("📱 Mengirim QR codes...")
    chat_id = update.effective_chat.id
    for i in range(0, len(media_group), 10):
        batch = media_group[i : i + 10]
        await context.bot.send_media_group(chat_id=chat_id, media=batch)

    await context.bot.send_message(chat_id=chat_id, text="✅ QR codes terkirim! Print dan tempel di setiap unit.\n\nKetik /start untuk menu.")
    return -1
