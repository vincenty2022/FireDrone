from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import numpy as np

####################### MODEL SPECIFIC VARIABLES ###############################
prediction_key ='09e3db73317249f78fbbb5ac10261ce8'
project_id = '8d0b1bca-87e6-4d23-a346-03ac599454c6'
publishedName = 'It'
ENDPOINT = 'https://eastus.api.cognitive.microsoft.com'
fire_classifier = 'Fire'            # Name of classifier in Custom Vision
smoke_classifier = 'smoke'          # Name of classifier in Custom Vision

# CALIBRATE FOR USE
fireThreshold = 0.10
smokeThreshold = 0.00
################################################################################

image_path = './frame.png'

class analyze:
    def __init__(self):
        self.model = CustomVisionPredictionClient(prediction_key, endpoint=ENDPOINT)
        self.fires = []
        self.smoke = []

    # updates using the image_path
    def predictUpdate(self):
        fires = []
        smoke = []

        with open(image_path, mode="rb") as test_data:
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
            dist = sqrt(delta_x**2 + delta_y**2)

            fireDist.append(distSq)

        for inst in self.smoke:
            x, y = inst.bounding_box.left, inst.bounding_box.top
            delta_x, delta_y = 0.5 - x, 0.5 - y
            dist = sqrt(delta_x**2 + delta_y**2)

            fireDist.append(dist)

        return fireDist, smokeDist

    # boxes the object and labels with tag name and probability.
    def __boxObject(self, obj_list, ax, im_width, im_height):
        for inst in obj_list:
            x, y = inst.bounding_box.left, inst.bounding_box.top
            label = inst.tag_name
            probability = inst.probability

            # scale to frame dimensions
            pic_coord = (x* im_width, y*im_height)

            # dimensions of recognized region
            obj_width = inst.bounding_box.width*im_width
            obj_height = inst.bounding_box.height*im_height

            rect = patches.Rectangle((pic_coord), obj_width, obj_height, edgecolor = 'r', fill = False)
            text = plt.text(pic_coord[0], pic_coord[1],f'{label}: {round(probability, 3)}')

            ax.add_patch(rect)

    def dispPredict(self, ax):
        if self.__areBothEmpty():
            self.predictUpdate()
            if self.__areBothEmpty():
                return

        im_width, im_height = Image.open(image_path).size

        img = np.array(Image.open(image_path), dtype = np.uint8)

        self.__boxObject(self.fires, ax, im_width, im_height)
        self.__boxObject(self.smoke, ax, im_width, im_height)

        ax.imshow(img)
        plt.pause(1)
