from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from checklists import CHECKLISTS, DAILY_TYPES, WEEKLY_TYPES, MONTHLY_TYPES
from db import get_rekap


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start — check for QR deep link payload or show menu."""
    args = context.args
    if args and "_" in args[0]:
        # QR deep link: e.g. toilet_3, apar_2
        parts = args[0].rsplit("_", 1)
        if len(parts) == 2 and parts[0] in CHECKLISTS:
            insp_type, unit = parts[0], int(parts[1])
            context.user_data["type"] = insp_type
            context.user_data["unit"] = unit
            context.user_data["issues"] = set()
            from handlers.inspection import show_checklist
            return await show_checklist(update, context, from_start=True)
    return await show_menu(update, context)


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu with inspection categories."""
    buttons = []
    # Daily
    buttons.append([InlineKeyboardButton("━━ HARIAN ━━", callback_data="noop")])
    for t in DAILY_TYPES:
        cl = CHECKLISTS[t]
        buttons.append([InlineKeyboardButton(f"{cl['name']} ({cl['units']} unit)", callback_data=f"inspect_{t}")])
    # Weekly
    buttons.append([InlineKeyboardButton("━━ MINGGUAN ━━", callback_data="noop")])
    for t in WEEKLY_TYPES:
        cl = CHECKLISTS[t]
        label = f"{cl['name']}" if cl["units"] == 1 else f"{cl['name']} ({cl['units']} unit)"
        buttons.append([InlineKeyboardButton(label, callback_data=f"inspect_{t}")])
    # Monthly
    buttons.append([InlineKeyboardButton("━━ BULANAN ━━", callback_data="noop")])
    for t in MONTHLY_TYPES:
        cl = CHECKLISTS[t]
        buttons.append([InlineKeyboardButton(cl["name"], callback_data=f"inspect_{t}")])
    # Rekap & QR
    buttons.append([InlineKeyboardButton("━━━━━━━━━━", callback_data="noop")])
    buttons.append([
        InlineKeyboardButton("📊 Rekap", callback_data="rekap"),
        InlineKeyboardButton("📱 QR Codes", callback_data="gen_qr"),
    ])

    text = "🏥 *EIRA-MFK — Puskesmas Selogiri*\nPilih inspeksi yang akan dilakukan:"
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")
    return 0  # MENU state


async def rekap_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show today's inspection progress."""
    q = update.callback_query
    await q.answer()

    lines = ["📊 *REKAP INSPEKSI*\n"]

    for schedule, label in [("daily", "📅 HARIAN"), ("weekly", "📆 MINGGUAN"), ("monthly", "🗓️ BULANAN")]:
        data = get_rekap(schedule)
        lines.append(f"*{label}*")
        for key, info in data.items():
            check = "✅" if info["done"] >= info["total"] else f"⏳ {info['done']}/{info['total']}"
            lines.append(f"  {info['name']}: {check}")
        lines.append("")

    lines.append("Ketik /start untuk kembali ke menu.")
    await q.edit_message_text("\n".join(lines), parse_mode="Markdown")
    return -1  # End conversation


async def test_reminders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually trigger all reminders for testing."""
    from scheduler import daily_reminder, weekly_reminder, monthly_reminder_check
    await update.message.reply_text("🔄 Menjalankan simulasi semua reminder...")
    await daily_reminder(context)
    await weekly_reminder(context)
    await monthly_reminder_check(context)
    await update.message.reply_text("✅ Simulasi selesai.")
