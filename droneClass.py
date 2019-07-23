# for simplification of use of FireDrone client. Configured to automatically
# create new run_id upon creation of drone object.
#
# Available public functions:
#
#     startRun(scene_number)                        starts a directrun on specified scene and creates run_id
#     endRun(run_id = self.run_id)                  ends run
#     __droneDisp()                                 displays drone frame as frame.png
#     directRun(initial_x = 0, inital_y = 0)        call after startRun(). Allows manual control and testing.
#     __moveUp(repeat = 1)                          moves up with a repeat value
#     __moveDown(" ")
#     __moveLeft(" ")
#     __moveRight(" ")

import firedrone.client as fdc
from firedrone.client.errors import FireDroneClientHttpError
import os
from IPython.display import Image
import readchar

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
import numpy as np
from PIL import Image

from predictor import analyze

class Drone:
    def __init__(self, api_key):
        self.api_key = api_key
        self.workspace = fdc.Workspace(api_key)
        self.run_id = -1        # defaults to error value
        self.image_path = "./frame.png"
        self.scenes = self.workspace.get_scenes()
        self.canceled = False

    def __printScenes(self):
        print(self.scenes)

    def __checkScenes(self, input):
        for dict in self.scenes:
            val = str(dict['id'])
            if val == input:
                return True
        return False

    def startRun(self):
        self.__printScenes()
        scene_num = input('Cancel with "e". Select a scene ID: ')

        print(scene_num)

        if self.__checkScenes(scene_num):
            try:
                start_result = self.workspace.directrun_start(scene_num)
                run_id = start_result.get('uniqueId')
                self.run_id = run_id
            except FireDroneClientHttpError as e:
                print(e)
        elif scene_num == 'e':
            print('Cancelling')
            self.canceled = True
            return
        else:
            print('Not a valid ID!')
            self.startRun()

    def __matplotDisp(self, ax):
        img = np.array(Image.open(self.image_path), dtype=np.uint8)
        ax.imshow(img)
        plt.pause(1)

    def directRun(self, init_x = 0, init_y = 0):
        if self.canceled == True:
            return

        self.__check_run()
        print("Enabling Manual Run. Use wasd to move, q to quit, e to analyze")

        # zeroes to bottom left
        while self.__moveLeft():
            pass
        x = 0
        y = 0

        # go to initial coords
        while not (x == init_x and y == init_y):
            diff_x = init_x - x
            diff_y = init_y - y

            if diff_x > 0:
                self.__moveRight()
                x+=1
            elif diff_x < 0:
                self.__moveLeft()
                x-=1

            if diff_y > 0:
                self.__moveUp()
                y+=1
            elif diff_x < 0:
                self.__moveDown()
                y-=1

        # initialize display
        fig, ax = plt.subplots()
        coord_text = fig.text(0.9, 0.05, f'({x}, {y})', fontsize=10)
        self.__droneDisp()
        self.__matplotDisp(ax)

        while True:
            print('Use wasd to move, q to quit, e to analyze')

            val = readchar.readkey()
            # cleaning up
            for p in reversed(ax.patches):
                p.remove()

            for t in reversed(ax.texts):
                t.remove()

            if val == 'w':                  # Up
                # coordinates
                if self.__moveUp():
                    y+=1
                coord_text.set_text(f'({x}, {y})')

                self.__droneDisp()
                self.__matplotDisp(ax)

            if val == 'a':                  # Left
                # coordinates
                if self.__moveLeft():
                    x-=1
                coord_text.set_text(f'({x}, {y})')

                self.__droneDisp()
                self.__matplotDisp(ax)

            if val == 's':                  # Down
                # coordinates
                if self.__moveDown():
                    y-=1
                coord_text.set_text(f'({x}, {y})')

                self.__droneDisp()
                self.__matplotDisp(ax)

            if val == 'd':                  # Right
                # coordinates
                if self.__moveRight():
                    x+=1
                coord_text.set_text(f'({x}, {y})')

                self.__droneDisp()
                self.__matplotDisp(ax)

            if val == 'e':                  # Pass to vision
                analyzer = analyze()
                patch = analyzer.dispPredict(ax)

            if val == 'q':                  # Quit
                print ("Disabling Manual Run")
                plt.close()
                break

        plt.show()

    def endRun(self, run_id = -1):
        if self.canceled == True:
            return

        # change run_id such that default is always self.run_id
        if run_id == -1:
            run_id = self.run_id
        self.workspace.directrun_end(run_id)
        print("Done!")

    # check if a direct run has been started
    def __check_run(self):
        if self.run_id == -1:
            raise Exception('No direct run started or previous not closed')

    # set frame.png to current image
    def __droneDisp(self):
        self.__check_run()
        frame = self.workspace.get_drone_fov_image(self.run_id)
        with open(self.image_path, 'wb') as f:
            f.write(frame)

    # motion functions. Will return true or false for success
    def __moveUp(self, repeat = 1):
        self.__check_run()
        for _ in range(repeat):
            move_result = self.workspace.directrun_move_up(self.run_id)
            if move_result.get('success') == False:
                break
        return move_result.get('success')

    def __moveDown(self, repeat = 1):
        self.__check_run()
        for _ in range(repeat):
            move_result = self.workspace.directrun_move_down(self.run_id)
            if move_result.get('success') == False:
                break
        return move_result.get('success')

    def __moveRight(self, repeat = 1):
        self.__check_run()
        for _ in range(repeat):
            move_result = self.workspace.directrun_move_right(self.run_id)
            if move_result.get('success') == False:
                break
        return move_result.get('success')

    def __moveLeft(self, repeat = 1):
        self.__check_run()
        for _ in range(repeat):
            move_result = self.workspace.directrun_move_left(self.run_id)
            if move_result.get('success') == False:
                break
        return move_result.get('success')

# testing
if __name__ == "__main__":

    api_key = 'cyg-yPk*NBPKa!?%F73$$&8a6y7viE*d8_j$uYL2qnsgEndnWWz^q*zh!FO-d!jJ'

    test = Drone(api_key)
    test.startRun()
    test.directRun(3, 3)
    test.endRun()

    # use in case of code breaks and manual override is required, use endRun(run_key)
    # test.endRun()
