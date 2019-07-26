from droneClass import Drone
import io
from PIL import Image

api_key = 'cyg-yPk*NBPKa!?%F73$$&8a6y7viE*d8_j$uYL2qnsgEndnWWz^q*zh!FO-d!jJ'

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

def reverse_run(droneInstance):
    run.startRun()

    if droneInstance.canceled:
        return

    # zero to bottom left corner
    while droneInstance.moveLeft():
        pass

    imgStor = []

    imgStor.append(horiz_scan(run, 'right', 500))

    while run.moveUp():
        height = 100
        for _ in range(4):
            success = run.moveUp()
            if success:
                height += 100
            else:
                break

        imgStor.append(horiz_scan(run, 'left', height))

        while run.moveUp():
            height2 = 100
            for _ in range(4):
                success = run.moveUp()
                if success:
                    height2 += 100
                else:
                    break

            imgStor.append(horiz_scan(run, 'right', height2))

    result = combine_imrows(imgStor)
    result.save('./stitched.png')

    run.endRun()

run = Drone(api_key)
reverse_run(run)
# run.endRun('69b30efc-b660-4ee2-a726-12b5d4557c8e')
