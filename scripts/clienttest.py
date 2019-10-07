import requests
import json

# GET all orders
response = requests.get('http://127.0.0.1:5000/orders')
# print all orders
print (response.content)
# convert from JSON to dictionary
decoded = json.loads(response.content)

# look for an order with smallest ID which is not taken, so we can process it
try:
    y = []
    for x in decoded['orders']:
        if x['status'] != 'taken':
            y.append(x['id'])
    minimal_id = min(y)
except ():
    print('JSON error')

print('id:' + ' ' + str(minimal_id))

# PUT - update order, we process it, so it's status changes to taken after that
statement_put = 'http://127.0.0.1:5000/orders/' + str(minimal_id)
update_for_ticket = requests.put(statement_put)
decoded_update = json.loads(update_for_ticket.content)
ticket = decoded_update['ticket']
print('ticket:' + ' ' + str(ticket))

# DELETE, we 'processed' the order, so we delete it from the list
stmndel = 'http://127.0.0.1:5000/orders/' + str(minimal_id) + '/' + str(ticket)
responsedelete = requests.delete(stmndel)


