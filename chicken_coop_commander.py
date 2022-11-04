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
        
        self.__lights_out_counter = int(settings.lights_out_seconds / settings.timing_brightness)
        self.__door_down_counter = int(settings.door_down_seconds / settings.timing_brightness)
        self.__light_goodnight = False
        
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
            
            logging.info("Helligkeit bei %.2f lx", current_brightness)
            
            if current_brightness < settings.brightness_low:
                if not self.__light_goodnight:
                    self.__light_goodnight = True
                    self.__cc.lightOn()
                    logging.info("es wird Nacht - Licht an! - Rein in die Bude")
                else:
                    self.__lights_out_counter -= 1
                    self.__door_down_counter -= 1
                    
                    if self.__lights_out_counter == 0:
                        self.__cc.lightOff()
                        self.__lights_out_counter = int(settings.lights_out_seconds / settings.timing_brightness)
                        logging.info("Alle herinnen? - Schlafenszeit!!")
                    
                    if self.__door_down_counter == 0:
                        self.__cc.doorClose()
                        self.__door_down_counter = int(settings.door_down_seconds / settings.timing_brightness)
                        logging.info("Alle herinnen? - Türl zu!!")
                    
            if current_brightness > settings.brightness_high:
                
                if self.__light_goodnight:
                    self.__light_goodnight = False  
                    self.__cc.doorOpen() 
                

                
            
            # if self.__cc.isLight() == True:
            #     self.__cc.lightOff()
                
            # else:
            #     self.__cc.lightOn()    
            
            

            if self.__light_stop.is_set():
                break
            
            # i dont care about a slight tick/seconds deviation 
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