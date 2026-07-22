"""
AI Risk Engine Thresholds Module.
Defines configurable risk score constants for various anomaly event types.
"""
TAB_SWITCH: int = 20
MULTIPLE_FACE: int = 30
FACE_MISSING: int = 15
HEAD_DOWN: int = 10
LOOKING_AWAY: int = 8
PHONE_DETECTED: int = 35

# Dictionary mapping uppercase event names to risk score values
EVENT_THRESHOLDS = {
    "TAB_SWITCH": TAB_SWITCH,
    "MULTIPLE_FACE": MULTIPLE_FACE,
    "FACE_MISSING": FACE_MISSING,
    "HEAD_DOWN": HEAD_DOWN,
    "LOOKING_AWAY": LOOKING_AWAY,
    "PHONE_DETECTED": PHONE_DETECTED,
}
