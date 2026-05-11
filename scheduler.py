from datetime import time, datetime, timedelta, timezone
from telegram.ext import ContextTypes
from checklists import CHECKLISTS, DAILY_TYPES, WEEKLY_TYPES, MONTHLY_TYPES
from db import get_rekap
from config import CHAT_ID

WIB = timezone(timedelta(hours=7))


def setup_scheduler(job_queue):
    """Register all reminder jobs."""
    if not CHAT_ID:
        print("CHAT_ID not set — reminders disabled.")
        return

    # Daily reminder: Mon-Sat at 07:15 WIB
    job_queue.run_daily(
        daily_reminder,
        time=time(7, 15, tzinfo=WIB),
        days=(0, 1, 2, 3, 4, 5),  # Mon=0, Sat=5, exclude Sun=6
        name="daily_reminder",
    )

    # Weekly reminder: Tue-Sat at 07:20 WIB (exclude Mon & Sun)
    job_queue.run_daily(
        weekly_reminder,
        time=time(7, 20, tzinfo=WIB),
        days=(1, 2, 3, 4, 5),  # Tue=1 to Sat=5
        name="weekly_reminder",
    )

    # Monthly check: Tue-Sat at 07:25 WIB, logic inside callback
    job_queue.run_daily(
        monthly_reminder_check,
        time=time(7, 25, tzinfo=WIB),
        days=(1, 2, 3, 4, 5),  # Tue-Sat
        name="monthly_reminder",
    )

    print(f"Scheduler active — reminders for chat {CHAT_ID}")


async def daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Send daily inspection reminder with progress."""
    rekap = get_rekap("daily")
    lines = ["🌅 *Reminder Inspeksi Harian*\n"]
    all_done = True
    for key, info in rekap.items():
        if info["done"] >= info["total"]:
            lines.append(f"  ✅ {info['name']} — Selesai")
        else:
            remaining = info["total"] - info["done"]
            lines.append(f"  ⏳ {info['name']} — {remaining} unit belum")
            all_done = False

    if all_done:
        lines.append("\n🎉 Semua inspeksi harian sudah selesai!")
    else:
        lines.append("\nKetik /start untuk mulai inspeksi.")

    await context.bot.send_message(CHAT_ID, "\n".join(lines), parse_mode="Markdown")


async def weekly_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Send weekly inspection reminder — only on first eligible day (Tue)."""
    now = datetime.now(WIB)
    # Only send on Tuesday (weekday=1) to avoid duplicate weekly reminders
    if now.weekday() != 1:
        # Check if Tuesday was skipped (e.g., holiday) — send if nothing done yet
        rekap = get_rekap("weekly")
        any_done = any(info["done"] > 0 for info in rekap.values())
        if any_done:
            return  # Already started this week, skip

    rekap = get_rekap("weekly")
    lines = ["📋 *Reminder Inspeksi Mingguan*\n"]
    all_done = True
    for key, info in rekap.items():
        if info["done"] >= info["total"]:
            lines.append(f"  ✅ {info['name']} — Selesai")
        else:
            lines.append(f"  ⏳ {info['name']} — Belum dicek")
            all_done = False

    if all_done:
        lines.append("\n🎉 Semua inspeksi mingguan sudah selesai!")
    else:
        lines.append("\nKetik /start untuk mulai inspeksi.")

    await context.bot.send_message(CHAT_ID, "\n".join(lines), parse_mode="Markdown")


async def monthly_reminder_check(context: ContextTypes.DEFAULT_TYPE):
    """Send monthly reminder on first eligible day of the month."""
    now = datetime.now(WIB)
    if now.day > 7:
        return  # Only check first week of month

    rekap = get_rekap("monthly")
    any_done = any(info["done"] > 0 for info in rekap.values())
    if any_done:
        return  # Already started this month

    lines = ["🗓️ *Reminder Inspeksi Bulanan*\n"]
    for key, info in rekap.items():
        lines.append(f"  ⏳ {info['name']} — Belum dicek")
    lines.append("\nKetik /start untuk mulai inspeksi.")

    await context.bot.send_message(CHAT_ID, "\n".join(lines), parse_mode="Markdown")
