# basically useless now

import firedrone.client as fdc
from firedrone.client.errors import FireDroneClientHttpError

registration = fdc.Registration()

user_registration_info = {
    "name": "DroneStuff",
    "devpostAccount": "vincenty2022"
}
new_user = registration.register_user(user_registration_info)
print(new_user)