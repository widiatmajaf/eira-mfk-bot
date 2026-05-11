from datetime import datetime, timedelta, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from checklists import CHECKLISTS
from db import save_inspection
from drive import upload_photo

WIB = timezone(timedelta(hours=7))

# Conversation states (shared with main)
MENU, SELECT_UNIT, CHECKLIST, PHOTO, NOTES = range(5)


async def select_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User selected an inspection type from menu."""
    q = update.callback_query
    await q.answer()
    insp_type = q.data.replace("inspect_", "")
    if insp_type not in CHECKLISTS:
        return MENU

    context.user_data["type"] = insp_type
    context.user_data["issues"] = set()
    cl = CHECKLISTS[insp_type]

    if cl["units"] == 1:
        context.user_data["unit"] = 1
        return await show_checklist(update, context)
    else:
        # Show unit selection
        buttons = []
        row = []
        for i in range(1, cl["units"] + 1):
            row.append(InlineKeyboardButton(f"#{i}", callback_data=f"unit_{i}"))
            if len(row) == 3:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="back_menu")])
        await q.edit_message_text(
            f"{cl['name']} — Pilih nomor unit:",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return SELECT_UNIT


async def select_unit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User selected a unit number."""
    q = update.callback_query
    await q.answer()
    unit = int(q.data.replace("unit_", ""))
    context.user_data["unit"] = unit
    context.user_data["issues"] = set()
    return await show_checklist(update, context)


async def show_checklist(update: Update, context: ContextTypes.DEFAULT_TYPE, from_start=False):
    """Display batch checklist with toggle buttons."""
    insp_type = context.user_data["type"]
    unit = context.user_data["unit"]
    issues = context.user_data.get("issues", set())
    cl = CHECKLISTS[insp_type]

    buttons = []
    row = []
    for i, item in enumerate(cl["items"]):
        icon = "❌" if i in issues else "✅"
        row.append(InlineKeyboardButton(f"{icon} {item}", callback_data=f"t_{i}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    issue_count = len(issues)
    if issue_count == 0:
        btn_text = "➡️ Semua OK — Lanjut"
    else:
        btn_text = f"➡️ Lanjut ({issue_count} bermasalah)"
    buttons.append([InlineKeyboardButton(btn_text, callback_data="checklist_done")])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="back_menu")])

    unit_label = f" #{unit}" if cl["units"] > 1 else ""
    text = f"{cl['name']}{unit_label} — *Checklist*\n\nTap item yang ❌ BERMASALAH.\nYang tidak di-tap = ✅ Baik."

    if from_start and update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")
    return CHECKLIST


async def toggle_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle a checklist item."""
    q = update.callback_query
    await q.answer()
    idx = int(q.data.replace("t_", ""))
    issues = context.user_data.get("issues", set())
    if idx in issues:
        issues.discard(idx)
    else:
        issues.add(idx)
    context.user_data["issues"] = issues
    return await show_checklist(update, context)


async def checklist_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Checklist completed, ask for photo."""
    q = update.callback_query
    await q.answer()
    cl = CHECKLISTS[context.user_data["type"]]

    if cl["photo_required"]:
        text = "📸 Kirim *foto* sebagai bukti inspeksi."
    else:
        text = "📸 Kirim *foto* (opsional), atau tap Skip."

    buttons = []
    if not cl["photo_required"]:
        buttons.append([InlineKeyboardButton("⏭️ Skip Foto", callback_data="skip_photo")])

    await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons) if buttons else None, parse_mode="Markdown")
    return PHOTO


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive photo evidence and upload to Drive."""
    photo = update.message.photo[-1]  # Highest resolution
    file = await photo.get_file()
    file_bytes = await file.download_as_bytearray()

    insp_type = context.user_data["type"]
    unit = context.user_data["unit"]
    cl = CHECKLISTS[insp_type]
    now = datetime.now(WIB)
    filename = f"{insp_type}_{unit}_{now.strftime('%Y%m%d_%H%M%S')}.jpg"

    await update.message.reply_text("⏳ Mengupload foto...")
    photo_url = await upload_photo(bytes(file_bytes), filename, cl["drive_folder"])
    context.user_data["photo_url"] = photo_url

    buttons = [[InlineKeyboardButton("⏭️ Skip — Tanpa Catatan", callback_data="skip_notes")]]
    await update.message.reply_text(
        "📝 Tambahkan *catatan* (ketik), atau tap Skip.",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown",
    )
    return NOTES


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Skip photo step."""
    q = update.callback_query
    await q.answer()
    context.user_data["photo_url"] = None
    buttons = [[InlineKeyboardButton("⏭️ Skip — Tanpa Catatan", callback_data="skip_notes")]]
    await q.edit_message_text(
        "📝 Tambahkan *catatan* (ketik), atau tap Skip.",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown",
    )
    return NOTES


async def receive_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive text notes and save inspection."""
    notes = update.message.text
    return await _save(update, context, notes)


async def skip_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Skip notes and save inspection."""
    q = update.callback_query
    await q.answer()
    return await _save(update, context, None, from_callback=True)


async def _save(update: Update, context: ContextTypes.DEFAULT_TYPE, notes: str | None, from_callback=False):
    """Save inspection to database."""
    insp_type = context.user_data["type"]
    unit = context.user_data["unit"]
    issues = context.user_data.get("issues", set())
    photo_url = context.user_data.get("photo_url")
    cl = CHECKLISTS[insp_type]

    # Build checklist data: True = OK, False = issue
    checklist_data = {}
    for i, item in enumerate(cl["items"]):
        checklist_data[item] = i not in issues

    save_inspection(insp_type, unit, checklist_data, photo_url, notes)

    # Build summary
    unit_label = f" #{unit}" if cl["units"] > 1 else ""
    status = "⚠️ PERLU TINDAKAN" if issues else "✅ BAIK"
    lines = [f"*{cl['name']}{unit_label}* — Tersimpan!\n", f"Status: {status}"]
    if issues:
        lines.append("\nItem bermasalah:")
        for i in sorted(issues):
            lines.append(f"  ❌ {cl['items'][i]}")
    if photo_url:
        lines.append(f"\n📸 [Lihat Foto]({photo_url})")
    if notes:
        lines.append(f"\n📝 {notes}")
    lines.append("\nKetik /start untuk menu.")

    text = "\n".join(lines)
    if from_callback:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", disable_web_page_preview=True)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

    # Clear user data
    context.user_data.clear()
    return -1  # ConversationHandler.END
