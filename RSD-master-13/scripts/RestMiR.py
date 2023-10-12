import requests
import time
import logging
#Probable will change after network is ready
url = 'http://10.10.19.40/api/v2.0.0/'

Authorization = {
    'Authorization': "PUT_THE_RIGHT_KEY"}
language = {'Accept-Language': "en_US"}


class RestMiR():
    def __init__(self):
        self.authorization = {
            'Authorization': "Basic ZGlzdHJpYnV0b3I6NjJmMmYwZjFlZmYxMGQzMTUyYzk1ZjZmMDU5NjU3NmU0ODJiYjhlNDQ4MDY0MzNmNGNmOTI5NzkyODM0YjAxNA=="}
        self.HOST = 'http://10.10.19.40/api/v2.0.0/'

    #We need to put the name of our mission

    def add_mission_to_queue(self, mission):
        r = requests.get(self.HOST + 'mission_queue', headers=self.authorization)
        data = {"mission_id": str(mission["guid"])}
        for i in [-1, -2, -3, -4]:
            # print(data['mission_id'])
            _id = requests.get(self.HOST + 'mission_queue/' + str(r.json()[i]['id']), headers=self.authorization)
            # print(_id.json()['mission_id'])
            if data['mission_id'] == _id.json()['mission_id']:
                if r.json()[i]['state'] == 'Pending' or r.json()[i]['state'] == 'Executing':
                    print("ERROR" + " Already Pending or Executing")
                    return 0
        response = requests.post(self.HOST + "mission_queue", json=data, headers=self.authorization)
        if response.status_code != 201:
            print("ERROR" + str(response.status_code))
            return 0
        return 1

    def is_docked(self):
        if self.read_register(6) == 1:
            return True
        return False

    def get_mission(self, mission_name="MISSION_NAME"):
        response = None
        try:
            response = requests.get(url + 'missions', headers=self.authorization)
        except requests.exceptions.ConnectionError:
            logging.error("[MiR] Cannot request mission")
            time.sleep(0.1) #sleep 0.1 to not ddos flask server
            #self.get_mission(mission_name)

        mission = ""
        if response != None:
            if response.status_code != 200:
                logging.info(response.status_code)
            for counter in response.json():
                if counter["name"] == mission_name:
                    mission = counter
                    logging.info(mission)
            return mission

    def add_mission_to_queue(self, mission):
        try:
            r = requests.get(self.HOST + 'mission_queue', headers=self.authorization)
            data = {"mission_id": str(mission["guid"])}
            for i in [-1, -2, -3, -4]:
                # print(data['mission_id'])
                _id = requests.get(self.HOST + 'mission_queue/' + str(r.json()[i]['id']), headers=self.authorization)
                # print(_id.json()['mission_id'])
                if data['mission_id'] == _id.json()['mission_id']:
                    if r.json()[i]['state'] == 'Pending' or r.json()[i]['state'] == 'Executing':
                        print("ERROR" + " Already Pending or Executing")
                        return False
            response = requests.post(self.HOST + "mission_queue", json=data, headers=self.authorization)
            if response.status_code != 201:
                print("ERROR" + str(response.status_code))
                return False
            return True
        except requests.exceptions.ConnectionError:
            return False

    def delete_from_queue(self, mission):
        try:
            r = requests.delete(self.HOST + 'mission_queue/' + str(mission["guid"]), headers=self.authorization)
            if r.status_code == 204:
                print("MIR mission deleted due to abort")
                return True
        except r.status_code != 204:
            print("Error deleting MIR mission" + str(r.status_code))
            return False



    #In the mission we will have to set coils (plc registers) in order to get information if robot has docked and etc.
    def read_register(self, register_id):

        try:
            response = requests.get(url + 'registers/' + str(register_id), headers=self.authorization)
        except requests.exceptions.ConnectionError:
            logging.error(" MiR :  Cannot connect to server")
            return

        register_value = 0
        if response.status_code != 200:
            print(response.status_code)
            print(response.text)

        if (response.json()['id'] == register_id):
            register_value = response.json()['value']
        return register_value

    def is_timeout(self):
        if self.get_time()> 599:
            return True
        return False

    def get_time(self):
        return self.read_register(60)

    def release_mir(self):
        self.write_register(6, 0)  # MIR can go

    #As above, we can set the register when loading on the robot is ready to move to main table
    def write_register(self, register_id, value):
        data = {"value": value}
        response = requests.put(url + 'registers/' + str(register_id), json = data, headers=self.authorization)

        if response.status_code != 200:
            print(response.status_code)
        return 0

#
# mir = RestMiR()
# guid = mir.get_mission("GoTo6")
# mir.add_mission_to_queue(guid)
# while mir.read_register(6) != 1: # wait for MIR to arrive
#     mir.read_register(1)
# # add function to put boxes on MIR & flag to make sure we are done with packing
# print("mir arrived")
# time.sleep(2)
# mir.write_register(6, 0)  # MIR can go
# print("bye MIR")
# #change state to completing
