from hanparse import HanParse
import json
from datetime import datetime

settings=json.load(open("settings.json"))

han = HanParse(settings['user'], settings['password'], settings['urlstring'])

han.get_token()
print("Token: " + han.token)

han.get_meter_id()
print("Meter: " + han.meter_id)

result_data = han.get_profile()
print("%s: %f %s" % (result_data['timestamp'], result_data['value'], result_data['unit']))

#date = datetime.strptime(result_data['timestamp'], "%Y-%m-%d %H:%M:%S");
#print(date)
#2025-05-25 17:30:01
