import datetime
import config

def get_utc_iso_timestamp() -> str:
    """Returns the current UTC timestamp in YYYY-MM-DDTHH:MM:SSZ format."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def build_message(msg_type: str, data: dict = None) -> dict:
    """Builds a standardized JSON message payload for the student agent."""
    if data is None:
        data = {}
    return {
        "type": msg_type,
        "system_id": config.SYSTEM_ID,
        "timestamp": get_utc_iso_timestamp(),
        "data": data
    }
