class CCSettings():
    """A class to store Settings for the Chicken Coop Programm"""
    
    def __init__(self):
        self.mac_sensor_temp = "283c01f0953119" 
        
        #
        # temperature settings
        #      
        
        self.temperature_low = 27
        self.temperature_high = self.temperature_low + 3
        
        #
        # brightness settings
        #
        
        self.brightness_low = 100
        self.brightness_high = self.brightness_low + 50
        
        #
        # GPIO - Pins
        #
        
        self.pin_relais_in_1 = 16       # Heating Lamp
        self.pin_relais_in_2 = 26       # Light
        self.pin_relais_in_3 = 20       # Input for Kerbl Up
        self.pin_relais_in_4 = 21       # Input for Kerbl Down
        
        self.pin_button_up = 5      # Taster 1
        self.pin_button_down = 12   # Taster 2
        
        
        