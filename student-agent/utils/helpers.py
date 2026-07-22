import datetime
import config

def get_iso_timestamp():
    """Returns the current local timestamp in YYYY-MM-DDTHH:MM:SS format."""
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def create_message(message_type, data):
    """Creates a standardized JSON message payload for the agent."""
    return {
        "type": message_type,
        "student_id": config.STUDENT_ID,
        "timestamp": get_iso_timestamp(),
        "data": data
    }
