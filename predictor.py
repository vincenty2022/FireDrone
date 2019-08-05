################################################################################
# Descrption: Defines analyze class which contains functions associated with
# the Azure Cognitive Services functionality
################################################################################

from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from PIL.ImageDraw import Draw
from PIL import ImageFont
import math
import numpy as np

##################### AZURE MODEL SPECIFIC VARIABLES ###########################
prediction_key = '9ef10c8af98c4b6eabba85f7a31a718d'
project_id = 'a3ee9e07-9016-443c-a300-a8bb7f3a0dba'
publishedName = 'BuildingsOnFire01'
ENDPOINT = 'https://westus2.api.cognitive.microsoft.com/'
fire_classifier = 'fire'            # Name of classifier in Custom Vision
smoke_classifier = 'smoke'          # Name of classifier in Custom Vision

# CALIBRATE FOR USE
fireThreshold = 0.15
smokeThreshold = 0.15
################################################################################

class analyze:
    def __init__(self, path_to_image_to_predict):
        self.model = CustomVisionPredictionClient(prediction_key, endpoint=ENDPOINT)
        self.fires = []
        self.smoke = []
        self.image_path = path_to_image_to_predict

    # updates using the self.image_path
    def predictUpdate(self):
        fires = []
        smoke = []

        with open(self.image_path, mode="rb") as test_data:
            results = self.model.detect_image(project_id, publishedName, test_data)

        for pred in results.predictions:
            if (pred.tag_name == fire_classifier and pred.probability >= fireThreshold):
                fires.append(pred)

        for pred in results.predictions:
            if (pred.tag_name == smoke_classifier and pred.probability >= smokeThreshold):
                smoke.append(pred)

        self.fires = fires
        self.smoke = smoke

    def __areBothEmpty(self):
        return (len(self.fires) == 0 and len(self.smoke) == 0)

    # returns original list after prediction
    def getFireSmoke(self):
        if self.__areBothEmpty():
            self.predictUpdate()
        return self.fires, self.smoke

    # returns two lists of distances from the center of frame
    def returnDistances(self):
        if self.__areBothEmpty():
            self.predictUpdate()

        fireDist = []
        smokeDist = []

        for inst in self.fires:
            x, y = inst.bounding_box.left, inst.bounding_box.top
            delta_x, delta_y = 0.5 - x, 0.5 - y
            dist = math.sqrt(delta_x**2 + delta_y**2)

            fireDist.append(dist)

        for inst in self.smoke:
            x, y = inst.bounding_box.left, inst.bounding_box.top
            delta_x, delta_y = 0.5 - x, 0.5 - y
            dist = math.sqrt(delta_x**2 + delta_y**2)

            fireDist.append(dist)

        return fireDist, smokeDist

    # boxes the object and labels with tag name and probability for matplotlib. for direct_run
    def __boxObject(self, obj_list, droneInstance, ax, im_width, im_height):
        scoring_array = [0] * 250000

        for inst in obj_list:
            x, y = inst.bounding_box.left * im_width, inst.bounding_box.top * im_height
            label = inst.tag_name
            probability = inst.probability

            # scale to frame dimensions
            pic_coord = (x, y)

            # dimensions of recognized region
            obj_width = inst.bounding_box.width*im_width
            obj_height = inst.bounding_box.height*im_height

            # display
            rect = patches.Rectangle(pic_coord, obj_width, obj_height, edgecolor = 'r', fill = False)
            plt.text(pic_coord[0], pic_coord[1],f'{label}: {round(probability, 3)}')

            ax.add_patch(rect)

            # scoring
            scoring_array = self.__score(scoring_array, x, y, obj_width, obj_height)

        # export to FireDrone
        droneInstance.score(scoring_array)

    # changes scoring array for one instance of fire. for direct_run
    def __score(self, scoring_array, top_left_x, top_left_y, width, height):
        width = int(round(width))
        height = int(round(height))
        top_left_x = int(round(top_left_x))
        top_left_y = int(round(top_left_y))
        arr_index = top_left_x + top_left_y * 500
        for _ in range(height):
            for i in range(arr_index, arr_index+ width):
                scoring_array[i] = 1
            arr_index += 500

        return scoring_array

    # display on matplotlib. Use only with direct run. for direct_run
    def dispPredict(self, droneInstance, ax):
        if self.__areBothEmpty():
            self.predictUpdate()
            if self.__areBothEmpty():
                return

        im_width, im_height = Image.open(self.image_path).size

        img = np.array(Image.open(self.image_path), dtype = np.uint8)

        self.__boxObject(self.fires, droneInstance, ax, im_width, im_height)
        self.__boxObject(self.smoke, droneInstance, ax, im_width, im_height)

        ax.imshow(img)
        plt.pause(1)

    # returns nearest drone coordinates using image coordinates
    def __img_to_drone_coords(self, im_x, im_y, im_width, im_height):
        im_x, im_y = int(round(im_x)), int(round(im_y))
        drone_x = int(round((im_x - 250) / 100))
        drone_y = int(round((im_height - im_y - 250) / 100))

        max_drone_x = int(round((im_width - 500) / 100))
        max_drone_y = int(round((im_height - 500) / 100))

        # bounding
        if drone_x < 0:
            drone_x = 0
        elif drone_x > max_drone_x:
            drone_x = max_drone_x

        if drone_y < 0:
            drone_y = 0
        elif drone_y > max_drone_y:
            drone_y = max_drone_y

        return drone_x, drone_y

    # boxes objects and returns a Draw PIL image and list of object center coordinates. For reverse_run
    def __imgBox(self, obj_list, image, im_width, im_height):
        im = image.convert('RGBA')
        drawn = Draw(im)
        fontsize = im_height * 0.01

        font = ImageFont.truetype('arial.ttf', int(round(fontsize)))

        coords = []

        for inst in obj_list:
            label = inst.tag_name
            probability = inst.probability

            x0, y0 = inst.bounding_box.left * im_width, inst.bounding_box.top * im_height
            x1, y1 = x0 + inst.bounding_box.width * im_width, y0 + inst.bounding_box.height * im_height
            xC, yC = abs(x0 + x1) / 2, abs(y0 + y1) / 2

            xC, yC = self.__img_to_drone_coords(xC, yC, im_width, im_height)

            coords.append((xC, yC))

            drawn.rectangle([(x0, y0), (x1, y1)], outline=(255, 0, 0, 255))
            drawn.text((x0, y0), f'{label}: {round(probability, 3)}; ({xC}, {yC})', fill=(0, 0, 0, 255), font= font)

        return im, coords

    # for reverse_run
    def imgPredict(self):
        if self.__areBothEmpty():
            self.predictUpdate()
            if self.__areBothEmpty():
                return

        img = Image.open(self.image_path)
        im_width , im_height = img.size

        draw, coordList = self.__imgBox(self.fires, img, im_width, im_height)

        return draw, coordList
