# Checklist definitions for all MFK inspection types

CHECKLISTS = {
    "toilet": {
        "name": "🚽 Toilet",
        "schedule": "daily",
        "units": 6,
        "drive_folder": "FOLDER_TOILET",
        "photo_required": True,
        "items": [
            "Kebersihan lantai",
            "Ketersediaan air",
            "Sabun cuci tangan",
            "Tissue / tisu",
            "Kondisi kloset",
            "Tempat sampah",
            "Penerangan",
            "Bau / ventilasi",
        ],
    },
    "apar": {
        "name": "🧯 APAR",
        "schedule": "weekly",
        "units": 5,
        "drive_folder": "FOLDER_MFK",
        "photo_required": True,
        "items": [
            "Tekanan gauge (hijau)",
            "Segel utuh",
            "Pin pengaman",
            "Kondisi selang",
            "Nozzle",
            "Label & tanggal exp",
            "Posisi penempatan",
            "Akses mudah dijangkau",
        ],
    },
    "genset": {
        "name": "⚡ Genset",
        "schedule": "weekly",
        "units": 1,
        "drive_folder": "FOLDER_GENSET",
        "photo_required": True,
        "items": [
            "Level oli mesin",
            "Level coolant",
            "Kondisi aki/baterai",
            "Test run (nyalakan)",
            "Suara mesin",
            "Kebersihan area",
            "Indikator panel",
        ],
    },
    "listrik": {
        "name": "🔌 Listrik (MCB Panel)",
        "schedule": "weekly",
        "units": 1,
        "drive_folder": "FOLDER_MFK",
        "photo_required": False,
        "items": [
            "Kondisi MCB panel",
            "Kabel tidak terkelupas",
            "Tidak ada percikan/bau gosong",
            "Label MCB terbaca",
        ],
    },
    "air": {
        "name": "💧 Air Bersih",
        "schedule": "weekly",
        "units": 1,
        "drive_folder": "FOLDER_MFK",
        "photo_required": False,
        "items": [
            "Kualitas visual (jernih)",
            "Tidak berbau",
            "Aliran lancar",
        ],
    },
    "jalur_evakuasi": {
        "name": "🚪 Jalur Evakuasi",
        "schedule": "weekly",
        "units": 1,
        "drive_folder": "FOLDER_MFK",
        "photo_required": False,
        "items": [
            "Rambu terlihat jelas",
            "Jalur tidak terhalang",
        ],
    },
    "ipal": {
        "name": "🏭 IPAL",
        "schedule": "weekly",
        "units": 1,
        "drive_folder": "FOLDER_MFK",
        "photo_required": False,
        "items": [
            "Kondisi visual bak",
            "Tidak ada kebocoran",
            "Aliran normal",
            "Tidak berbau menyengat",
        ],
    },
    "titik_kumpul": {
        "name": "📍 Titik Kumpul",
        "schedule": "monthly",
        "units": 1,
        "drive_folder": "FOLDER_MFK",
        "photo_required": False,
        "items": [
            "Rambu mudah terlihat",
            "Area tidak terhalang",
            "Akses dari semua arah",
        ],
    },
    "tps_b3": {
        "name": "☣️ TPS B3",
        "schedule": "monthly",
        "units": 1,
        "drive_folder": "FOLDER_MFK",
        "photo_required": True,
        "items": [
            "Tidak ada kebocoran",
            "Cold storage berfungsi",
            "Label B3 terbaca",
            "Wadah dalam kondisi baik",
        ],
    },
    "safety_box": {
        "name": "🗑️ Safety Box",
        "schedule": "monthly",
        "units": 1,
        "drive_folder": "FOLDER_MFK",
        "photo_required": False,
        "items": [
            "Isi < 3/4 penuh",
            "Tidak bocor/rusak",
            "Label terlihat",
        ],
    },
}

# Helper groupings
DAILY_TYPES = [k for k, v in CHECKLISTS.items() if v["schedule"] == "daily"]
WEEKLY_TYPES = [k for k, v in CHECKLISTS.items() if v["schedule"] == "weekly"]
MONTHLY_TYPES = [k for k, v in CHECKLISTS.items() if v["schedule"] == "monthly"]
