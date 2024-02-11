from datetime import datetime


def log(message: str):
    """Log message with current time"""
    time = datetime.now().strftime("%T")
    print(f"\r[{time}] {message}", flush=True)
