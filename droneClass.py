# for simplification of use of FireDrone client. Configured to automatically
# create new run_id upon creation of drone object.
#
# Available public functions:
#
#     startRun(scene_number)                        scene_number can be inputted in code, otherwise it is prompted for
#     endRun(run_id = self.run_id)                  ends run
#     check_run()                                   check if a valid run_id exists
#
#     getFrame()                                    returns current drone fov
#     moveUp()                                      moves up 100 pixels
#     moveDown()                                    down 100 pix
#     moveLeft()                                    left 100 pix
#     moveRight()                                   right 100 pix

import firedrone.client as fdc
from firedrone.client.errors import FireDroneClientHttpError
import os

import numpy as np
from PIL import Image

class Drone:
    def __init__(self, api_key):
        self.api_key = api_key
        self.workspace = fdc.Workspace(api_key)
        self.run_id = -1        # defaults to error value
        self.scenes = self.workspace.get_scenes()
        self.canceled = False
        self.scene_num = -1

    def __printScenes(self):
        print(self.scenes)

    def checkScenes(self, input):
        input = str(input)
        for d in self.scenes:
            val = str(d['id'])
            if val == input:
                return True
        return False

    # start a run. Either select a scene_number or provide it in code
    def startRun(self, scene_num = -1):
        # scene_num is not provided in code
        if scene_num == -1:
            self.__printScenes()

            scene_num = input('Cancel with "q". Select a scene ID: ')

            if self.checkScenes(scene_num):
                try:
                    self.scene_num = scene_num
                    start_result = self.workspace.directrun_start(scene_num)
                    run_id = start_result.get('uniqueId')
                    self.run_id = run_id
                except FireDroneClientHttpError as e:
                    print(e)
            elif scene_num == 'q':
                print('Cancelling')
                self.canceled = True
                return
            else:
                print('Not a valid input')
                self.startRun()

        # scene_num is provided in code
        else:
            print(scene_num)
            if self.checkScenes(scene_num):
                try:
                    self.scene_num = scene_num
                    start_result = self.workspace.directrun_start(scene_num)
                    run_id = start_result.get('uniqueId')
                    self.run_id = run_id
                except FireDroneClientHttpError as e:
                    print(e)
            elif scene_num == 'q':
                self.canceled = True
                return
            else:
                print('Not a valid input')

    def endRun(self, run_id = -1):
        if self.canceled == True:
            return

        # change run_id such that default is always self.run_id
        if run_id == -1:
            run_id = self.run_id
        self.workspace.directrun_end(run_id)
        print("Done!")

    # check if a direct run has been started
    def check_run(self):
        if self.run_id == -1:
            raise Exception('No direct run started or previous not closed')

    def getFrame(self):
        self.check_run()
        return self.workspace.get_drone_fov_image(self.run_id)

    # motion functions. Will return true or false for success
    def moveUp(self):
        self.check_run()
        move_result = self.workspace.directrun_move_up(self.run_id)
        return move_result.get('success')

    def moveDown(self):
        self.check_run()
        move_result = self.workspace.directrun_move_down(self.run_id)
        return move_result.get('success')

    def moveRight(self):
        self.check_run()
        move_result = self.workspace.directrun_move_right(self.run_id)
        return move_result.get('success')

    def moveLeft(self):
        self.check_run()
        move_result = self.workspace.directrun_move_left(self.run_id)
        return move_result.get('success')

# testing
if __name__ == '__main__':

    api_key = 'cyg-yPk*NBPKa!?%F73$$&8a6y7viE*d8_j$uYL2qnsgEndnWWz^q*zh!FO-d!jJ'

    test = Drone(api_key)
    test.startRun()
    test.endRun()

    # use in case of code breaks and manual override is required, use endRun(run_key)
    # test.endRun()
