from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import readchar

from droneClass import Drone
from predictor import analyze

api_key = 'cyg-yPk*NBPKa!?%F73$$&8a6y7viE*d8_j$uYL2qnsgEndnWWz^q*zh!FO-d!jJ'
image_path = './resources/frame.png'                  # file path that current fov is saved to for direct_run

# displays drone images on matplotlib display
def matplotDisp(droneInstance, ax):
    img = np.array(Image.open(image_path), dtype=np.uint8)
    ax.imshow(img)
    plt.pause(1)

# writes to frame.png
def droneDisp(droneInstance):
    droneInstance.check_run()
    frame = droneInstance.getFrame()
    with open(image_path, 'wb') as f:
        f.write(frame)

# starts direct run
def directRun(droneInstance, init_x = 0, init_y = 0):
    if droneInstance.canceled == True:
        return

    droneInstance.check_run()
    print("Enabling Manual Run. Use wasd to move, q to quit, e to analyze")

    # zeroes to bottom left
    while droneInstance.moveLeft():
        pass
    while droneInstance.moveDown():
        pass

    x = 0
    y = 0

    # go to initial coords
    while not (x == init_x and y == init_y):
        diff_x = init_x - x
        diff_y = init_y - y

        if diff_x > 0:
            droneInstance.moveRight()
            x+=1
        elif diff_x < 0:
            droneInstance.moveLeft()
            x-=1

        if diff_y > 0:
            droneInstance.moveUp()
            y+=1
        elif diff_x < 0:
            droneInstance.moveDown()
            y-=1

    # initialize display
    fig, ax = plt.subplots()
    coord_text = fig.text(0.9, 0.05, f'({x}, {y})', fontsize=10)
    droneDisp(droneInstance)
    matplotDisp(droneInstance, ax)

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
            if droneInstance.moveUp():
                y+=1
            coord_text.set_text(f'({x}, {y})')

            droneDisp(droneInstance)
            matplotDisp(droneInstance, ax)

        if val == 'a':                  # Left
            # coordinates
            if droneInstance.moveLeft():
                x-=1
            coord_text.set_text(f'({x}, {y})')

            droneDisp(droneInstance)
            matplotDisp(droneInstance, ax)

        if val == 's':                  # Down
            # coordinates
            if droneInstance.moveDown():
                y-=1
            coord_text.set_text(f'({x}, {y})')

            droneDisp(droneInstance)
            matplotDisp(droneInstance, ax)

        if val == 'd':                  # Right
            # coordinates
            if droneInstance.moveRight():
                x+=1
            coord_text.set_text(f'({x}, {y})')

            droneDisp(droneInstance)
            matplotDisp(droneInstance, ax)

        if val == 'e':                  # Pass to vision
            analyzer = analyze('./resources/frame.png')
            patch = analyzer.dispPredict(droneInstance, ax)
            print('Analysis complete')

        if val == 'q':                  # Quit
            print ("Disabling Direct Run")
            plt.close()
            break
    plt.show()

if __name__ == '__main__':

    run = Drone(api_key)
    run.startRun()
    directRun(run)
    run.endRun()
