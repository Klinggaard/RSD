import requests

#Probable will change after network is ready
url = 'http://mir.com/api/v2.0.0/'

Authorization = {
    'Authorization': "PUT_THE_RIGHT_KEY"}
language = {'Accept-Language': "en_US"}


class Rest_MiR():
    def __init__(self):
        self.authorization = {
            'Authorization': "PUT_THE_RIGHT_KEY"}

    #We need to put the name of our mission
    def get_mission(self, mission_name="MISSION_NAME"):
        response = requests.get(url + 'missions', headers=self.authorization)
        mission = ""
        if response.status_code != 200:
            print(response.status_code)
        for counter in response.json():
            if counter["name"] == mission_name:
                mission = counter
                print(mission)
        return mission

    def add_mission_to_queue(self, mission):
        data = {"mission_id": str(mission["guid"])}
        print(data)
        response = requests.post(url + "mission_queue", json=data, headers=self.authorization)
        if response.status_code != 201:
            print("ERROR" + str(response.status_code))

    #In the mission we will have to set coils(plc registers) in order to get information if robot has docked and etc.
    def read_register(self, register_id):
        response = requests.get(url + 'registers/' + str(register_id), headers=self.authorization)
        register_value = 0
        if response.status_code != 200:
            print(response.status_code)
            print(response.text)

        if (response.json()['id'] == register_id):
            register_value = response.json()['value']
        return register_value

    #As above, we can set the register when loading on the robot is ready to move to main table
    def write_register(self, register_id, value):
        data = {"value": value}
        response = requests.put(url + 'registers/' + str(register_id), json = data, headers=self.authorization)

        if response.status_code != 200:
            print(response.status_code)
        return 0
