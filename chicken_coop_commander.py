import time
import logging
import threading

import settings
# from chicken_coop_rest import ChickeChickenCoopRestServer
# from chicken_coop import ChickenCoop


class ChickenCoopCommander:
    
    def __init__(self, cc):
        self.__cc = cc
        
        self.__temp_thread = threading.Thread(target=self.runTemperatureManagement)
        self.__temp_stop = threading.Event()
        
        self.__light_thread = threading.Thread(target=self.runLightManagement)
        self.__light_stop = threading.Event()
        
    def runTemperatureManagement(self):
        while True:
            current_temperature = self.__cc.getTemperature()
            logging.info("Temperatur bei %.2f", current_temperature)
            
            if (current_temperature <= settings.temperature_low and self.__cc.isHeating() == False):
                self.__cc.heatingOn()
                logging.info("Wärmelampe Ein bei %.2f", current_temperature)
            elif (current_temperature >= settings.temperature_high and self.__cc.isHeating() == True):
                self.__cc.heatingOff()
                logging.info("Wärmelampe Aus bei %.2f", current_temperature)
                
            if self.__temp_stop.is_set():
                break
            time.sleep(settings.timing_temperature)
            
    def runLightManagement(self):
        while True:
            current_brightness = self.__cc.getBrightness()
            print("%.2f lx" % current_brightness)
            
            logging.info("Helligkeit bei %.2f lx", current_brightness)
            
            if self.__cc.isLight() == True:
                self.__cc.lightOff()
                
            else:
                self.__cc.lightOn()    
            

            if self.__light_stop.is_set():
                break
            
            time.sleep(settings.timing_brightness)
            
    def run(self):
        logging.info("Starting Light & Temperature Management")
        
        self.__temp_thread.start()
        self.__light_thread.start()
        
        logging.info("Starting Light & Temperature Management Done!")
        
    def __del__(self):
        self.__temp_stop.set()
        self.__temp_thread.join()
        
        self.__light_stop.set()
        self.__light_thread.join()