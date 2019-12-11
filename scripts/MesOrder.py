import time

import requests
import json

import logging


class MesOrder():
    def __init__(self):
        self.url = 'http://10.10.19.20/orders'  #Server ip for
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
