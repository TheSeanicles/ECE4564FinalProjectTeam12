import requests
import random
import time
import json


base_url = 'http://192.168.10.150:5000'

for _ in range(30):
    ran = random.randint(60, 70)
    msg = {"metadata": "Sean", "hr": ran}
    r = requests.post(url=base_url + '/API/hr', headers={'Connection': 'close'}, json=msg)
    # print(r.content)
    time.sleep(1)
count = 70
for _ in range(50):
    msg = {"metadata": "Sean", "hr": count+1}
    r = requests.post(url=base_url + '/API/hr', headers={'Connection': 'close'}, json=msg)
    # print(r.content)
    time.sleep(1)
for _ in range(50):
    msg = {"metadata": "Sean", "hr": count-1}
    r = requests.post(url=base_url + '/API/hr', headers={'Connection': 'close'}, json=msg)
    # print(r.content)
    time.sleep(1)
print('Should get text here')
msg = {"metadata": "Sean", "hr": 130}
r = requests.post(url=base_url + '/API/hr', headers={'Connection': 'close'}, json=msg)
# print(r.content)
time.sleep(1)
msg = {"metadata": "Sean", "hr": 134}
r = requests.post(url=base_url + '/API/hr', headers={'Connection': 'close'}, json=msg)
# print(r.content)
time.sleep(1)
msg = {"metadata": "Sean", "hr": 150}
r = requests.post(url=base_url + '/API/hr', headers={'Connection': 'close'}, json=msg)
# print(r.content)
time.sleep(1)

msg = {"user": "Sean", "time": "2min"}
r = requests.get(url=base_url + '/API/hr', headers={'Connection': 'close'}, json=msg)
ans_dict = json.loads(r.content.decode('utf-8'))
print(json.dumps(ans_dict, indent=4))
time.sleep(1)
