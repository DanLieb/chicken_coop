#!/usr/bin/python3


import pigpio
from pi1wire import Pi1Wire, W1Driver, OneWire

import time
import logging
import threading

from settings import CCSettings
import chicken_coop
            
my_chicken_coop = None       

class ChickenCoopCommander:
    """ BlaBla bla bla"""
    
    self.cc = None
    
    self.temp_thread = None
    self.bright_thread = None
    self.server_thread = None
    
    def __init__(self, ChickenCoop cc):
        self.cc = cc
        
        self.temp_thread = threading.Thread
    
    def run(self):
        print("Not Implemented Yet...")
        
    def runTemperatureManagement(self):
        logging.info("Starting Temperature Management")
        current_temperature = self.getTemperature()
        
        if (current_temperature <= self.__settings.temperature_low and self.heating == False):
            self.heatingOn()
            print("Zeitpunkt: %s: Wärmelampe Ein bei %.2f" % (current_time, current_temperature))
        elif (current_temperature >= self.__settings.temperature_high and self.heating == True):
            self.heatingOff()
            print("Zeitpunkt: %s: Wärmelampe Aus bei %.2f" % (current_time, current_temperature))
        
    def run(self):
        logging.info("Starting Temperature Management")

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%Y-%m-%D %H:%M:%S")

    logging.INFO("Starting in __main__")
    
    try:
        my_chicken_coop = ChickenCoop()
        cc_cmd = ChickenCoopCommander(my_chicken_coop)
        
        cc_cmd.run()
        
    except Exception as e:
        print('Another Error happend: %s' % e)
        