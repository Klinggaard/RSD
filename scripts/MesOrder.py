import time

import requests
import json

import logging


class MesOrder():
    def __init__(self):
        self.url = 'http://10.10.19.20/orders'  #Server ip for
        self.urlglob = 'http://10.10.19.20/'
        self.headerglob = {'Content-Type': "application/json", 'Accept-Language': "en_US", 'Cache-Control': "no-cache"}
        self.counter = 0  # counter of processed orders

    def get_order(self):
        # GET all orders
        try:
            response = requests.get(self.url)
            decoded = json.loads(response.content)  # convert from JSON to dictionary
            return decoded
        except requests.exceptions.ConnectionError:
            logging.error("[MesOrder] Cannot connect to database")
        return


    def get_put_order(self):
        # GET all orders
        response = requests.get(self.url)
        #print(response.content)
        decoded = json.loads(response.content)  # convert from JSON to dictionary
        orderdict = {
            "id": 0,
            "ticket": "",
            "red": 0,
            "blue": 0,
            "yellow": 0
        }
        # look for an order with smallest ID which is not taken, so we can process it
        try:
            y = []
            for x in decoded['orders']:
                if x['status'] != 'taken':
                    y.append(x['id'])
            while len(y) == 0:
                logging.info("No orders available, waiting for new orders")
                time.sleep(10)
                response = requests.get(self.url)
                decoded = json.loads(response.content)  # convert from JSON to dictionary
                y = []
                for x in decoded['orders']:
                    if x['status'] != 'taken':
                        y.append(x['id'])
            minimal_id = min(y)
            for xx in decoded['orders']:
                if xx['id'] == minimal_id:
                    orderdict["red"] = xx["red"]
                    orderdict["blue"] = xx["blue"]
                    orderdict["yellow"] = xx["yellow"]
                    orderdict["id"] = minimal_id
            #print(orderdict)
        except ():
            logging.ERROR('MesOrder' + ' JSON error')

        #print('id:' + ' ' + str(minimal_id))
        # PUT - update order, we process it, so it's status changes to taken after that
        statement_put = self.url + '/' + str(minimal_id)
        update_for_ticket = requests.put(statement_put)
        decoded_update = json.loads(update_for_ticket.content)
        #print(decoded_update)
        orderdict["ticket"] = decoded_update['ticket']
        #print('ticket:' + ' ' + orderdict["ticket"])
        #print(orderdict)

        logging.info("[MesOrder] %s %s", str('Taking order with ID: '), str(minimal_id))
        return orderdict

    def delete_order(self, processing):
        # DELETE, we 'processed' the order, so we delete it from the list
        id_delete = processing["id"]
        ticket_delete = processing["ticket"]
        stmndel = self.url + '/' + str(id_delete) + '/' + str(ticket_delete)
        responsedelete = requests.delete(stmndel)
        self.counter += 1
        return self.counter

    def log_state(self, state):
        payload = None

        # PML_Idle
        if state == "Idle":
            payload = {
                "cell_id": 6,
                "comment": ("State: " + state),
                "event": "PML_Idle"
            }

        # PML_Execute
        if state == "Executing":
            payload = {
                "cell_id": 6,
                "comment": ("State: " + state),
                "event": "PML_Execute"
            }

        # PML_Complete ???

        # PML_Held
        if state == "Held":
            payload = {
                "cell_id": 6,
                "comment": ("State: " + state),
                "event": "PML_Held"
            }

        # PML_Suspended
        if state == "Suspended":
            payload = {
                "cell_id": 6,
                "comment": ("State: " + state),
                "event": "PML_Suspended"
            }

        # PML_Aborted
        if state =="Aborted":
            payload = {
                "cell_id": 6,
                "comment": ("State: " + state),
                "event": "PML_Aborted"
            }

        # PML_Stopped
        if state == "Stopped":
            payload = {
                "cell_id": 6,
                "comment": ("State: " + state),
                "event": "PML_Stopped"
            }

        payload = json.dumps(payload)
        self.post_log(payload)
        return

    def log_order_start(self, order):
        payload = {
            "cell_id": 6,
            "comment": "Started on "+str(order),
            "event": "Order_Start"
        }
        payload = json.dumps(payload)
        self.post_log(payload)
        return

    def log_order_done(self, order):
        payload = {
            "cell_id": 6,
            "comment": "Done with "+str(order),
            "event": "Order_Done"
        }
        payload = json.dumps(payload)
        self.post_log(payload)
        return

    def post_log(self, payload):
        url = self.urlglob+"/log"
        headers = self.headerglob
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)
        logs = json.loads(response.text)
        return logs