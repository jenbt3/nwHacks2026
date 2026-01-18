# --- Recognition Constants ---
MODEL_NAME = "Facenet512" 
FACE_MATCH_THRESHOLD = 0.35  

# --- Vision Processing ---
DETECTION_DOWNSCALE = 0.25  # Reduces CPU load on Pi 5 for Haar Cascades

# --- Wandering Sentry Logic ---
# Area in pixels (w * h) that triggers a 'Proximity' alert
EXIT_PROXIMITY_AREA = 50000  

# Hours where wandering is considered 'High Priority'
OFF_HOURS_START = 22  # 10 PM
OFF_HOURS_END = 6     # 6 AM

# --- Social Dignity Filter ---
# 15-minute cooldown (in seconds) to prevent repetitive whispers
GREETING_COOLDOWN = 900 

# --- AI Scripting ---
MAX_WHISPER_WORDS = 20