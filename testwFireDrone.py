import firedrone.client as fdc
from firedrone.client.errors import FireDroneClientHttpError
import os

api_key = 'cyg-yPk*NBPKa!?%F73$$&8a6y7viE*d8_j$uYL2qnsgEndnWWz^q*zh!FO-d!jJ'

workspace = fdc.Workspace(api_key)
try:
    scenes = workspace.get_scenes()
    print("Yes!")
except FireDroneClientHttpError as e:
    if e.status_code == 401:
        print("Nope")
