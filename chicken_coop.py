# import pigpio
# from pi1wire import Pi1Wire, W1Driver, OneWire

import settings
import time


chicken_coop = None
class ChickenCoop:
    """A Class integrating all sensors and outputs available"""

 
    def __init__(self):        
        chicken_coop = self
        
        try:
            self.pi = pigpio.pi()
            if not self.pi.connected:
                print("OOps i couldn't connect to the pigpio daemon!")
            else:
                print("Setting Up Output Pins")
                
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
                
                print("Setting Up Input Pins")
                
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
            
            print("Connected to temperature sensor")
            
            #
            # Init Brightness Sensor
            #
            
            self.heating = False
            
            print("Connected to temperature sensor")
            
        except Exception as e:
            print("OOps i f***** it up while looking for temperature sensors\n %s" % e)

    def lightOn(self):
        print("Not Implemented Yet")
        
    def lightOff(self):
        print("Not Implemented Yet")
    
    @staticmethod    
    def callbackUp(gpio, level, tick):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        # print('Zeitpunkt: %s  Level: %i on GPIO %i' % (current_time, level, gpio))
        chicken_coop.doorOpen()
        
    
    @staticmethod
    def callbackDown(gpio, level, tick):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        # print('Zeitpunkt: %s  Level: %i on GPIO %i' % (current_time, level, gpio))
        chicken_coop.doorClose()
    
    
    def heatingOn(self):
        self.heating = True
        self.pi.write(settings.pin_relais_in_1, 0)

    def heatingOff(self):
        self.heating = False
        self.pi.write(settings.pin_relais_in_1, 1)
    
    def doorOpen(self):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        print('Zeitpunkt: %s Open Door Signal' % (current_time))
        
        self.pi.write(settings.pin_relais_in_3, 0)
        time.sleep(0.5)
        self.pi.write(settings.pin_relais_in_3, 1)
        

    def doorClose(self):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        print('Zeitpunkt: %s Close Door Signal' % (current_time))
        
        self.pi.write(settings.pin_relais_in_4, 0)
        time.sleep(0.5)
        self.pi.write(settings.pin_relais_in_4, 1)
        
    def getTemperature(self):
        current_temperature = self.temp_sensor.get_temperature()
        return current_temperature
        
    def isHeating(self):
        return self.heating
    
    
    # def run(self):
    #     while (True):
    #         try:  
    #             current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                
                
    #             # print('Zeitpunkt: %s  Temperatur: %.2f °C' % (current_time, current_temperature))
                

                
    #             time.sleep(1.)
                
    #         except KeyboardInterrupt:
    #             print('Byebye')
    #             break
    #         except Exception as e:
    #             print('Another Error happend: %s' % e)
    #             break
    
    def __del__(self):
        self.heatingOff()
        self.lightOff()
        self.pi.stop()
