import json

from droneClass import Drone

api_key = 'cyg-yPk*NBPKa!?%F73$$&8a6y7viE*d8_j$uYL2qnsgEndnWWz^q*zh!FO-d!jJ'

run = Drone(api_key)
run.startRun(20)
run.score([1,0,1,0])
run.endRun()




try:
    print(run.get_all_history())

    id = input('ID')

    entry = run.get_history_entry(id)

    parsed = json.loads(entry['content'])
    print(parsed)

except Exception as e:
    print(e)




