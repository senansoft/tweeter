# 🐦 Django Auto-Tweeter Bot

A Django-based application that automates Twitter posts every hour. It includes a custom **Admin Dashboard** to manage tweets, monitor logs, and control scheduling.

---

## 🚀 Features
* **Auto-Post:** Automatically sends a tweet every 60 minutes.
* **Admin Dashboard:** Full control over tweet content and scheduling.
* **Task Scheduling:** Powered by `django-celery-beat` (or `apscheduler`).
* **Secure:** Environment variables for Twitter API keys.

---

## 🛠️ Tech Stack
* **Backend:** Python 3.x, Django
* **Database:** PostgreSQL (or SQLite for dev)
* **API Integration:** Tweepy (Twitter API v2)
* **Task Queue:** Celery / Redis (or APScheduler)

---
📅 How it Works
The project uses a background worker that checks the database every hour for the next scheduled tweet and pushes it to Twitter using the Tweepy library.
