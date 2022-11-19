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
        
        
        self.__light_manual = False
        self.__light_manual_countdown = settings.lights_manual_countdown
        
        self.__heating_manual = False
        self.__heating_manual_countdown = settings.heating_manual_countdown
        
        self.__lights_out_counter = int(settings.lights_out_seconds / settings.timing_brightness)
        # self.__lights_counting = True
        self.__door_down_counter = int(settings.door_down_seconds / settings.timing_brightness)
        # self.__door_counting = True
        self.__light_goodnight = False
        
        self.__brightness_old = cc.getBrightness()
        
        self.__temp_thread = threading.Thread(target=self.runTemperatureManagement)
        self.__temp_stop = threading.Event()
        
        self.__light_thread = threading.Thread(target=self.runLightManagement)
        self.__light_stop = threading.Event()
    
        self.__flask_app = Flask(__name__.split('.')[0])
        
        self.__flask_app.add_url_rule(rule='/door/<status>', view_func=self.door, methods=['GET'])
        self.__flask_app.add_url_rule(rule='/light/<status>', view_func=self.light, methods=['GET'])
        self.__flask_app.add_url_rule(rule='/heating/<status>', view_func=self.heating, methods=["GET"])
        self.__flask_app.add_url_rule(rule='/measure/<status>', view_func=self.measure, methods=["GET"])
        # self.__flask_app.add_url_rule(rule='/door',  view_func=self.door, methods=['GET'])
        # endpoint='door',
        
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
            
            # Manual Switching with Safety Turn-Off After heating_manual_countdown seconds
            
            if self.__heating_manual == True:
                self.__heating_manual_countdown -= settings.timing_temperature
                
                if self.__heating_manual_countdown <= 0:
                    self.__heating_manual = False
                elif not self.__cc.isHeating():
                    self.__cc.heatingOn()
                    
                time.sleep(settings.timing_temperature)
                continue
            
            elif self.__heating_manual == False and self.__heating_manual_countdown != settings.heating_manual_countdown:
                self.__heating_manual_countdown = settings.heating_manual_countdown
                self.__cc.heatingOff()
            
            # Automated Heatings depending on the chicken coop temperature
            if self.__light_goodnight:
                current_temperature = self.__cc.getTemperature()
                # temp_logger.info("T= %.2f °C", current_temperature)
                
                if (current_temperature <= settings.temperature_low and self.__cc.isHeating() == False):
                    self.__cc.heatingOn()
                    basic_logger.info("Wärmelampe Ein bei %.2f", current_temperature)
                elif (current_temperature >= settings.temperature_high and self.__cc.isHeating() == True):
                    self.__cc.heatingOff()
                    basic_logger.info("Wärmelampe Aus bei %.2f", current_temperature)
                    
                if self.__temp_stop.is_set():
                    self.__cc.heatingOff()
                    break
                time.sleep(settings.timing_temperature)
                
    def runLightManagement(self):
        while True:

            # Manual Switching with Safety Turn-Off after settings.lights_manual_countdown seconds.
            
            if self.__light_manual == True:
                self.__light_manual_countdown -= settings.timing_brightness
                
                if self.__light_manual_countdown <= 0:
                    self.__light_manual = False
                    # self.__cc.lightOff()  
                elif not self.__cc.isLight():
                    self.__cc.lightOn()
                    
                time.sleep(settings.timing_brightness)
                continue
            elif self.__light_manual == False and self.__light_manual_countdown != settings.lights_manual_countdown:
                self.__light_manual_countdown = settings.lights_manual_countdown
                self.__cc.lightOff()
                
            # Automatic Light Management
            
            current_brightness = self.__cc.getBrightness()
            
            # brightness_logger.info("B= %.2f lx", current_brightness)        
                   
            if current_brightness < settings.brightness_low and self.__brightness_old < settings.brightness_low:
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

                    
            if current_brightness > settings.brightness_high and self.__brightness_old > settings.brightness_high:
                
                if self.__light_goodnight:
                    self.__light_goodnight = False  
                    self.__lights_out_counter = int(settings.lights_out_seconds / settings.timing_brightness)
                    self.__door_down_counter = int(settings.door_down_seconds / settings.timing_brightness)
                    self.__cc.doorOpen() 
                    basic_logger.info("Guten Morgen! - Raus mit euch!!")

            self.__brightness_old = current_brightness
            
            if self.__light_stop.is_set():
                break
            
            # i dont care about a slight tick/seconds deviation 
            time.sleep(settings.timing_brightness)
            
    def runRestServer(self):
        self.__flask_app.run(host='0.0.0.0')
    
    def run(self):
        basic_logger.info("Starting Light & Temperature Management.")
          
        self.__temp_thread.start()
        self.__light_thread.start()

        
        basic_logger.info("Starting Rest-API on localhost.")
        self.__rest_thread.start()
        
    def door(self, status):
        if status == "open":
            self.__cc.doorOpen()
            return jsonify({'action': 'chicken_coop.doorOpen()',
                            'status': 'done'})
        elif status == "close":
            self.__cc.doorClose()
            return jsonify({'action': 'chicken_coop.doorClose()',
                            'status': 'done'})
        elif status == "get":
            return jsonify({'action': 'chicken_coop.getDoorStatus()',
                            'status': 'not implemented'})
        else:
            basic_logger.info("What do you mean? door status :%s is unknown" % status)
            return jsonify({'action': 'None',
                            'status': 'failed'})
    
    def light(self, status):
        if status == "on":
            self.__light_manual = True
            return jsonify({'action': 'chicken_coop.manualLightOn()',
                            'status': 'done'})
        elif status == "off":
            self.__light_manual = False
            return jsonify({'action': 'chicken_coop.manualLightOff()',
                            'status': 'done'})
        elif status == "get":
            return jsonify({'action': 'chicken_coop.getLightStatus()',
                            'status': self.__cc.isLight() })
        else:
            basic_logger.info("What do you mean? light status :%s is unknown" % status)
            return jsonify({'action': 'None',
                            'status': 'failed'})
    
    def heating(self, status):
        if status == "on":
            self.__heating_manual = True
            return jsonify({'action': 'chicken_coop.manualHeatingOn()',
                            'status': 'done'})
        elif status == "off":
            self.__heating_manual = False
            return jsonify({'action': 'chicken_coop.manualHeatingOff()',
                            'status': 'done'})
        elif status == "get":
            return jsonify({'action': 'chicken_coop.getHeatingStatus()',
                            'status': self.__cc.isHeating()})
        else:
            basic_logger.info("What do you mean? heating status :%s is unknown" % status)
            return jsonify({'action': 'None',
                            'status': 'failed'})
            
    def measure(self, status):
        if status =="light":
            return jsonify({'action': 'chicken_coop.measureLight()',
                            'data': self.__cc.getTemperature(),
                            'status': 'done'})
        elif status == "brightness":
            return jsonify({'action': 'chicken_coop.measureBrightness()',
                            'data': self.__cc.getBrightness(),
                            'status': 'done'}) 
        else:
            basic_logger.info("What do you mean? measurement:%s is unknown" % status)
            return jsonify({'action': 'None',
                            'status': 'failed'})
