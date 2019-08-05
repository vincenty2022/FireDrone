################################################################################
# Descrption: Creates a heat map-style image in indicator.png for testing
# purposes
################################################################################

from droneClass import Drone

import json
from PIL import Image
import numpy as np

def create_image(pix_arr):
    img = Image.new('RGBA', (500, 500))
    pixel_map = img.load()

    for y in range(500):
        for x in range(500):
            if pix_arr[y][x] == 1:
                pixel_map[x, y] = (255, 0, 0)
    return img

api_key = 'cyg-yPk*NBPKa!?%F73$$&8a6y7viE*d8_j$uYL2qnsgEndnWWz^q*zh!FO-d!jJ'
run = Drone(api_key)
last_five = run.get_all_history()['directRuns'][-5:]
i = 1
for id in last_five:
    print(f'{i}. {id}')
    i+=1

val = input()
index = int(val) - 1
data = run.get_history_entry(last_five[index])
data = json.loads(data['content'])
data = data['Events']
pixels = ''

for obj in data:
    if obj['EventType'] == 9:
        pixels = obj['EventDetails']
        break

pixel_array = []
if pixels != '':
    temp_array = []
    for i in range(len(pixels)):
        temp_array.append(int(pixels[i]))

    for i in range(500):
        start = i * 500
        pixel_array.append(temp_array[start:start + 500])

    pixel_array = np.array(pixel_array)
    print(pixel_array[0][0])
    img = create_image(pixel_array)
    img.save('./resources/indicator.png')

else:
    print('Empty')
