import time
import logging
import threading

import json
from flask import Flask, request, jsonify

import settings
# from chicken_coop_rest import ChickeChickenCoopRestServer
# from chicken_coop import ChickenCoop

temp_logger = logging.getLogger("Temperature_Sensor")

brightness_logger = logging.getLogger("Brightness_Sensor")

basic_logger = logging.getLogger("Basic Logging")



class ChickenCoopCommander:
    
    def __init__(self, cc):
        self.__cc = cc
        
        self.__temp_thread = threading.Thread(target=self.runTemperatureManagement)
        self.__temp_stop = threading.Event()
        
        self.__light_thread = threading.Thread(target=self.runLightManagement)
        self.__light_stop = threading.Event()
        
        self.__lights_out_counter = int(settings.lights_out_seconds / settings.timing_brightness)
        # self.__lights_counting = True
        self.__door_down_counter = int(settings.door_down_seconds / settings.timing_brightness)
        # self.__door_counting = True
        self.__light_goodnight = False
        
        self.__flask_app = Flask(__name__)
        
        self.__flask_app.add_url_rule(rule='/door', endpoint='door', view_func=self.setDoor, methods=['POST'])
        
        
        self.__rest_thread = threading.Thread(target=self.runRestServer)
        self.__rest_stop = threading.Event()
        
    def __del__(self):
        basic_logger.info("Shutting Down Everything - Prepare for evacuation")
        self.__temp_stop.set()
        self.__temp_thread.join()
        
        self.__light_stop.set()
        self.__light_thread.join()
        
        self.__rest_stop.set()
        self.__rest_thread.join()
        
        
                
    def runTemperatureManagement(self):
        while True:
            current_temperature = self.__cc.getTemperature()
            # temp_logger.info("T= %.2f °C", current_temperature)
            
            if (current_temperature <= settings.temperature_low and self.__cc.isHeating() == False):
                self.__cc.heatingOn()
                basic_logger.info("Wärmelampe Ein bei %.2f", current_temperature)
            elif (current_temperature >= settings.temperature_high and self.__cc.isHeating() == True):
                self.__cc.heatingOff()
                basic_logger.info("Wärmelampe Aus bei %.2f", current_temperature)
                
            if self.__temp_stop.is_set():
                break
            time.sleep(settings.timing_temperature)
            
    def runLightManagement(self):
        while True:
            current_brightness = self.__cc.getBrightness()
            
            brightness_logger.info("B= %.2f lx", current_brightness)
            
            if current_brightness < settings.brightness_low:
                if not self.__light_goodnight:
                    self.__light_goodnight = True
                    basic_logger.info("es wird dunkel bei bei %.2f lx - Licht an! - Rein in die Bude", current_brightness)
                    self.__cc.lightOn()
                else:
                      
                    if self.__door_down_counter != 0:
                        
                        self.__door_down_counter -= 1
                        
                        if self.__door_down_counter == 0:
                            self.__cc.doorClose()
                            basic_logger.info("Alle herinnen? - Türl zu!!")                    
                    
                    if self.__lights_out_counter != 0:
                        
                        self.__lights_out_counter -= 1
                        
                        if self.__lights_out_counter == 0:
                            
                            basic_logger.info("Schlafenszeit!! - A Ruah is und Licht aus")
                            self.__cc.lightOff()

                    
            if current_brightness > settings.brightness_high:
                
                if self.__light_goodnight:
                    self.__light_goodnight = False  
                    self.__lights_out_counter = int(settings.lights_out_seconds / settings.timing_brightness)
                    self.__door_down_counter = int(settings.door_down_seconds / settings.timing_brightness)
                    self.__cc.doorOpen() 
                    basic_logger.info("Guten Morgen! - Raus mit euch!!")


            if self.__light_stop.is_set():
                break
            
            # i dont care about a slight tick/seconds deviation 
            time.sleep(settings.timing_brightness)
            
    def runRestServer(self):
        self.__flask_app.run()
    
    def run(self):
              
        self.__temp_thread.start()
        self.__light_thread.start()

        basic_logger.info("Starting Light & Temperature Management Done!")
        
        self.__rest_thread.start()
        
    def setDoor(self):
        record = json.loads(request.data)
        print(jsonify(record))
        return 
