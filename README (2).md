# Weapon Detection System

Smart Real-Time Weapon Detection is a Python desktop application using YOLOv4, OpenCV, and PyQt5 to detect handguns and knives from a live webcam feed. It highlights detections, saves evidence frames, and sends alerts with location and recipient details to a Django REST API.

## Project structure

```
weapondetection project/
├── Client Side/     # Desktop app (PyQt5 + OpenCV + YOLOv4) that runs detection on webcam feed
└── Server Side/      # Django REST API that receives and stores alerts
```

## Setup

### 1. Client Side (desktop app)

```bash
cd "weapondetection project/Client Side"
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

**Download the YOLOv4 weights file** (not included in this repo — it's 245MB, over GitHub's file size limit):
- Get `yolov4.weights` from the [official AlexeyAB/darknet releases](https://github.com/AlexeyAB/darknet/releases)
- Place it in `Client Side/weights/`

Then run:
```bash
python main.py
```

### 2. Server Side (Django API)

```bash
cd "weapondetection project/Server Side/wd_s"
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r ../requirements.txt
```

**Set up environment variables:**
- Copy `.env.example` to `.env`
- Fill in your own values for `SECRET_KEY`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_NUMBER`

Then run migrations and start the server:
```bash
python manage.py migrate
python manage.py runserver
```

## Notes

- `db.sqlite3`, `.env`, `venv/`, and uploaded alert images are excluded from this repo via `.gitignore` — they're either local secrets, local databases, or generated at runtime.
- `Client Side/save_frame/` and `Server Side/wd_s/static/images/` are empty placeholder folders (with `.gitkeep`) that fill up with runtime data when the app runs.
