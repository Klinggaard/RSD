from flask import Flask, jsonify
from flask import make_response, abort, request
from flaskext.mysql import MySQL
import uuid
import threading
import time
import random
# import mysql.connector

mysql = MySQL()

class FlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(*args, **kwargs)
        self.config['MYSQL_DATABASE_USER'] = 'root'
        self.config['MYSQL_DATABASE_PASSWORD'] = 'andrzej137'
        self.config['MYSQL_DATABASE_DB'] = 'rsd2018'
        self.config['MYSQL_DATABASE_HOST'] = 'localhost'

        mysql.init_app(self)
        self._activate_background_job()

    def _activate_background_job(self):
        def run_job():
            while True:
                # check if there is enough jobs in the job queue
                num = -1

                con = mysql.connect()
                cur = con.cursor()

                try:
                    cur.execute('''select * from rsd2018.jobs''')
                    num = cur.rowcount
                except Exception as e:
                    err_str = "Problem accesing sql: " + str(e)
                    print(err_str)

                print("There are " + str(num) + " jobs in queue")

                if num >= 0 and num < 5:
                    # insert a new order in the system
                    params = (
                        random.randint(0, 4),
                        random.randint(0, 3),
                        random.randint(0, 2)
                    )

                    #what is all three are zero?
                    if params[0] == 0 and params[1] == 0 and params[2] == 0:
                        params = ( 1, 1, 0 )

                    insert_stmt = ("INSERT INTO rsd2018.jobs (time, red, blue, yellow, status) "
                                   "VALUES (CURRENT_TIMESTAMP, %s, %s, %s, 1)"
                                   )

                    #print("SQL ", insert_stmt, " + ", params)

                    try:
                        cur.execute(insert_stmt, params)
                        con.commit()
                    except Exception as e:
                        err_str = "Problem inserting jobs: " + str(e)
                        print(err_str)

                cur.close()
                con.close()

                time.sleep(5)

        t1 = threading.Thread(target=run_job)
        t1.start()

app = FlaskApp(__name__)
#app = Flask(__name__)


# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'andrzej137'
app.config['MYSQL_DATABASE_DB'] = 'rsd2018'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

EventTypes = [
    "PML_Idle",
    "PML_Execute",
    "PML_Complete",
    "PML_Held",
    "PML_Suspended",
    "PML_Aborted",
    "PML_Stopped",
    "Order_Start",
    "Order_Done"
	]

StatusText = [
    "undefined",
    "ready",
    "taken"
    ]

mysql.init_app(app)

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
def get_log():
    cur = mysql.connect().cursor()
    cur.execute('''select * from rsd2018.log''')
    r = [dict((cur.description[i][0], value)
              for i, value in enumerate(row)) for row in cur.fetchall()]

    cur.close()
    return jsonify({'logs' : r})



@app.route('/log', methods=['POST'])
def postlog_entry():
    if not request.json:
        raise InvalidUsage('Missing json content', status_code=400)

    if 'cell_id' in request.json:
        if type(request.json['cell_id']) is not int:
            raise InvalidUsage('cell_id type is not int', status_code=400)
    else:
        raise InvalidUsage('Missing cell_id in content', status_code=400)

    if 'comment' in request.json:
        if type(request.json['comment']) is not str:
            raise InvalidUsage('comment type is not str', status_code=400)
    else:
        raise InvalidUsage('Missing comment in content', status_code=400)

    if 'event' in request.json:
        if type(request.json['event']) is not str:
            raise InvalidUsage('event type is not str', status_code=400)
    else:
        raise InvalidUsage('Missing event in content', status_code=400)

    event_str = request.json.get('event')

    if not event_str in EventTypes:
        raise InvalidUsage('event is not of legal type', status_code=400)

    params = (
        request.json.get('cell_id'),
        request.json.get('comment'),
        EventTypes.index(event_str)
    )

    insert_stmt = ("INSERT INTO rsd2018.log (time, cell_id, comment, event) "
                   "VALUES (CURRENT_TIMESTAMP, %s, %s, %s)"
                   )

    con = mysql.connect()
    cur = con.cursor()
    try:
        cur.execute(insert_stmt, params)
        con.commit()
    except Exception as e:
        err_str = "Problem inserting into db: " + str(e)
        raise InvalidUsage(jsonify({'sql error': err_str}), status_code=500)

    last_row_id = cur.lastrowid
    cur.close()
    con.close()

    # 201 Created
    return make_response(jsonify({'log_entry': last_row_id}),201)


@app.route('/event_types', methods=['GET'])
def get_event_types():
    return jsonify({'EventTypes' : EventTypes})


@app.route('/orders', methods=['GET'])
def get_orders():
    r = []
    #temp = mysql.connector.connect(database="rsd2018")
    #cur = temp.cursor()
    con = mysql.connect()
    cur = con.cursor()
    #select_stmt = ("select id, blue, red, yellow, status from rsd2018.jobs")
    #cur.execute("""SELECT * FROM rsd2018.jobs""")
    cur.execute('''select id, blue, red, yellow, status from rsd2018.jobs''')
    #cur.execute(select_stmt)
    for row in cur.fetchall():
        r.append({'id': row[0], 'blue': row[1], 'red': row[2], 'yellow': row[3], 'status': StatusText[row[4]]})

    cur.close()

    return jsonify({'orders': r})


@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    return jsonify({'order': order_id})

@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    params = (order_id)
    select_stmt = ("select id, status from rsd2018.jobs where id = %s")

    con = mysql.connect()
    cur = con.cursor()
    try:
        cur.execute(select_stmt, params)
    except Exception as e:
        err_str = "Problem selecting order_id: " + str(e)
        raise InvalidUsage(jsonify({'sql error': err_str}), status_code=500)

    if cur.rowcount != 1: # we should only have one entry
        raise InvalidUsage('Order id  not in db', status_code=400)

    if cur.fetchall()[0][1] == 2: # check if the job is already taken
        raise InvalidUsage('Order is taken and not ready', status_code=400)

    update_stmt = ("update rsd2018.jobs set status = 2 where id = %s")

    try:
        cur.execute(update_stmt, params)
        con.commit()
    except Exception as e:
        err_str = "Problem updating order_id: " + str(e)
        raise InvalidUsage(jsonify({'sql error': err_str}), status_code=500)

    # now generate the ticket, and insert it into the db
    ticket = uuid.uuid4().hex.upper()[0:6]
    ticket_update_stmt = ("update rsd2018.jobs set ticket = %s where id = %s")
    params_2 = (ticket, order_id)

    try:
        cur.execute(ticket_update_stmt, params_2)
        con.commit()
    except Exception as e:
        err_str = "Problem updating order_id: " + str(e)
        raise InvalidUsage(jsonify({'sql error': err_str}), status_code=500)

    cur.close()
    con.close()

    return jsonify({'ticket': ticket})

@app.route('/orders/<int:order_id>/<string:ticket>', methods=['DELETE'])
def delete_order(order_id, ticket):
    params = (order_id)
    select_stmt = ("select ticket from rsd2018.jobs where id = %s")

    con = mysql.connect()
    cur = con.cursor()
    try:
        cur.execute(select_stmt, params)
    except Exception as e:
        err_str = "Problem selecting order_id: " + str(e)
        raise InvalidUsage(jsonify({'sql error': err_str}), status_code=500)

    if cur.rowcount != 1: # we should only have one entry
        raise InvalidUsage('Order id  not in db', status_code=400)

    tuple = cur.fetchall()
    if tuple[0][0] != ticket: # check if the ticket is the same as in the db
        raise InvalidUsage('Ticket does not match', status_code=400)

    #params = (order_id)
    delete_stmt = ("delete from rsd2018.jobs where id = %s")

    #con = mysql.connect()
    #cur = con.cursor()

    try:
        cur.execute(delete_stmt, params)
        con.commit()
    except Exception as e:
        err_str = "Problem selecting order_id: " + str(e)
        raise InvalidUsage(jsonify({'sql error': err_str}), status_code=500)

    # cnt = cur.rowcount

    cur.close()
    con.close()

    # return code 204 No Content
    headers = {"Content-Type": "application/json2"}
    return make_response(jsonify({}), 204)

if __name__ == '__main__':
    app.run()
