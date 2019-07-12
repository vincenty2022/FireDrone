import firedrone.client as fdc
from firedrone.client.errors import FireDroneClientHttpError
import os
from IPython.display import Image
import readchar
from droneClass import Drone

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

matplotlib.rcParams['interactive'] == True

api_key = 'cyg-yPk*NBPKa!?%F73$$&8a6y7viE*d8_j$uYL2qnsgEndnWWz^q*zh!FO-d!jJ'

test = Drone(api_key)
test.startRun(21)
test.manualRun()
test.endRun()
