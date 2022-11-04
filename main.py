#!/usr/bin/python3

import time
import logging
import threading
from flask import Flask

import settings
from chicken_coop_commander import ChickenCoopCommander
from chicken_coop import ChickenCoop





if __name__ == "__main__":

    data_formatter = logging.Formatter('%(asctime)s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    
    temp_logger = logging.getLogger("Temperature_Sensor")
    temp_handler = logging.FileHandler(settings.TEMP_LOGS)
    temp_handler.setFormatter(data_formatter)
    temp_logger.setLevel(logging.INFO)
    temp_logger.addHandler(temp_handler)
    
    brightness_logger = logging.getLogger("Brightness_Sensor")
    brightness_handler = logging.FileHandler(settings.TEMP_LOGS)
    brightness_handler.setFormatter(data_formatter)
    brightness_logger.setLevel(logging.INFO)
    brightness_logger.addHandler(temp_handler)
    
    logging.basicConfig(
        format="%(asctime)s: %(message)s", 
        level=logging.INFO,
        datefmt="%Y-%m-%D %H:%M:%S")
        # filename="output.log")

    logging.info("Starting Up The ChickenScoop Module")
    
    try:
        cc = ChickenCoop()
        cc_cmd = ChickenCoopCommander(cc)
        
        cc_cmd.run()
        
    except Exception as e:
        logging.info('Another Error happend: %s', e)
        