#!/usr/bin/env python3
"""Ascending method.

For more details about the 'ascending method', have a look at
https://github.com/franzpl/audiometer/blob/master/docu/docu_audiometer.ipynb
The 'ascending method' is described in chapter 3.1.1

**WARNING**: If the hearing loss is too severe, this method will
not work! Please, consult an audiologist!

**WARNUNG**: Bei extremer Schwerhörigkeit ist dieses Verfahren nicht
anwendbar! Bitte suchen Sie einen Audiologen auf!

"""

import sys
import logging
import time
from audiometer import controller
from audiometer import audiogram


logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s',
                    handlers=[logging.FileHandler("logfile.log", 'w'),
                              logging.StreamHandler()])


class AscendingMethod:
    print("\n\n\n\n*****************************************************************WELCOME!!**********************************************************************************)
    time.sleep(3)
    
    print("\n\nREAD THE INSTRUCTIONS CAREFULLY BEFORE THE TEST BEGINS\n\n1) To begin with decrease or increase the tone intensity with '1' or '2' NUM KEYS according to the hearing comfort\n2) Once the desired tone level is set press on the space bar to proceed for the test\n3) Click the button once to begin the test\n4) Kindly press and hold the button whenever the played tone is heard to you each time")
    time.sleep(10)

    def __init__(self):
        self.ctrl = controller.Controller()
        self.current_level = 0
        self.click = True
          
        print("\n\nREADY!!, click the button to begin")
        self.ctrl.wait_for_click()

    def decrement_click(self, level_decrement):

        self.current_level -= level_decrement
        self.click = self.ctrl.clicktone(self.freq, self.current_level,
                                         self.earside)

    def increment_click(self, level_increment):

        self.current_level += level_increment
        self.click = self.ctrl.clicktone(self.freq, self.current_level,
                                         self.earside)

    def familiarization(self):
        logging.info("Begin Familiarization")

        print("\nSet a clearly audible tone "
              "via the '1' and '2' num keys ('1' num key decreases the tone by 10dB, '2' num key increases the tone by 5dB) on the keypad")
        time.sleep(3)
          
        print("Press the Space key once the tone is set")

        self.current_level = self.ctrl.audibletone(
                             self.freq,
                             self.ctrl.config.beginning_fam_level,
                             self.earside)

        

    def hearing_test(self):
        self.familiarization()
          
        print("\n\n\nTo begin the test, click once\nPress and hold the button until the tone is heard")
        self.ctrl.wait_for_click()
          
          
        while self.click:
            logging.info("End Familiarization: -%s",
                     self.ctrl.config.major_decrement)
        self.decrement_click(self.ctrl.config.major_decrement)

        while not self.click:
            logging.info("+%s", self.ctrl.config.minor_increment)
            self.increment_click(self.ctrl.config.minor_increment)

        current_level_list = []
        current_level_list.append(self.current_level)

        two_answers = False
        while not two_answers:
            logging.info("2of3?: %s", current_level_list)
            for x in range(3):
                while self.click:
                    logging.info("-%s", self.ctrl.config.minor_decrement)
                    self.decrement_click(
                        self.ctrl.config.minor_decrement)

                while not self.click:
                    logging.info("+%s", self.ctrl.config.minor_increment)
                    self.increment_click(
                        self.ctrl.config.minor_increment)

                current_level_list.append(self.current_level)
                logging.info("2of3?: %s", current_level_list)
                # http://stackoverflow.com/a/11236055
                if [n for n in current_level_list
                   if current_level_list.count(n) == 2]:
                    two_answers = True
                    logging.info("2of3 --> True")
                    break
            else:
                logging.info("No Match! --> +%s",
                             self.ctrl.config.major_increment)
                current_level_list = []
                self.increment_click(self.ctrl.config.major_increment)

    def run(self):

        if not self.ctrl.config.logging:
            logging.disable(logging.CRITICAL)

        for self.earside in self.ctrl.config.earsides:
            for self.freq in self.ctrl.config.freqs:
                logging.info('freq:%s earside:%s', self.freq, self.earside)
                try:
                    self.hearing_test()
                    self.ctrl.save_results(self.current_level, self.freq,
                                           self.earside)

                except OverflowError:
                    print("The signal is distorted. Possible causes are "
                          "an incorrect calibration or a severe hearing "
                          "loss. I'm going to the next frequency.")
                    self.current_level = None
                    continue

                except KeyboardInterrupt:
                    sys.exit('\nInterrupted by user')

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.ctrl.__exit__()
        audiogram.make_audiogram(self.ctrl.config.filename,
                                 self.ctrl.config.results_path)

if __name__ == '__main__':

    with AscendingMethod() as asc_method:
        asc_method.run()

    print("Finished!")
