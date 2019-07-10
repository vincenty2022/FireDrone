# for simplification of use of FireDrone client. Configured to automatically
# create new run_id upon creation of drone object.
#
# Available public functions:
#
#     startRun(scene_number)              starts a directrun and creates run_id
#     endRun(run_id = self.run_id)        ends run
#     droneDisp()                         displays drone frame as frame.png
#     moveUp(repeat = 1)                  moves up with a repeat value
#     moveDown(" ")
#     moveLeft(" ")
#     moveRight(" ")





import firedrone.client as fdc
from firedrone.client.errors import FireDroneClientHttpError
import os
from IPython.display import Image

class Drone:
    def __init__(self, api_key):
        self.api_key = api_key
        self.workspace = fdc.Workspace(api_key)
        self.run_id = -1        # defaults to error value

    def startRun(self, scene_num):
        try:
            start_result = self.workspace.directrun_start(scene_num)
            run_id = start_result.get('uniqueId')
            self.run_id = run_id
        except FireDroneClientHttpError as e:
            print(e)
            print("Run ended")

    def endRun(self, run_id = -1):
        # change run_id such that default is always self.run_id
        if run_id == -1:
            run_id = self.run_id
        self.workspace.directrun_end(run_id)
        print("Done!")

    # check if a direct run has been started
    def __check_run(self):
        if self.run_id == -1:
            raise Exception('No direct run started!')

    # set frame.png to current image
    def droneDisp(self):
        self.__check_run()
        frame = self.workspace.get_drone_fov_image(self.run_id)
        with open('./frame.png', 'wb') as f:
            f.write(frame)

    # motion functions. Will return true or false for success
    def moveUp(self, repeat = 1):
        self.__check_run()
        for _ in range(repeat):
            move_result = self.workspace.directrun_move_up(self.run_id)
            if move_result.get('success') == False:
                break
        return move_result.get('success')

    def moveDown(self, repeat = 1):
        self.__check_run()
        for _ in range(repeat):
            move_result = self.workspace.directrun_move_down(self.run_id)
            if move_result.get('success') == False:
                break
        return move_result.get('success')


    def moveRight(self, repeat = 1):
        self.__check_run()
        for _ in range(repeat):
            move_result = self.workspace.directrun_move_right(self.run_id)
            if move_result.get('success') == False:
                break
        return move_result.get('success')

    def moveLeft(self, repeat = 1):
        self.__check_run()
        for _ in range(repeat):
            move_result = self.workspace.directrun_move_left(self.run_id)
            if move_result.get('success') == False:
                break
        return move_result.get('success')

# testing
api_key = 'cyg-yPk*NBPKa!?%F73$$&8a6y7viE*d8_j$uYL2qnsgEndnWWz^q*zh!FO-d!jJ'

test = Drone(api_key)

test.startRun(21)
test.moveUp()
test.moveUp(15000)
test.moveLeft(15000)
test.moveRight(15000)
test.moveDown(15000)
test.droneDisp()
test.endRun()

# use in case of code breaks and manual override is required
# test.endRun()
