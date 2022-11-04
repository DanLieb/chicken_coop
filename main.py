#!/usr/bin/python3

import time
import logging
import threading
from flask import Flask

# import settings
from chicken_coop_commander import ChickenCoopCommander
from chicken_coop import ChickenCoop





if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    
    logging.basicConfig(
        format=format, 
        level=logging.INFO,
        datefmt="%Y-%m-%D %H:%M:%S")
        # filename="output.log")

    logging.info("Starting in __main__")
    
    try:
        cc = ChickenCoop()
        cc_cmd = ChickenCoopCommander(cc)
        
        cc_cmd.run()
        
    except Exception as e:
        logging.info('Another Error happend: %s', e)
        