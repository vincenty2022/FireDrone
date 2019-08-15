################################################################################
# Description: runs reverse_run. Scans the entire scene, stitches the images
# together, identifies the fires, and exports a clean image of the scene, an
# image of the scene marked with fire, and a json fire containing coordinates
# of the instances of fire to Azure Blob Storage.
################################################################################
from azure.storage.blob import BlockBlobService, PublicAccess

from droneClass import Drone
import io
from PIL import Image
import json
import datetime as dt
import os

from predictor import analyze


# FireDrone api_key
api_key = 'cyg-yPk*NBPKa!?%F73$$&8a6y7viE*d8_j$uYL2qnsgEndnWWz^q*zh!FO-d!jJ'

#################### AZURE STORAGE SPECIFIC VARIABLES ##########################
# Azure blob storage info
account_name = 'account_name'
account_key = 'account_key'
################################################################################

def horiz_scan(droneInstance, direction, height):
    img = droneInstance.getFrame()
    img = Image.open(io.BytesIO(img))

    if direction == 'right':
        while droneInstance.moveRight():
            frame_width = 100

            for _ in range(4):
                success = droneInstance.moveRight()
                if success:
                    frame_width += 100
                else:
                    break

            curr_frame = droneInstance.getFrame()
            curr_frame = Image.open(io.BytesIO(curr_frame))

            if not frame_width == 500:
                curr_frame = curr_frame.crop((500 - frame_width, 0, 500, height))

            w1, _ = img.size
            w2, _ = curr_frame.size

            merge = Image.new('RGB', (w1 + w2, height))
            merge.paste(img, (0,0))
            merge.paste(curr_frame, (w1, 0))

            img = merge

    elif direction == 'left':
        while droneInstance.moveLeft():
            frame_width = 100

            for _ in range(4):
                success = droneInstance.moveLeft()
                if success:
                    frame_width += 100
                else:
                    break

            curr_frame = droneInstance.getFrame()
            curr_frame = Image.open(io.BytesIO(curr_frame))

            if not frame_width == 500:
                curr_frame = curr_frame.crop((0, 0, frame_width, height))

            w1, _ = img.size
            w2, _ = curr_frame.size

            merge = Image.new('RGB', (w1 + w2, height))
            merge.paste(img, (w2,0))
            merge.paste(curr_frame, (0, 0))

            img = merge

    return img

def combine_imrows(row_array):
    img = row_array.pop(0)
    for row in row_array:
        w, h1 = img.size
        _, h2 = row.size

        merge = Image.new('RGB', (w, h1 + h2))
        merge.paste(row, (0, 0))
        merge.paste(img, (0, h2))

        img = merge

    return img

def output_to_cloud(image, coords, scene_num):
    # variables for naming container
    is_fire = not len(coords) == 0
    year = dt.datetime.now().year
    month = dt.datetime.now().month
    day = dt.datetime.now().day
    hour = dt.datetime.now().hour
    minute = dt.datetime.now().minute

    folderpath = os.getcwd()

    image.save('./resources/marked.png')

    # format for json export
    data = {}
    data['fires'] = []

    for pair in coords:
        x, y = pair

        data['fires'].append({
            'x': x,
            'y': y
        })

    with open('./resources/coordinates.json', 'w') as f:
        json.dump(data, f)

    service = BlockBlobService(account_name, account_key)

    container_name = ''

    if is_fire:
        container_name = f'fire-{scene_num}-{year}-{month}-{day}-{hour}-{minute}'
    else:
        container_name = f'safe-{scene_num}-{year}-{month}-{day}-{hour}-{minute}'

    # export to blob storage
    service.create_container(container_name)
    service.set_container_acl(container_name, public_access=PublicAccess.Container)

    service.create_blob_from_path(container_name, 'scene_image.png', os.path.join(folderpath, 'resources\stitched.png'))
    service.create_blob_from_path(container_name, 'marked_scene_image.png', os.path.join(folderpath, 'resources\marked.png'))
    service.create_blob_from_path(container_name, 'drone_coordinates.json', os.path.join(folderpath, 'resources\coordinates.json'))


def reverse_run(droneInstance):
    scene_num = droneInstance.scene_num

    if droneInstance.canceled:
        return

    # zero to bottom left corner
    while droneInstance.moveLeft():
        pass

    imgStor = []

    imgStor.append(horiz_scan(droneInstance, 'right', 500))

    while droneInstance.moveUp():
        height = 100
        for _ in range(4):
            success = droneInstance.moveUp()
            if success:
                height += 100
            else:
                break

        imgStor.append(horiz_scan(droneInstance, 'left', height))

        while droneInstance.moveUp():
            height2 = 100
            for _ in range(4):
                success = droneInstance.moveUp()
                if success:
                    height2 += 100
                else:
                    break

            imgStor.append(horiz_scan(droneInstance, 'right', height2))

    result = combine_imrows(imgStor)
    result.save('./resources/stitched.png')

    analyzer = analyze('./resources/stitched.png')
    image, coordinates = analyzer.imgPredict()

    output_to_cloud(image, coordinates, scene_num)

# runs it
if __name__ == "__main__":

    run = Drone(api_key)
    run.startRun()
    reverse_run(run)
    run.endRun()
