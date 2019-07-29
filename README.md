# DroneStuff FireDroneAI Entry
## Purpose
This project was intended for entry in the FireDroneAI 2019 online hackathon.
The theme of this hackathon was to utilize Microsoft Azure services to develop software for fire detecting drones using
the provided virtual drone API.

The code for this project was written by vincenty2022. The custom vision model used was trained by leonmat using
Microsoft Azure Custom Vision Services

## Libaries Used
###### Microsoft Azure Services
- Azure Storage
- Azure Cognitive Services

###### Other Libaries
- Matplotlib
- PIL
- Numpy
- Readchar

## Description
###### __direct_run.py__
Imagined as being part of the on-board code of the virtual drone.

Accepts manual input in controlling the virtual drone. Displays and updates the image on a matplotlib matplotlib. The
drone's current field of vision can be analyzed for fires by the Azure custom vision model at any point.
Note: run this script to run the direct_run once

###### __reverse_run.py__
Imagined as being part of the on-board code of the virtual drone.

Operates autonomously after a scene is selected. Scans the entire scene and stitches together the larger image. The
image is then passed to the azure custom vision model to identify fires. The located fires are boxed onto a copy of the
initial image of the scene. The coordinates of the files are loaded onto a json file. These two images and the json
files are then exported to Azure Storage services.
Note: run this script to run the reverse_run once

###### __control_panel.py__
Imagined as being the primary code used by off-site hardware used to control the drone.

Prompts the user to begin either an indefinite (until cancelled) set of reverse_runs for data collection purposes or
a direct_run that imports previously recorded data from the cloud and direct_run to take a closer look at the identified
fires.
Note: primary script to run for use of this project


