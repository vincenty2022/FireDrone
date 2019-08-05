################################################################################
# Descrption: Imagined 'control panel code.' Allows user to select between
# continuously scanning a selected scene and exporting data to Azure Blob
# Storage (monitoring the scene), running a normal direct run, or starting a
# direct run centered on a previous detected fire using data stored in Azure
# Blob Storage.
################################################################################

from azure.storage.blob import BlockBlobService

import reverse_run
import direct_run
from droneClass import Drone

import keyboard
import time
import os
import json

################################################################################
# FireDrone API key
api_key = 'cyg-yPk*NBPKa!?%F73$$&8a6y7viE*d8_j$uYL2qnsgEndnWWz^q*zh!FO-d!jJ'

# Azure blob storage info
account_name = 'firedronestor'
account_key = 'dEvAqLZ2iU3WbvjehqVb/6d44hhMf5RpJlTpXXEdEeaR6bQtIeOJ6QWxmPjosJhsXdYLw22x/HeHfZi0v1H3Aw=='
################################################################################


continuous_run_time_interval = 300                       # time interval between consecutive reverse_runs

def continuous_reverse_run():
    run = Drone(api_key)
    print(run.scenes)
    scene_num = input("Select a scene. Press 'q' to quit: ")

    start = time.time()

    while run.run_id == -1:
        run.startRun(scene_num)

        if run.run_id != -1:
            break
        elif scene_num == 'q':
            print('Cancelling')
            return

        scene_num = input("Select a scene. Press 'q' to quit: ")

    reverse_run.reverse_run(run)
    run.endRun()

    print("Press 'q' to quit")

    while True:
        wait = True
        stop = False

        # Guaranteed 5 seconds to cancel
        if wait:
            wait_start = time.time()
            while (time.time() - wait_start < 5):
                if keyboard.is_pressed('q'):
                    print('Quitting')
                    stop = True
                    break

        if stop:
            break

        now = time.time()
        delay = now - start

        if delay >= continuous_run_time_interval:
            start = now

            run = Drone(api_key)
            run.startRun(scene_num)
            reverse_run.reverse_run(run)
            run.endRun()

            wait = True

            print("Press 'q' to quit")

def direct_run_by_container(droneInstance, blobservice, container_name):
    # data processing

    blobservice.get_blob_to_path(container_name, 'drone_coordinates.json', os.path.join(os.getcwd(), 'resources\coordinates.json'))
    scene_num = container_name.split('-')[1]
    scene_num = int(scene_num)

    droneInstance.startRun(scene_num)

    with open(r'resources\coordinates.json') as f:
        data = json.load(f)

    coords = []
    # reading from json
    for i in data['fires']:
        x, y = i['x'], i['y']
        coords.append((x, y))

    while True:
        for i in range(len(coords)):
            x, y = coords[i]
            print(f'{i + 1}. ({x}, {y})')

        index = input("Select a detected fire to start the direct_run on. Press 'q' to quit: ")
        try:
            index = int(index)
            index -= 1
            if 0 <= index < len(coords):
                direct_run.directRun(droneInstance, coords[index][0], coords[index][1])
            else:
                print('Invalid selection. Out of range')
        except ValueError:
            if index == 'q':
                break
            print('Invalid selection')

def input_direct_run():
    run = Drone(api_key)

    service = BlockBlobService(account_name, account_key)
    containers = service.list_containers()

    c_list = []

    for c in containers:
        c_list.append(c)

    if len(c_list) != 0:
        for i in range(len(c_list)):
            name = c_list[i].name
            print(f'{i+1}. {name}')

        print(f'{len(c_list) + 1}. Normal Direct Run')

        # select data of interest
        while True:
            index = input("Select the data you want to view. Press 'q' to quit: ")
            try:
                index = int(index)
                index -= 1
                if 0 <= index < len(c_list):                                    # select container index
                    container_name = c_list[index].name
                    direct_run_by_container(run, service, container_name)
                    break
                elif index == len(c_list):                                      # select the normal direct run option
                    print("Enabling normal direct_run")
                    run.startRun()
                    direct_run.directRun(run)
                    break
                else:                                                           # print and try again
                    print('Invalid input. Enter a value in the correct range')
            except ValueError:
                if index == 'q':                                                # cancel
                    print('Quitting')
                    return
                print('Invalid input. Enter an int')                            # print and try again

    else:                                                                       # there are no options
        print('No data available. Enabling normal direct_run')
        run.startRun()
        direct_run.directRun(run)

    run.endRun()

while True:
    key = input("Select '1' to enter continuous reverse_run or '2' to enter direct_run. Press 'q' to quit: ")
    if key == '1':
        continuous_reverse_run()
        break
    elif key == '2':
        input_direct_run()
        break
    elif key == 'q':
        break
    else:
        print('Not a valid input')

