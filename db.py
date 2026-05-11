from datetime import datetime, timedelta, timezone
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

WIB = timezone(timedelta(hours=7))
client = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_inspection(insp_type: str, unit: int, checklist: dict, photo_url: str | None, notes: str | None):
    has_issue = any(not v for v in checklist.values())
    data = {
        "type": insp_type,
        "unit_number": unit,
        "checklist_data": checklist,
        "photo_url": photo_url or "",
        "notes": notes or "",
        "status": "perlu_tindakan" if has_issue else "baik",
    }
    return client.table("inspections").insert(data).execute()


def get_today_inspections(insp_type: str) -> list:
    today = datetime.now(WIB).strftime("%Y-%m-%d")
    return (
        client.table("inspections")
        .select("unit_number, status")
        .eq("type", insp_type)
        .gte("created_at", f"{today}T00:00:00+07:00")
        .execute()
        .data
    )


def get_week_inspections(insp_type: str) -> list:
    now = datetime.now(WIB)
    monday = now - timedelta(days=now.weekday())
    start = monday.strftime("%Y-%m-%d")
    return (
        client.table("inspections")
        .select("unit_number, status")
        .eq("type", insp_type)
        .gte("created_at", f"{start}T00:00:00+07:00")
        .execute()
        .data
    )


def get_month_inspections(insp_type: str) -> list:
    now = datetime.now(WIB)
    start = now.replace(day=1).strftime("%Y-%m-%d")
    return (
        client.table("inspections")
        .select("unit_number, status")
        .eq("type", insp_type)
        .gte("created_at", f"{start}T00:00:00+07:00")
        .execute()
        .data
    )


def get_rekap(schedule: str) -> dict:
    """Get completion summary for a schedule type (daily/weekly/monthly)."""
    from checklists import CHECKLISTS
    result = {}
    for key, cl in CHECKLISTS.items():
        if cl["schedule"] != schedule:
            continue
        if schedule == "daily":
            done = get_today_inspections(key)
        elif schedule == "weekly":
            done = get_week_inspections(key)
        else:
            done = get_month_inspections(key)
        done_units = {d["unit_number"] for d in done}
        result[key] = {"name": cl["name"], "total": cl["units"], "done": len(done_units), "done_units": done_units}
    return result
