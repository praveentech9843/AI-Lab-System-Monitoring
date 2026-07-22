import datetime
import config

def get_utc_iso_timestamp():
    """Returns the current UTC timestamp in YYYY-MM-DDTHH:MM:SSZ format."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def build_message(type, data=None):
    """Builds a standardized JSON message payload for the agent containing type, system_id and timestamp."""
    message = {
        "type": type,
        "system_id": config.SYSTEM_ID,
        "timestamp": get_utc_iso_timestamp()
    }
    if data is not None:
        message["data"] = data
    return message
