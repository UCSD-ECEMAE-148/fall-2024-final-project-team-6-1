# Motor RPM values
FORWARD_RPM_MIN = 1800
FORWARD_RPM_MAX = 6000
REVERSE_RPM_MIN = -1600
REVERSE_RPM_MAX = -2500

# for spot detection
BAR_POSITIONS = {
    'horizontal1': 30,  # Default position for the first horizontal bar
    'horizontal2': 44,  # Default position for the second horizontal bar
    'vertical1': 1,    # Default position for the first vertical bar
    'vertical2': 38,    # Default position for the second vertical bar
    'vertical3': 66,    # Default position for the third vertical bar
    'vertical4': 99     # Default position for the fourth vertical bar
}

# Cropping range for yellow line detection
LOW_CROP = 100
HIGH_CROP = 33

# Vertical and horizontal line positions as percentages (for yellow endpoint detection)
LINES = {'line1_x_percent': 26, 'line2_x_percent': 73, 'horizontal_y_percent': 31}

# Vertical centerline alignment (percentage of frame width)
VERTICAL_CENTERLINE = 52

# Steering servo values
STEERING_LEFT_MAX = 0.12
STEERING_RIGHT_MAX = 0.92
STEERING_NEUTRAL = 0.52

# HSV values for color filtering
HSV_VALUES = {
    "yellow": {
        "LOW_H": 8,
        "HIGH_H": 60,
        "LOW_S": 11,
        "HIGH_S": 193,
        "LOW_V": 219,
        "HIGH_V": 255
    },
    "red": {
        "LOW_H": 0,
        "HIGH_H": 17,
        "LOW_S": 107,
        "HIGH_S": 223,
        "LOW_V": 141,
        "HIGH_V": 199
    },
    "blue": {
        "LOW_H": 71,
        "HIGH_H": 105,
        "LOW_S": 46,
        "HIGH_S": 119,
        "LOW_V": 122,
        "HIGH_V": 177
    },
    "green": {
        "LOW_H": 36,
        "HIGH_H": 76,
        "LOW_S": 67,
        "HIGH_S": 181,
        "LOW_V": 51,
        "HIGH_V": 211
    }
}

# Camera settings
CAMERA_RESOLUTION_WIDTH = 1280
CAMERA_RESOLUTION_HEIGHT = 720
CAMERA_FPS = 12

# Safety timeout
SAFETY_TIMEOUT = 1.5

# Color Mask
# Set to False to disable the Color Mask window
# False will improve performance
DISPLAY_COLOR_MASK = False
