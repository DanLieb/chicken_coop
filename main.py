#!/usr/bin/python3

import time
import logging
import threading

import settings
from chicken_coop import ChickenCoop
class ChickenCoopCommander:
    
    def __init__(self, ChickenCoop cc):
        self.self.__cc = cc
        
        self.__temp_thread = threading.Thread(target=self.runTemperatureManagement, args=(self))
        self.__temp_stop = threading.Event()
        
    def runTemperatureManagement(self):
        while True:
            current_temperature = self.__cc.getTemperature()
            
            if (current_temperature <= settings.temperature_low and self.self.__cc.isHeating() == False):
                self.__cc.heatingOn()
                logging.info("Wärmelampe Ein bei %.2f", current_temperature)
            elif (current_temperature >= settings.temperature_high and self.__cc.isHeating() == True):
                self.__cc.heatingOff()
                logging.info("Wärmelampe Aus bei %.2f", current_temperature)
                
            if self.__temp_stop.is_set():
                break
            time.sleep(settings.timing_temperature)
            
    def run(self):
        logging.info("Starting Temperature Management")
        
        self.__temp_thread.start()
        
        logging.info("Starting Temperature Management Done!")
        
    def __del__(self):
        self.__temp_stop.set()
        self.__temp_thread.join()


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%Y-%m-%D %H:%M:%S")

    logging.INFO("Starting in __main__")
    
    try:
        cc = ChickenCoop()
        cc_cmd = ChickenCoopCommander(cc)
        
        cc_cmd.run()
        
    except Exception as e:
        print('Another Error happend: %s' % e)
        