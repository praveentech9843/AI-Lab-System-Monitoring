import config

def build_message(type, data=None):
    """Builds a standardized JSON message payload for the agent containing type and system_id."""
    message = {
        "type": type,
        "system_id": config.SYSTEM_ID
    }
    if data is not None:
        message["data"] = data
    return message
