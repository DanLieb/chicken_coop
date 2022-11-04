import pigpio
from pi1wire import Pi1Wire, W1Driver, OneWire

import logging
import settings
import time

import smbus
from bh1750 import BH1750

basic_logger = logging.getLogger("Basic Logging")

global_chicken_coop = None

class ChickenCoop:
    """A Class integrating all sensors and outputs available"""

 
    def __init__(self):        
        global global_chicken_coop 
        global_chicken_coop = self
        
        try:
            self.pi = pigpio.pi()
            if not self.pi.connected:
                basic_logger.error("OOps i couldn't connect to the pigpio daemon!")
            else:
                basic_logger.info("Setting up output pins")
                
                self.pi.set_mode(settings.pin_relais_in_1, pigpio.OUTPUT)
                self.pi.set_mode(settings.pin_relais_in_2, pigpio.OUTPUT)
                self.pi.set_mode(settings.pin_relais_in_3, pigpio.OUTPUT)
                self.pi.set_mode(settings.pin_relais_in_4, pigpio.OUTPUT)
                
                self.pi.write(settings.pin_relais_in_1, 1)
                self.pi.write(settings.pin_relais_in_2, 1)
                self.pi.write(settings.pin_relais_in_3, 1)
                self.pi.write(settings.pin_relais_in_4, 1)
                
                #
                # Setup Input Pins 
                #
                
                basic_logger.info("Setting up input pins")
                
                self.pi.set_mode(settings.pin_button_up, pigpio.INPUT)
                self.pi.set_mode(settings.pin_button_down, pigpio.INPUT)
                self.pi.set_pull_up_down(settings.pin_button_up, pigpio.PUD_UP)
                self.pi.set_pull_up_down(settings.pin_button_down, pigpio.PUD_UP)
                
                # 100 ms filtering to avoid multiple callbacks 
                
                self.pi.set_glitch_filter(settings.pin_button_up, 100000)
                self.pi.set_glitch_filter(settings.pin_button_down, 100000)
                
                # Use the falling edge because i use a pullup res. for the button input.
                
                self.pi.callback(settings.pin_button_up, pigpio.FALLING_EDGE, self.callbackUp)
                self.pi.callback(settings.pin_button_down, pigpio.FALLING_EDGE, self.callbackDown)
            
            self.temp_sensor = Pi1Wire().find(settings.mac_sensor_temp)
            
            basic_logger.info("Connected to the temperature sensor")
            
            # 
            
            bus = smbus.SMBus(1)
            self.brightness_sensor = BH1750(bus)
            basic_logger.info("Connected to the brightness sensor")
            
            self.heating = False
            
            self.light = False
            
        except Exception as e:
            basic_logger.error("OOps i f***** it up: \n %s" % e)
            
    
    @staticmethod    
    def callbackUp(gpio, level, tick):
        global_chicken_coop.doorOpen()
        
    
    @staticmethod
    def callbackDown(gpio, level, tick):
        global_chicken_coop.doorClose()
    
    def heatingOn(self):
        self.heating = True
        self.pi.write(settings.pin_relais_in_1, 0)

    def heatingOff(self):
        self.heating = False
        self.pi.write(settings.pin_relais_in_1, 1)
        
    def lightOn(self):
        self.light = True
        self.pi.write(settings.pin_relais_in_2, 0)
        
    def lightOff(self):
        self.light = False
        self.pi.write(settings.pin_relais_in_2, 1)
    
    def doorOpen(self):
        # current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        basic_logger.info('Open Door Signal')
        
        self.pi.write(settings.pin_relais_in_3, 0)
        time.sleep(0.5)
        self.pi.write(settings.pin_relais_in_3, 1)
        

    def doorClose(self):
        # current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        basic_logger.info('Close Door Signal')
        
        self.pi.write(settings.pin_relais_in_4, 0)
        time.sleep(0.5)
        self.pi.write(settings.pin_relais_in_4, 1)
        
    def getTemperature(self):
        current_temperature = self.temp_sensor.get_temperature()
        return current_temperature
    
    def getBrightness(self):
        b = self.brightness_sensor.measure_high_res()
        return b
        
    def isHeating(self):
        return self.heating
    
    def isLight(self):
        return self.light
    
    
    def __del__(self):
        
        self.heatingOff()
        self.lightOff()
        self.pi.stop()
