from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import numpy as np

####################### MODEL SPECIFIC VARIABLES ###############################
prediction_key ='09e3db73317249f78fbbb5ac10261ce8'
project_id = '8d0b1bca-87e6-4d23-a346-03ac599454c6'
publishedName = 'It'
ENDPOINT = 'https://eastus.api.cognitive.microsoft.com'
fire_classifier = 'fire'            # Name of classifier in Custom Vision
smoke_classifier = 'smoke'          # Name of classifier in Custom Vision

# CALIBRATE FOR USE
fireThreshold = 0.10
smokeThreshold = 0.00
################################################################################

image_path = './frame.png'


predictor = CustomVisionPredictionClient(prediction_key, endpoint=ENDPOINT)

with open(image_path, mode="rb") as test_data:
    results = predictor.detect_image(project_id, publishedName, test_data)

# Display the results.
for prediction in results.predictions:
   print("\t" + prediction.tag_name + ": {0:.2f}% bbox.left = {1:.2f}, bbox.top = {2:.2f}, bbox.width = {3:.2f}, bbox.height = {4:.2f}".format(prediction.probability * 100, prediction.bounding_box.left, prediction.bounding_box.top, prediction.bounding_box.width, prediction.bounding_box.height))
