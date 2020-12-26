#!/usr/bin/python

from datetime import datetime
from datetime import timedelta
import time
import atexit
import os
import sys
import shutil
import RPi.GPIO as GPIO

from wrappers import GPhoto
from wrappers import Identify
from wrappers import NetworkInfo

from config_persist import Persist

import subprocess
import logging
import signal

__version__ = "1.0"
MIN_INTER_SHOT_DELAY_SECONDS = timedelta(seconds=60)
MIN_BRIGHTNESS = 12000
MAX_BRIGHTNESS = 17000
IMAGE_DIRECTORY = "/var/lib/timelapse/img/"
TMP_DIRECTORY = "/tmp/"
SETTINGS_FILE = "/var/lib/timelapse/settings.cfg"
INIT_CONFIG = 20
INIT_SHOT = 0
INIT_FLASH = False
SLEEP_TIME = 1
FLASH_THRESHOLD = 19
LOG_FILENAME = '/var/log/timelapse.log'

outPin = 21
RELAY = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(outPin, GPIO.OUT)
GPIO.setup(RELAY, GPIO.OUT)

# Canon camera shutter settings
CONFIGS = [(48, "1/1600", 2, 100),
    (46, "1/1000", 2, 100),
    (45, "1/800", 2, 100),
    (43, "1/500", 2, 100),
    (41, "1/320", 2, 100),
    (40, "1/250", 2, 100),
    (29, "1/200", 2, 100),
    (38, "1/160", 2, 100),
    (36, "1/100", 2, 100),
    (35, "1/80", 2, 100),
    (34, "1/60", 2, 100),
    (33, "1/50", 2, 100),
    (32, "1/40", 2, 100),
    (31, "1/30", 2, 100),
    (29, "1/20", 2, 100),
    (28, "1/15", 2, 100),
    (27, "1/13", 2, 100),
    (26, "1/10", 2, 100),
    (24, "1/6", 2, 100),
    (23, "1/5", 2, 100),
    (22, "1/4", 2, 100),
    (21, "0.3", 2, 100),
    (19, "0.5", 2, 100),
    (18, "0.6", 2, 100),
    (17, "0.8", 2, 100),
    (16, "1", 2, 100),
    (14, "1.6", 2, 100),
    (12, "2.5", 2, 100),
    (11, "3.2", 2, 100),
    ( 9, "5", 2, 100),
    ( 7, "8", 2, 100),
    ( 6, "10", 2, 100),
    ( 5, "13", 2, 100),
    ( 4, "15", 2, 100),
    ( 3, "20", 2, 100),
    ( 1, "30", 2, 100),
    ( 1, "30", 3, 200),
    ( 1, "30", 4, 400),
    ( 1, "30", 4, 800),
    ( 1, "30", 5, 1600)]



class App():

    def __init__(self):
        self.camera = GPhoto(subprocess)
        self.idy = Identify(subprocess)
        self.netinfo = NetworkInfo(subprocess)
        self.shot = 0

        self.displaySet = False

    def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        GPIO.cleanup()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    def startup(self):
        logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO, format='%(asctime)s %(message)s')
        logging.info('Started %s' % __file__)
        logging.info("Timelapse Version %s"%__version__)

        time.sleep(SLEEP_TIME)

        self.getNetwork()
        self.getModel()

        self.shoot()

    def run(self):
        self.startup()

    def showConfig(self, current):
        config = CONFIGS[current]
        logging.info("Timelapse\nT:%s ISO:%d" % (config[1], int(config[3])))

    def showStatus(self, shot, current):
        config = CONFIGS[current]
        logging.info("Shot %d\nT:%s ISO:%d" % (shot, config[1], int(config[3])))

    def getNetwork(self):
        network_status = self.netinfo.network_status()
        logging.info(network_status)

    def handleLight(self, enabled):
        if (enabled):
            GPIO.output(outPin,True)
        else:
            GPIO.output(outPin,False)

    def turnLightOn(self):
        self.handleLight(True)

    def turnLightOff(self):
        self.handleLight(False)

    def stop(self, mode):
        logging.info("Goodbye!")
        if mode == "exit":
            logging.info("End")
            sys.exit()
        if mode == "shutdown":
            logging.info("Shutown")
            os.system("sudo shutdown -h now")

    def testConfigs(self):
        print("Testing Configs")
        camera = GPhoto(subprocess)

        for config in CONFIGS:
            print("Testing camera setting: Shutter: %s ISO %d" % (config[1], config[3]))
            camera.set_shutter_speed(secs=config[1])
            camera.set_iso(iso=str(config[3]))
            time.sleep(SLEEP_TIME)

    def main(self):
        self.testConfigs()

    def getModel(self):
        model = "undef"
        try:
            model = self.camera.get_model()
        except Exception, e:
            raise Exception(str(e))

        logging.info(model)
        time.sleep(SLEEP_TIME)

    def shoot(self):
        persist = Persist()

        try:
            settings = persist.readLastConfig(INIT_CONFIG, INIT_SHOT, INIT_FLASH, SETTINGS_FILE)
            logging.info("Settings: " +str(settings))
            current_config = settings["lastConfig"]
            flash_on = settings["flashOn"]
            self.shot = settings["lastShot"] + 1

            prev_acquired = None
            last_acquired = None
            last_started = None
            been_over = False

            while True:
                last_started = datetime.now()
                config = CONFIGS[current_config]
                logging.info("Shot: %d T: %s ISO: %d" % (self.shot, config[1], config[3]))
                print "Shot: %d T: %s ISO: %d" % (self.shot, config[1], config[3])
                try:
                    self.camera.set_shutter_speed("1/60")
                    self.camera.set_iso(iso="200")
                except Exception, e:
                    logging.info("Error setting configs")
                try:
                    GPIO.output(RELAY,True)
                    time.sleep(1)
                    filename = self.camera.capture_image_and_download(shot=self.shot, image_directory=TMP_DIRECTORY)
                except Exception, e:
                    logging.error("Error on capture." + str(e))
                    print "Error on capture." + str(e)
                    print "Retrying..."
                    # Occasionally, capture can fail but retries will be successful.
                    continue
		GPIO.output(RELAY,False)
                prev_acquired = last_acquired
                # brightness = float(self.idy.mean_brightness(TMP_DIRECTORY+filename))
                last_acquired = datetime.now()
                persist.writeLastConfig(current_config, self.shot, 0, SETTINGS_FILE, flash_on)

                logging.info("Shot: %d File: %s Brightness: %s Flash: %s Been Over: %s" % (self.shot, filename, 0, flash_on, been_over))

                os.rename(TMP_DIRECTORY+filename, IMAGE_DIRECTORY+filename)
                been_over = False
                self.shot += 1
                if last_started and last_acquired and last_acquired - last_started < MIN_INTER_SHOT_DELAY_SECONDS:
                    logging.info("Sleeping for %s" % str(MIN_INTER_SHOT_DELAY_SECONDS - (last_acquired - last_started)))
                    print "Sleeping for %s" % str(MIN_INTER_SHOT_DELAY_SECONDS - (last_acquired - last_started))

                    time.sleep((MIN_INTER_SHOT_DELAY_SECONDS - (last_acquired - last_started)).seconds)
        except Exception,e:
            logging.error("Error: %s" %(str(e)))
            print "Error: %s" %(str(e))

        def exit_handler():
            print 'Shooting aborted!'

        # https://docs.python.org/2/library/atexit.html
        atexit.register(exit_handler)

if __name__ == "__main__":
    app = App().run()
