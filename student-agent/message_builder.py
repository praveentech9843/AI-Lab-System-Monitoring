import datetime
import socket
import config

def get_utc_iso_timestamp() -> str:
    """Returns the current UTC timestamp in YYYY-MM-DDTHH:MM:SSZ format."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def build_message(msg_type: str, data: dict = None) -> dict:
    """Builds a standardized JSON message payload for the student agent."""
    if data is None:
        data = {}
    
    # Auto-detect hostname
    hostname = socket.gethostname()
    
    return {
        "type": msg_type,
        "system_id": config.SYSTEM_ID,
        "workstation_id": config.WORKSTATION_ID,
        "hostname": hostname,
        "student_name": config.STUDENT_NAME,
        "timestamp": get_utc_iso_timestamp(),
        "data": data
    }
