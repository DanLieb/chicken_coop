from time import time 
from xmlrpc.client import DateTime


mac_sensor_temp = "283c01f0953119" 

#
# temperature settings
#      

temperature_low = 27
temperature_high = temperature_low + 3

#
# brightness settings
#

brightness_address = 0x23

brightness_low = 5
brightness_high = brightness_low + 50

#
# GPIO - Pins
#

pin_relais_in_1 = 16       # Heating Lamp
pin_relais_in_2 = 26       # Light
pin_relais_in_3 = 20       # Input for Kerbl Up
pin_relais_in_4 = 21       # Input for Kerbl Down

pin_button_up = 5      # Taster 1
pin_button_down = 12   # Taster 2

# Timing Values
# Functions are called every n seconds
#

timing_temperature = 10.
timing_brightness = 4.

# Das gibt ne saftige Fehlermeldung. mal schauen was da los ist.
# door_open_time = time(hours=7, minutes=30)
# door_close_time = time(hours=18, minutes=0)

# TIMING: 
#
# when current_brightness < brightness_low
#   -> lights on
#   -> after door_cown_seconds Door is Closed
#   -> after lights_out_seconds the light is turned off
#
 

lights_out_seconds = 16
door_down_seconds = 4
        

# LOGGING

TEMP_LOGS = "logs/temperature.log"
BRIGHTNESS_LOGS = "logs/brightness.log"
        