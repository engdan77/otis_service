#!/usr/bin/env python

# edoAutoHome.py - This Project for HomeAutomation
# URL: https://github.com/engdan77/edoautohome
# Author: Daniel Engvall (daniel@engvalls.eu)


import threading
import SocketServer
import json
import sys
import os
import argparse
import Queue
import time
from pprint import pprint
from edo import *

__version__ = "$Revision: 20160616.702 $"

CONFIG_FILE = "edoAutoHome.conf"


def create_schema(db_ip, db_user, db_pass, db_name, logObject):
        ''' Creates database if necessary '''
        from edo import edoTestSocket, edoClassDB
        if edoTestSocket(db_ip, 3306, logObject) == 0:
            oDB = edoClassDB('mysql', (db_ip, '3306', db_user, db_pass, db_name), logObject)
            oDB.create((['device', 'DEVICE_ID', 'INTEGER'],
                        ['device', 'name', 'TEXT'],
                        ['device', 'location', 'TEXT'],
                        ['device_attr', 'device_id', 'INTEGER'],
                        ['device_attr', 'attr_id', 'TEXT'],
                        ['device_attr', 'data', 'TEXT'],
                        ['device_attr', 'updated', 'TEXT'],
                        ['attribute', 'ATTR_ID', 'INTEGER'],
                        ['attribute', 'name', 'TEXT'],
                        ['type', 'TYPE_ID', 'INTEGER'],
                        ['type', 'name', 'TEXT'],
                        ['event_history', 'EVENT_ID', 'INTEGER'],
                        ['event_history', 'device_id', 'INTEGER'],
                        ['event_history', 'type_id', 'INTEGER'],
                        ['event_history', 'attr_id', 'INTEGER'],
                        ['event_history', 'data', 'TEXT'],
                        ['event_history', 'date', 'TEXT']))
            return oDB
        else:
            return None


def add_device(db_ip, db_user, db_pass, db_name, device_id, device_name, device_location, logObject):
        ''' Add device to database  '''
        from edo import edoTestSocket, edoClassDB
        if edoTestSocket(db_ip, 3306, logObject) == 0:
            oDB = edoClassDB('mysql', (db_ip, '3306', db_user, db_pass, db_name), logObject)
            oDB.insert('device', {'device_id': device_id, 'name': device_name, 'location': device_location})


def list_device(db_ip, db_user, db_pass, db_name, logObject):
        ''' List devices in database  '''
        from edo import edoTestSocket, edoClassDB
        if edoTestSocket(db_ip, 3306, logObject) == 0:
            oDB = edoClassDB('mysql', (db_ip, '3306', db_user, db_pass, db_name), logObject)
            result = oDB.select('device', "id > 0")
            print(result)


def add_attribute(db_ip, db_user, db_pass, db_name, attr_id, attr_name, logObject):
        ''' Add attribute to database  '''
        from edo import edoTestSocket, edoClassDB
        if edoTestSocket(db_ip, 3306, logObject) == 0:
            oDB = edoClassDB('mysql', (db_ip, '3306', db_user, db_pass, db_name), logObject)
            oDB.insert('attribute', {'attr_id': attr_id, 'name': attr_name})


def attr_to_dev(db_ip, db_user, db_pass, db_name, attr_id, dev_id, logObject):
        ''' Associate attr to dev in database  '''
        from edo import edoTestSocket, edoClassDB
        if edoTestSocket(db_ip, 3306, logObject) == 0:
            oDB = edoClassDB('mysql', (db_ip, '3306', db_user, db_pass, db_name), logObject)
            oDB.insert('device_attr', {'attr_id': attr_id, 'device_id': dev_id, 'data': 'None', 'updated': edoGetDateTime()})


def list_attribute(db_ip, db_user, db_pass, db_name, logObject):
        ''' List attributes in database  '''
        from edo import edoTestSocket, edoClassDB
        if edoTestSocket(db_ip, 3306, logObject) == 0:
            oDB = edoClassDB('mysql', (db_ip, '3306', db_user, db_pass, db_name), logObject)
            result = oDB.select('attribute', "id > 0")
            print(result)


def list_attr_dev(db_ip, db_user, db_pass, db_name, logObject):
        ''' List device attributes in database  '''
        from edo import edoTestSocket, edoClassDB
        if edoTestSocket(db_ip, 3306, logObject) == 0:
            oDB = edoClassDB('mysql', (db_ip, '3306', db_user, db_pass, db_name), logObject)
            result = oDB.select('device_attr', "id > 0")
            print(result)


def show_status_short():
    ''' List current status of sensors  '''
    from edo import edoTestSocket, edoClassDB
    db_ip = server_settings['db_ip']
    db_user = server_settings['db_user']
    db_pass = server_settings['db_pass']
    db_name = server_settings['db_name']
    if edoTestSocket(db_ip, 3306, logObject) == 0:
        oDB = edoClassDB('mysql', (db_ip, '3306', db_user, db_pass, db_name), logObject)
        result = oDB.sql("SELECT DATE_FORMAT(updated, '%e/%c %H:%i') as last_update, data, a.name as sensor, CONCAT(d.location, '-', d.name) as device FROM device_attr da INNER JOIN device d ON (da.device_id = d.device_id) INNER JOIN attribute a ON (da.attr_id = a.attr_id) ORDER BY updated DESC;")
    else:
        result = None
    info = ""
    for line in result:
        info += "%s \"%s\" %s %s\n" % line
    return info


def show_history(**args):
    ''' Show history of events  '''
    from tabulate import tabulate
    length = args.get('length', 100)
    mailer = args.get('mailer', 'no')
    mail_settings = args.get('mail_settings', None)
    from edo import edoTestSocket, edoClassDB
    db_ip = server_settings['db_ip']
    db_user = server_settings['db_user']
    db_pass = server_settings['db_pass']
    db_name = server_settings['db_name']
    db_success = False
    org_length = length
    if edoTestSocket(db_ip, 3306, logObject) == 0:
        oDB = edoClassDB('mysql', (db_ip, '3306', db_user, db_pass, db_name), logObject)
        while not db_success:
            print 'Getting last {} records'.format(length)
            try:
                # result = oDB.sql('select h.date, d.name, d.location, a.name, h.data from event_history h inner join device d on (h.device_id = d.device_id) inner join attribute a on (h.attr_id = a.attr_id) order by date desc limit {};'.format(length * 10))
                result = oDB.sql('select h.date, d.name, d.location, a.name, h.data from event_history h inner join device d on (h.device_id = d.device_id) inner join attribute a on (h.attr_id = a.attr_id) where h.date > NOW() - INTERVAL 60 DAY order by date desc limit 1000;')
                result = list(result)
                result.reverse()
                db_success = True
            except Exception as e:
                length /= 2
                print str(e)
                print 'Failed getting records'
        if not db_success:
            sys.exit(1)

        length = org_length
        formatted_list = list()
        buffert = list()
        prev_sensor = None
        for date, dn, dl, an, data in result:
            d = date[8:10]
            m = date[5:7]
            t = date[11:]
            date = '{}/{} {}'.format(d, m, t)
            sensor = '{}/{} {}'.format(dl[:3], dn[:3], an)
            if not prev_sensor == sensor:
                # Empty buffert into formatted_list if moren 3 items dump only
                # one
                if len(buffert) >= 3:
                    formatted_list.append(buffert[-1])
                else:
                    formatted_list.extend(buffert)
                buffert = list()
                buffert.append([date, sensor, '{} ({} other)'.format(data, len(buffert)) if len(buffert) > 3 else data])
            else:
                buffert.append([date, sensor, '{} ({} other)'.format(data, len(buffert)) if len(buffert) > 3 else data])
            prev_sensor = sensor
        # pprint(formatted_list)
        result = formatted_list[-length:]
    else:
        result = None
    print "Event history"
    result_text = tabulate(result)
    result_html = tabulate(result, tablefmt='html')
    if mailer == 'yes' and mail_settings:
        print "Sending mail"
        funcSendGMail(None, None, mail_settings['gmail_user'], mail_settings['gmail_pass'], mail_settings['to'], '{}@gmail.com'.format(mail_settings['gmail_user']), 'edoAutoHome History', result_html)
    return result_text


def show_status_json():
    ''' List current status of sensors in json-format '''
    from edo import edoTestSocket, edoClassDB
    from collections import namedtuple, defaultdict
    import json

    db_ip = server_settings['db_ip']
    db_user = server_settings['db_user']
    db_pass = server_settings['db_pass']
    db_name = server_settings['db_name']
    if edoTestSocket(db_ip, 3306, logObject) == 0:
        oDB = edoClassDB('mysql', (db_ip, '3306', db_user, db_pass, db_name), logObject)
        result = oDB.sql("SELECT updated AS last_update, data, a.name AS sensor, CONCAT(d.location, '-', d.name) AS device, da.device_id AS device_id, da.attr_id AS attr_id FROM device_attr da INNER JOIN device d ON (da.device_id = d.device_id) INNER JOIN attribute a ON (da.attr_id = a.attr_id) ORDER BY updated DESC;")
    else:
        result = None

    database_record = namedtuple('database_record', 'date data sensor device device_id attr_id')
    result_json = defaultdict(list)

    for record in map(database_record._make, result):
        record = record._replace(device_id=int(record.device_id))
        # Get 10 last record for each device
        last_records = oDB.sql("SELECT date, data FROM event_history WHERE device_id=%s AND attr_id=%s ORDER BY id DESC LIMIT 10" % (record.device_id, record.attr_id))
        # print last_records
        result_json[record.device].append({record.sensor: {'last_update': record.date, 'data': record.data, 'last_records': last_records}})
    return json.dumps(result_json)


def pause(duration):
    ''' Function to pause alerts for x hours '''
    try:
        import memcache
    except:
        print "Please install memcache to support reading status, can't use pause function"
    else:
        shared = memcache.Client(['127.0.0.1:11211'], debug=1)
        print "Current pause is set to %s" % (str(shared.get("pause")),)
        print "Pausing alerts for %s hours" % (str(duration),)
        shared.set("pause", int(duration) * 3600)


def show_onoff(db_ip, db_user, db_pass, db_name, logObject):
        ''' List current status of sensors  '''
        from edo import edoTestSocket, edoClassDB
        if edoTestSocket(db_ip, 3306, logObject) == 0:
            oDB = edoClassDB('mysql', (db_ip, '3306', db_user, db_pass, db_name), logObject)
            result = oDB.sql("SELECT CONCAT(d.location, '-', d.name) as device, a.name as sensor, data, DATE_FORMAT(updated, '%e/%c %H:%i') as last_update FROM device_attr da INNER JOIN device d ON (da.device_id = d.device_id) INNER JOIN attribute a ON (da.attr_id = a.attr_id) ORDER BY updated DESC;")
            print(result)


def get_attr_name(attr_id, objDB):
        ''' List attribute name from database  '''
        result = objDB.select('attribute', "attr_id = " + str(attr_id))
        return result[0][2]


def get_dev_name(dev_id, objDB):
        ''' List device name from database  '''
        result = objDB.select('device', "device_id = " + str(dev_id))
        return "%s/%s" % (result[0][2], result[0][3])


class edoThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    ''' BaseRequestHandler uses TCPserver and does the actual work '''
    def handle(self):
        data = self.request.recv(1024)
        print(edoGetDateTime() + ": Recieved - " + str(data))

        if data.find('show_status_json') > 0:
            print(edoGetDateTime() + ": Sending status of sensors in JSON")
            self.request.sendall(show_status_json())
            return

        try:
            # Check if json
            data = json.loads(data)
        except Exception:
            pass
        else:
            self.server.queue.put(data)
            response = "ok"
            self.request.sendall(response)
            # print self.server.queue


class edoThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, queue):
        ''' Extend init to handle queue '''
        self.queue = queue
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)


def edoSendSocket(ip, port, message):
    ''' Simple client to send data '''
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print "Received: {}".format(response)
    finally:
        sock.close()


class triggerListener():
    ''' Daemon used for listening for request to trigger events from server '''
    def __init__(self, port, queue=None):
        import Queue

        # Create queue for incoming trigger to handle if not supplied
        if queue is None:
            self.queue = Queue.Queue()
        else:
            self.queue = queue

        # Port 0 means to select an arbitrary unused port
        self.host, self.port = "0.0.0.0", port

    def start(self):
        # Extend edoThreadedTCPServer with queue
        self.server = edoThreadedTCPServer((self.host, self.port), edoThreadedTCPRequestHandler, self.queue)

        # Returns the ip and port
        # ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self.server_thread = threading.Thread(target=self.server.serve_forever)

        # Exit the server thread when the main thread terminates
        self.server_thread.daemon = True
        self.server_thread.start()
        print "TriggerListener loop running in thread:", self.server_thread.name

    def stop(self):
        self.server.shutdown()


class smsListener():
    ''' Daemon used for listening for request to send SMS - not used yet '''
    def __init__(self, port, **kwargs):
        self.m = kwargs.get('dongle', None)
        self.host = '0.0.0.0'
        self.port = int(port)

    def start(self):
        # Extend edoThreadedTCPServer with queue
        self.server = edoDongleTCPServer((self.host, self.port), edoDongleTCPRequestHandler, self.m)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self.server_thread = threading.Thread(target=self.server.serve_forever)

        # Exit the server thread when the main thread terminates
        self.server_thread.daemon = True
        self.server_thread.start()
        print "smsListener loop running in thread:", self.server_thread.name

    def stop(self):
        self.server.shutdown()


class triggerQueueHandler(threading.Thread):
    ''' Class to create trigger queue handler that runs in background
    mode=server/client
    queue=triggerQueue
    '''
    def __init__(self, mode, queue, **kwargs):
        threading.Thread.__init__(self)
        self.queue = queue
        self.objLcd = kwargs['lcd']
        self.mode = mode
        self.alarm = kwargs['alarm']
        self.db = kwargs['db']
        self.sensorList = kwargs.get('sensors', None)
        self.logObject = kwargs.get('loggerObject', None)

    def print_all(self):
        ''' Print whole content of queue '''
        while not self.queue.empty():
            print self.queue.get()

    def run(self):
        ''' The actual Queue handler (EDIT)'''
        import time
        import json
        self.running = True
        while self.running:
            if not self.queue.empty():
                trigger = self.queue.get()

                # Check if "reset_all_sensors" are recieved
                if trigger == "reset_all_sensors":
                    for sensor in self.sensorList:
                        if hasattr(sensor, 'reset'):
                            self.logObject.log("Resetting Sensor: " + str(sensor), 'INFO')
                            sensor.reset()
                    continue

                # If data comes as json
                if str(type(trigger)) == "<type 'unicode'>":
                    try:
                        trigger = json.loads(trigger)
                    except Exception as e:
                        print "Could not parse json '%s' result in error: %s" % (str(trigger), str(e))
                        self.logObject.log("Could not parse incoming TCP json '%s'" % (str(trigger)), 'WARNING')
                        continue

                # date = edoGetDateTime()
                deviceId = trigger['deviceId']
                type_id = trigger['type_id']
                attr_id = trigger['attr_id']
                data = trigger['data']

                print edoGetDateTime() + ": Handling trigger in queue " + str(trigger)
                if attr_id == 1:
                    # Motion Pir
                    date = edoEpochToDate(data[0])
                    db_data = "Motion"
                    alert = date + ",id=" + str(deviceId) + ": Motion Detected"
                elif attr_id == 2:
                    # Door switch
                    date = edoEpochToDate(data[0][0])
                    db_data = "Door " + data[0][1]
                    alert = date + ",id=" + str(deviceId) + ": " + db_data
                elif attr_id == 3:
                    # Power Meter
                    date = edoEpochToDate(data[0][0])
                    db_data = str(data[0][1])
                    alert = date + ",id=" + str(deviceId) + ": " + "Power Changed " + db_data
                elif attr_id == 4:
                    # Humidity Meter
                    date = edoEpochToDate(data[0][0])
                    db_data = str(data[0][1])
                    alert = date + ",id=" + str(deviceId) + ": " + "Humidity Changed " + db_data
                elif attr_id == 5:
                    # Temperature Meter
                    date = edoEpochToDate(data[0][0])
                    db_data = str(data[0][1])
                    alert = date + ",id=" + str(deviceId) + ": " + "Temperature Changed " + db_data
                elif attr_id == 6:
                    # MQ2 Meter
                    date = edoEpochToDate(data[0][0])
                    db_data = str(data[0][1])
                    alert = date + ",id=" + str(deviceId) + ": " + "MQ2 Changed " + db_data
                elif attr_id == 7:
                    # LuxMeter
                    date = edoEpochToDate(data[0][0])
                    db_data = str(data[0][1])
                    alert = date + ",id=" + str(deviceId) + ": " + "Lux Changed " + db_data

                # If LCD exists
                if self.objLcd:
                    self.objLcd.text(alert, 5)

                # If Server Mode - store to database
                if self.mode == 'server' and self.db is not None:
                    self.db.insert('event_history', {'device_id': deviceId, 'type_id': type_id, 'attr_id': attr_id, 'data': db_data, 'date': date})
                    # Check if current status stored
                    if self.db.select('device_attr', {'device_id': deviceId}) is not None:
                        self.db.update('device_attr', {'device_id': deviceId, 'attr_id': attr_id}, {'data': db_data, 'updated': date})
                    else:
                        self.db.insert('device_attr', {'device_id': deviceId, 'attr_id': attr_id, 'data': db_data, 'updated': date})
                    # ADD ALARM HANDLER
                    if self.alarm:
                        self.alarm.check(deviceId, attr_id, db_data)

                # If Client Mode - send event to Master
                if self.mode == 'client':
                    master_ip = client_settings['master_ip']
                    master_port = int(client_settings['master_port'])
                    send_data = json.dumps({'deviceId': int(deviceId), 'type_id': type_id, 'attr_id': attr_id, 'data': data})
                    result = triggerEvent(master_ip, master_port, send_data)
                    if result == 'ok':
                        self.logObject.log("Event sent: " + str(send_data), 'INFO')
                    else:
                        self.logObject.log("Error sending event: " + str(send_data) + " Exception: " + str(result), 'ERROR')

                time.sleep(0.5)

    def stop(self):
        ''' Stop handler '''
        self.running = False


class sensorMotion(threading.Thread):
    ''' Class to detectiom montion '''
    def __init__(self):
        self.detected = False

    def run(self):
        ''' Check for motion '''
        import time
        self.running = True
        while self.running:
            # Code to get GPIO data
            time.sleep(3)
            self.detected = True

    def stop(self):
        ''' Stop motion detection '''
        self.running = False

    def get(self):
        ''' Return true and reset motion detected '''
        if self.detected is True:
            self.detected = False
            return True
        else:
            return False


class sensorCheck(threading.Thread):
    ''' Class to create thread that check sensor(s) '''
    def __init__(self, queue, deviceId, sensorList):
        threading.Thread.__init__(self)
        self.queue = queue
        self.sensorList = sensorList
        self.deviceId = deviceId

        # Start checking of sensors
        for sensor in self.sensorList:
            sensor.start()

    def run(self):
        ''' Actual handler for checking sensor(s) '''
        import time
        self.running = True

        while self.running:
            # Start Loop
            for sensor in self.sensorList:
                # Handler for PIR MOTION
                if sensor.__class__.__name__ is "edoPirMotion":
                    motions_detected = sensor.get()
                    if len(motions_detected) > 0:
                        result = {'deviceId': self.deviceId, 'type_id': 1, 'attr_id': 1, 'data': motions_detected}
                        self.queue.put(result)
            for sensor in self.sensorList:
                # Handler for SWITCH
                if sensor.__class__.__name__ is "edoSwitch":
                    switch_status = sensor.get()
                    if len(switch_status) > 0:
                        result = {'deviceId': self.deviceId, 'type_id': 1, 'attr_id': 2, 'data': switch_status}
                        self.queue.put(result)
            for sensor in self.sensorList:
                # Handler for SWITCH
                if sensor.__class__.__name__ is "edoPowerMeter":
                    power_status = sensor.get()
                    if len(power_status) > 0:
                        result = {'deviceId': self.deviceId, 'type_id': 1, 'attr_id': 3, 'data': power_status}
                        self.queue.put(result)
            for sensor in self.sensorList:
                if sensor.__class__.__name__ is "edoDHT":
                    # Handler for DHT11_humid
                    if sensor.type == 0:
                        dht_humid_status = sensor.get()
                        if len(dht_humid_status) > 0:
                            result = {'deviceId': self.deviceId, 'type_id': 1, 'attr_id': 4, 'data': dht_humid_status}
                            self.queue.put(result)
                    # Handler for DHT11_temp
                    if sensor.type == 1:
                        dht_temp_status = sensor.get()
                        if len(dht_temp_status) > 0:
                            result = {'deviceId': self.deviceId, 'type_id': 1, 'attr_id': 5, 'data': dht_temp_status}
                            self.queue.put(result)
            for sensor in self.sensorList:
                # Handler for MQ2
                if sensor.__class__.__name__ is "edoADCmeter":
                    adc_status = sensor.get()
                    if len(adc_status) > 0:
                        result = {'deviceId': self.deviceId, 'type_id': 1, 'attr_id': 6, 'data': adc_status}
                        self.queue.put(result)
            for sensor in self.sensorList:
                # Handler for MQ2
                if sensor.__class__.__name__ is "edoLuxMeter":
                    lux_status = sensor.get()
                    if len(lux_status) > 0:
                        result = {'deviceId': self.deviceId, 'type_id': 1, 'attr_id': 7, 'data': lux_status}
                        self.queue.put(result)
            time.sleep(0.1)

    def stop(self):
        ''' Stop handler '''
        # Stop all sensors
        for sensor in self.sensorList:
            sensor.stop()
        # Stop checking
        self.running = False


def sendJSON(ip, port):
    ''' Used for diagnostic sending JSON messages to ip and port '''
    import socket
    import json

    input = raw_input('Enter JSON: ')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(json.dumps(input))
        response = sock.recv(1024)
        print "sendJSON_Received: {}".format(response)
    finally:
        sock.close()


def triggerEvent(ip, port, data):
    ''' Trigger Event  '''
    import socket
    import json

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, port))
        sock.sendall(json.dumps(data))
        response = sock.recv(1024)
        print edoGetDateTime() + ": tiriggerEvent_Received: {}".format(response)
    except Exception as e:
        return str(e)
    else:
        sock.close()
        return response


def createInitialConfig(configObject):
    ''' Creating initial configuration '''
    configObject.AddUpdate('server', {'DB_IP': '127.0.0.1',
                                      'DB_USER': 'user',
                                      'DB_PASS': 'pass',
                                      'DB_NAME': 'edoAutoHome'})
    configObject.AddUpdate('client', {'MASTER_IP': '127.0.0.1',
                                      'DEVICEID': '1'})
    configObject.AddUpdate('sensor_motionpir', {'ENABLE': 'false',
                                                'ATTR_ID': '1',
                                                'PIN': '4',
                                                'INTERVAL': '0.1'})
    configObject.AddUpdate('sensor_doorswitch', {'ENABLE': 'false',
                                                 'ATTR_ID': '2',
                                                 'PIN': '17',
                                                 'INTERVAL': '0.1'})
    configObject.AddUpdate('trigger_tellstickswitch', {'ENABLE': 'false',
                                                       'PIN': '18',
                                                       'INTERVAL': '0.01'})
    configObject.AddUpdate('lcd', {'ENABLE': 'false',
                                   'INTERVAL': '0.1'})
    configObject.AddUpdate('main', {'DEBUG': 'true',
                                    'MODE': 'CLIENT',
                                    'LISTEN_PORT': '3000',
                                    'BUTTON': 'false',
                                    'LCD': 'true'})


def startLoop(mode='client', queue=None, **kwargs):
    '''
    Function to start listening client
    keywords:
        sensors=List(sensors)
        listen_port=3000
        deviceId=X
        loggerObject=None
        mode=server/client
    '''
    # Parse arguments
    if kwargs['listen_port'] is not None:
        listen_port = int(kwargs['listen_port'])
    else:
        listen_port = 3000

    # Create triggerQueue if none exists
    if queue is None:
        triggerQueue = Queue.Queue()
    else:
        triggerQueue = queue

    # Start triggerListener (for incoming events to trigger actions)
    objTriggerListener = triggerListener(listen_port, triggerQueue)
    objTriggerListener.start()
    # Start triggerHandler (handling incoming events)
    objTriggerQueueHandler = triggerQueueHandler(mode, triggerQueue, **kwargs)
    objTriggerQueueHandler.start()
    # Start check of Sensors (checking sensors that trigger events)
    if kwargs['sensors'] is not None:
            objSensorCheck = sensorCheck(triggerQueue, kwargs['deviceId'], kwargs['sensors'])
            objSensorCheck.start()
            print("Client started and monitoring sensors: " + str(kwargs['sensors']))

    # Wait for key to abort
    print("Press Enter to exit")
    raw_input()

    objTriggerListener.stop()
    objTriggerQueueHandler.stop()

    if kwargs['sensors'] is not None:
        objSensorCheck.stop()
    # Exit loop
    print("Aborted")


def getEnabledSensors(configObject, logObject=None):
    ''' configObject as argument, starts sensors and returns list of sensor-objects '''
    import json
    sensors = list()
    if configObject.get('sensor_motionpir', 'enable') == 'true':
        pin = configObject.get('sensor_motionpir', 'pin')
        # interval = configObject.get('sensor_motionpir', 'interval')
        sensor_motionpir = edoPirMotion(logObject, pin=int(pin))
        sensors.append(sensor_motionpir)
    if configObject.get('sensor_doorswitch', 'enable') == 'true':
        pin = configObject.get('sensor_doorswitch', 'pin')
        # interval = configObject.get('sensor_doorswitch', 'interval')
        sensor_doorswitch = edoSwitch(logObject, pin=int(pin))
        sensors.append(sensor_doorswitch)
    if configObject.get('sensor_dht11_humid', 'enable') == 'true':
        pin = configObject.get('sensor_dht11_humid', 'pin')
        limit = configObject.get('sensor_dht11_humid', 'limit')
        sensor_dht11_humid = edoDHT(logObject, pin=int(pin), type=0, limit=limit)
        sensors.append(sensor_dht11_humid)
    if configObject.get('sensor_dht11_temp', 'enable') == 'true':
        pin = configObject.get('sensor_dht11_temp', 'pin')
        limit = configObject.get('sensor_dht11_temp', 'limit')
        sensor_dht11_temp = edoDHT(logObject, pin=int(pin), type=1, limit=limit)
        sensors.append(sensor_dht11_temp)
    if configObject.get('sensor_mq2', 'enable') == 'true':
        adc_in = int(configObject.get('sensor_mq2', 'adc_in'))
        clockpin = int(configObject.get('sensor_mq2', 'clockpin'))
        mosipin = int(configObject.get('sensor_mq2', 'mosipin'))
        misopin = int(configObject.get('sensor_mq2', 'misopin'))
        cspin = int(configObject.get('sensor_mq2', 'cspin'))
        sleep_int = float(configObject.get('sensor_mq2', 'sleep_int'))
        check_int = int(configObject.get('sensor_mq2', 'check_int'))
        pause_int = int(configObject.get('sensor_mq2', 'pause_int'))
        limit = int(configObject.get('sensor_mq2', 'limit'))
        sensor_mq2 = edoADCmeter(adc_in, clockpin=clockpin, mosipin=mosipin, misopin=misopin, cspin=cspin, check_int=check_int, sleep_int=sleep_int, pause_int=pause_int, limit=limit, loggerObject=logObject)
        sensors.append(sensor_mq2)
    if configObject.get('sensor_luxmeter', 'enable') == 'true':
        limit = int(configObject.get('sensor_luxmeter', 'limit'))
        check_int = int(configObject.get('sensor_luxmeter', 'check_int'))
        sensor_luxmeter = edoLuxMeter(limit=limit, check_int=check_int, loggerObject=logObject)
        sensors.append(sensor_luxmeter)
    if configObject.get('sensor_power', 'enable') == 'true':
        adc_in = int(configObject.get('sensor_power', 'adc_in'))
        minref = int(configObject.get('sensor_power', 'minref'))
        clockpin = int(configObject.get('sensor_power', 'clockpin'))
        mosipin = int(configObject.get('sensor_power', 'mosipin'))
        misopin = int(configObject.get('sensor_power', 'misopin'))
        cspin = int(configObject.get('sensor_power', 'cspin'))
        sleep_int = float(configObject.get('sensor_power', 'sleep_int'))
        interval = int(configObject.get('sensor_power', 'interval'))
        limit = int(configObject.get('sensor_power', 'limit'))
        debug = json.loads(configObject.get('sensor_power', 'debug').lower())
        sensor_power = edoPowerMeter(minref, adc_in, clockpin=clockpin, mosipin=mosipin, misopin=misopin, cspin=cspin, check_int=interval, sleep_int=sleep_int, limit=limit, debug=debug, loggerObject=logObject)
        sensors.append(sensor_power)
    return sensors


def checkEventInTrigger((argDevice, argAttr, argData), trigger_json):
    ''' Function to compare attributes with json_list from config '''
    import json
    trigger_when = json.loads(trigger_json)
    result = []
    for current_cond in trigger_when:
        if current_cond['data'][0] == '=':
            if int(current_cond['dev']) == int(argDevice) and int(current_cond['attr']) == int(argAttr) and current_cond['data'][1:] == argData:
                result.append(True)
            else:
                result.append(False)
        if current_cond['data'][0] == '>':
            if int(current_cond['dev']) == int(argDevice) and int(current_cond['attr']) == int(argAttr) and float(argData) > float(current_cond['data'][1:]):
                result.append(True)
            else:
                result.append(False)
        if current_cond['data'][0] == '<':
            if int(current_cond['dev']) == int(argDevice) and int(current_cond['attr']) == int(argAttr) and float(argData) < float(current_cond['data'][1:]):
                result.append(True)
            else:
                result.append(False)
    return any(result)


class edoGmailAlarm(edoGmail):
    ''' Inherit and add new property to sendmail '''
    def __init__(self, *args, **kwargs):
        edoGmail.__init__(self, *args, **kwargs)
        self.trigger_when = None
        self.mail_to = None
        self.mail_from = None

    def trigger(self, *args, **kwargs):
        self.send(*args, **kwargs)

    def stop(self):
        print edoGetDateTime() + ": Stopping gmail"


class edoSMSAlarm(edoModemDongle):
    ''' Inherit and add new property to sendmail '''
    def __init__(self, *args, **kwargs):
        edoModemDongle.__init__(self, *args, **kwargs)
        self.trigger_when = kwargs.get('trigger_when', None)
        self.number = kwargs.get('number', None)

    def trigger(self, *args, **kwargs):
        self.send(*args, **kwargs)

    def stop(self):
        edoModemDongle.stop(self)
        print edoGetDateTime() + ": Stopping SMS"


def getEnabledAlarms(configObject, logObject=None):
    ''' configObject as argument, check enables alarms and returns list of alarm-objects '''
    alarms = list()
    if configObject.get('alarm_buzzer', 'enable') == 'true':
        pin = configObject.get('alarm_buzzer', 'pin')
        alarm_buzzer = edoBuzzer(logObject, pin=int(pin))
        alarm_buzzer.start()
        alarms.append(alarm_buzzer)
    if configObject.get('alarm_gmail', 'enable') == 'true':
        gmail_user = configObject.get('alarm_gmail', 'gmail_user')
        gmail_pass = configObject.get('alarm_gmail', 'gmail_pass')
        alarm_gmail = edoGmailAlarm(gmail_user, gmail_pass, logObject)
        alarm_gmail.trigger_when = configObject.get('alarm_gmail', 'trigger_when')
        alarm_gmail.mail_from = configObject.get('alarm_gmail', 'from')
        alarm_gmail.mail_to = configObject.get('alarm_gmail', 'to')
        alarms.append(alarm_gmail)
    if configObject.get('alarm_sms', 'enable') == 'true':
        sms_tty = configObject.get('alarm_sms', 'sms_tty')
        ## sms_port = configObject.get('alarm_sms', 'sms_port')
        sms_number = configObject.get('alarm_sms', 'sms_number')
        sms_check_int = configObject.get('alarm_sms', 'sms_check_int')
        sms_incoming_cmd = configObject.get('alarm_sms', 'sms_incoming_cmd')
        sms_trigger_when = configObject.get('alarm_sms', 'trigger_when')

        # Create SMS Dongle Object
        alarm_sms = edoSMSAlarm(logObject, tty=sms_tty, incoming_cmd=sms_incoming_cmd, check_int=sms_check_int, number=sms_number, trigger_when=sms_trigger_when, functions={'show_status_short': show_status_short, 'pause': pause})
        alarm_sms.start()
        print "Starting SMS engine thread: %s" % (str(alarm_sms),)
        # Start listening daemon - experimental
        ## objSMSListener = smsListener(sms_port, dongle=alarm_sms)
        ## objSMSListener.start()
        # Append object to alarms list
        alarms.append(alarm_sms)
    return alarms


class edoCamera():
    ''' Define class for Camera '''
    def __init__(self, camera_type, camera_name, camera_ftp_server=None, camera_ftp_port=None, camera_ftp_user=None, camera_ftp_pass=None, camera_ftp_dir=None, loggerObject=None):
        self.camera_type = camera_type
        self.camera_name = camera_name
        self.camera_ftp_server = camera_ftp_server
        self.camera_ftp_port = camera_ftp_port
        self.camera_ftp_user = camera_ftp_user
        self.camera_ftp_pass = camera_ftp_pass
        self.camera_ftp_dir = camera_ftp_dir
        self.cam_shots = []
        self.loggerObject = loggerObject
        self.objFTP = edoFTP(camera_ftp_server, camera_ftp_user, camera_ftp_pass, self.loggerObject, port=camera_ftp_port)
        self.objFTP.start()
        self.status = None

    def trigger(self):
        self.status = "capture"
        filename = "/tmp/" + edoGetDateTime().replace("-", "").replace(":", "").replace(" ", "_") + '_' + self.camera_name + ".jpg"
        if self.camera_type == 'pi':
            edoPiCamera(filename)
            self.cam_shots.append(filename)
        self.status = None

    def upload_all(self, remove=False):
        import thread
        while self.status is not None:
            time.sleep(1)
        self.objFTP.status = "transfer"
        self.objFTP.upload(self.cam_shots, self.camera_ftp_dir)
        if remove is True:
            while self.objFTP.status is not None:
                time.sleep(1)
            # Add delay to removal by thread
            thread.start_new_thread(self.remove_all, ())
            # self.remove_all()

    def remove_all(self):
        import os
        import time

        filelist = self.cam_shots
        self.cam_shots = []
        time.sleep(300)
        # Clear list of files to prevent same pic being mailed again, delay del
        for current_file in filelist:
            os.remove(current_file)

    def list_all(self):
        return self.cam_shots

    def stop(self):
        print edoGetDateTime() + ": Stopping camera " + self.camera_name
        self.objFTP.stop()


def getEnabledCameras(configObject, logObject=None):
    ''' configObject as argument, check enables cameras and returns list of camera-objects '''
    import re
    cameras = []
    all_sections = configObject.sections()
    for current_section in all_sections:
        camera_id = re.match(r'camera_([0-9]+)', current_section)
        if camera_id is not None:
            camera_name = configObject.get(current_section, 'name')
            camera_enable = configObject.get(current_section, 'enable')
            camera_type = configObject.get(current_section, 'type')
            camera_ftp_server = configObject.get(current_section, 'ftp_server')
            camera_ftp_port = configObject.get(current_section, 'ftp_port')
            camera_ftp_user = configObject.get(current_section, 'ftp_user')
            camera_ftp_pass = configObject.get(current_section, 'ftp_pass')
            camera_ftp_dir = configObject.get(current_section, 'ftp_dir')

            # Add camera to the list
            if camera_enable == 'true':
                cameras.append(edoCamera(camera_type, camera_name, camera_ftp_server, camera_ftp_port, camera_ftp_user, camera_ftp_pass, camera_ftp_dir, logObject))
    return cameras


def triggerAllCameras(cameraList):
    ''' Trigger all cameras and retuurn list of filenames '''
    # Get list of cameras
    cameras = cameraList
    # Trigger cameras
    thread_list = []
    camera_files = []
    for camera in cameras:
        t = threading.Thread(target=camera.trigger)
        t.start()
        thread_list.append(t)
    # Wait for all cameras to complete
    for thread in thread_list:
        thread.join()
    # Get names of files
    for camera in cameras:
        camera_files += camera.cam_shots
    return camera_files


def uploadAllCameras(cameraList):
    ''' Upload and remove all files from camers '''
    for camera in cameraList:
        # Enable or disable delete of files
        camera.upload_all(True)


def getSensorStatus(objDB):
    ''' Generate list of the status of current sensors in database '''
    device_attr_list = objDB.select('device_attr', "id > 0")
    result_list = []

    if device_attr_list is not None:
        for item in device_attr_list:
            dev = str(item[1])
            attr = str(item[2])
            status = str(item[3])
            date = str(item[4])
            result_list.append(date + "\nDev:" + dev + ",Attr:" + attr + "\nStatus:\n" + status)
    return result_list


def displayStatusLcd(objLcd, *args):
    ''' Display in LCD display status '''
    # If getSensorStatus is the function, then call it with objDB as argument
    if args[0].__name__ == 'getSensorStatus':
        messages = args[0](args[1])
    elif type(args) is List:
        messages = args
    else:
        messages = [args]
    for item in messages:
            objLcd.text(item, 8)


def checkDeviceCondition(objDB, argDevice, argAttr, argData):
    ''' Checks the conditions in database for argDevice, argAttribute '''
    if argData[0] == '=':
        argData = argData[1:]
        result = objDB.select('device_attr', {'device_id': argDevice, 'attr_id': argAttr, 'data': argData})
    elif argData[0] == '>' or argData[0] == '<':
        result = objDB.select('device_attr', 'device_id = ' + argDevice + ' AND attr_id = ' + argAttr + ' AND data ' + argData[0] + ' ' + argData[1:])
    else:
        result = objDB.select('device_attr', {'device_id': argDevice, 'attr_id': argAttr, 'data': argData})
    if result:
        return True
    else:
        return False


def send_reset_all_clients(AlarmList, conf):
    ''' Function to send reset_all to all clients '''
    import json
    ips = json.loads(alarm_settings.get('clients_ip', None))
    print edoGetDateTime() + ": Send Reset Sensors - " + str(ips)
    if len(ips) > 0:
        for ip, port in ips:
            triggerEvent(str(ip), int(port), 'reset_all_sensors')
            result = edoTestSocket(ip, port, logObject)
            if result == 1:
                for AlarmDev in AlarmList:
                    if AlarmDev.__class__.__name__ is "edoBuzzer" and conf.get('alarm_buzzer', 'enable') == 'true':
                        print edoGetDateTime() + ": Client %s could not be reached" % (ip,)
                        logObject.log("Client %s could not be reached" % (ip,), 'DEBUG')
                        AlarmDev.buzz_on(5)


class alarmClass():
    ''' Class that handles alarm notifications '''

    def __init__(self, objConfig, objDB, AlarmDevList, objLed, cameras):
        import json
        self.objConfig = objConfig
        self.objDB = objDB
        self.AlarmDevList = AlarmDevList
        self.objLed = objLed
        self.active = False
        self.skip = False
        self.activate = json.loads(objConfig.get('alarm', 'activate'))
        self.alarm_settings = objConfig.getAll('alarm')
        self.buzzer_settings = objConfig.getAll('alarm_buzzer')
        # self.mail_settings = objConfig.getAll('alarm_mail')
        try:
            import memcache
        except:
            print "Please install memcache to support inter-process communication"
        else:
            self.shared = memcache.Client(['127.0.0.1:11211'], debug=1)

    def check(self, argDev, argAttr, argData):
        ''' Checks the argDevice, argAttribute '''
        # Create list of results
        result = [checkDeviceCondition(self.objDB, cond_item['dev'], cond_item['attr'], cond_item['data']) for cond_item in self.activate]
        if all(result) is True and self.active is False:
            # Trigger if all is True
            print edoGetDateTime() + ": Alarm armed"
            logObject.log("Alarm armed", 'INFO')
            self.active = True
            if 'shared' in dir(self):
                self.shared.set('active', True)
            # Start blink of LED exists
            if self.objLed:
                logObject.log("Start Led blink", 'DEBUG')
                self.objLed.blink()
            # Send reset to all clients sensors to get alarm if currently
            # active
                send_reset_all_clients(AlarmDevList, self.objConfig)

        elif all(result) is False and self.active is True:
            print edoGetDateTime() + ": Alarm disarmed"
            logObject.log("Alarm disarmed", 'INFO')
            self.active = False
            if 'shared' in dir(self):
                self.shared.set('active', False)
            if self.objLed:
                logObject.log("Stop Led blink", 'DEBUG')
                self.objLed.led_off()

        if self.active is True:
            # Trigger alarm when active
            import time

            # If a pause exists in the queue
            if 'shared' in dir(self):
                pause_memcache = self.shared.get('pause')
                if pause_memcache > 0:
                    pause_memcache = int(pause_memcache)
                    print "Found pause in memcache queue for %s minutes" % (str(pause_memcache / 60),)
                    pause_memcache -= 60
                    if pause_memcache <= 0:
                        pause_memcache = 0
                        self.skip = False
                        print "Pause is complete"
                    else:
                        self.skip = True
                    self.shared.set("pause", pause_memcache)
                    time.sleep(60)
                else:
                    self.skip = False

            if not self.skip:
                for AlarmDev in AlarmDevList:
                    if AlarmDev.__class__.__name__ is "edoBuzzer" and self.objConfig.get('alarm_buzzer', 'enable') == 'true':
                        print edoGetDateTime() + ": BUZZ !!"
                        logObject.log("BUZZ !!", 'DEBUG')
                        AlarmDev.buzz_on(0.5)
                        time.sleep(0.2)
                        AlarmDev.buzz_on(0.5)
                    if AlarmDev.__class__.__name__ is "edoGmailAlarm":
                        mail_body = edoGetDateTime() + ": " + str(argData)
                        if checkEventInTrigger((argDev, argAttr, argData), AlarmDev.trigger_when):
                            dev_name = get_dev_name(argDev, self.objDB)
                            attr_name = get_attr_name(argAttr, self.objDB)
                            print edoGetDateTime() + ": Mail Alarm Sent, " + dev_name + ", " + attr_name
                            logObject.log("Alarm mail sent, " + dev_name + ", " + attr_name, 'INFO')
                            # Trigger and get images from all cameras
                            cam_shots = triggerAllCameras(cameras)
                            # Send email
                            AlarmDev.trigger(AlarmDev.mail_to, "HomeAlarm Trigger " + dev_name + ", " + attr_name + " " + str(argData), mail_body, cam_shots)
                            # Upload pictrues to FTP
                            uploadAllCameras(cameras)
                    if AlarmDev.__class__.__name__ is "edoSMSAlarm":
                        sms_body = edoGetDateTime() + ": " + str(argData)
                        if checkEventInTrigger((argDev, argAttr, argData), AlarmDev.trigger_when):
                            dev_name = get_dev_name(argDev, self.objDB)
                            attr_name = get_attr_name(argAttr, self.objDB)
                            print edoGetDateTime() + ": SMS Alarm Sent, " + dev_name + ", " + attr_name
                            logObject.log("Alarm SMS sent, " + dev_name + ", " + attr_name, 'INFO')
                            # Send sms
                            AlarmDev.trigger(AlarmDev.number, sms_body + "..HomeAlarm Trigger " + dev_name + ", " + attr_name + " " + str(argData))
                        # Feed event and have mail sent if true
                        # AlarmDev.trigger(self.objDB, argDev, argAttr, argData)


if __name__ == "__main__":
    ''' Here starts the program '''

    parser = argparse.ArgumentParser(description='This pythonscript is used for home-automation')
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--version", action="version", version=__version__)
    # choice.add_argument("--sendjson", help="send json-messages to host", metavar="host ip", nargs=argparse.REMAINDER)
    choice.add_argument("--sendjson", help="send json-messages to host", metavar=("host", "ip"), nargs=2)
    choice.add_argument("--start", help="Starts the home-automation", action="store_true")
    choice.add_argument("--createdb", help="Create initial database", action="store_true")
    choice.add_argument("--list_device", help="List devices in database", action="store_true")
    choice.add_argument("--add_device", help="Add device to database", action="store_true")
    choice.add_argument("--list_attribute", help="List attributes in database", action="store_true")
    choice.add_argument("--add_attribute", help="Add attribute to database", action="store_true")
    choice.add_argument("--attr_to_dev", help="Assign attribute to device", action="store_true")
    choice.add_argument("--list_attrdev", help="List attribute to device", action="store_true")
    choice.add_argument("--show_status_short", help="Show all statuses short", action="store_true")
    choice.add_argument("--show_status_json", help="Show all statuses in json", action="store_true")
    choice.add_argument("--show_onoff", help="Return 0 if alarm is armed/on, 1 if it is disarmed/off", action="store_true")
    choice.add_argument("--pause_hours", help="Pause alerts for X hours", type=int, metavar="hours", choices=xrange(0, 200), default=None)
    choice.add_argument("--show_history", help="Show history", action="store_true")
    choice.add_argument("--send_history", help="Send history by mail using configuration in alarm_gmail", action="store_true")
    args = parser.parse_args()
    if len(sys.argv) == 1: parser.print_help()

    # Create log object
    logObject = edoClassFileLogger('edoAutoHome.log', 1, 5, 'DEBUG')

    # Create config file if required
    if os.path.isfile(CONFIG_FILE):
        configObject = edoClassConfig(CONFIG_FILE, logObject)
        main_settings = configObject.getAll('main')
        server_settings = configObject.getAll('server')
        client_settings = configObject.getAll('client')
        alarm_settings = configObject.getAll('alarm')
        alarm_mail_settings = configObject.getAll('alarm_gmail')
    else:
        configObject = edoClassConfig(CONFIG_FILE, logObject)
        createInitialConfig(configObject)
        print("Configuration created, please restart")
        sys.exit(0)

    if args.sendjson:
        # Start json send function
        ip, port = args.sendjson
        print "Send JSON to host: " + ip + ":" + port
        data = None
        while not data == '':
            data = raw_input('Enter data: ')
            edoSendSocket(ip, int(port), json.dumps(data))
        sys.exit(0)

    if args.createdb:
        # Create database using variables
        create_schema(server_settings['db_ip'],
                      server_settings['db_user'],
                      server_settings['db_pass'],
                      server_settings['db_name'], logObject)
        sys.exit(0)

    if args.add_device:
        # Add device to the database
        device_id = raw_input("Enter id: ")
        device_name = raw_input("Enter Name of device: ")
        device_location = raw_input("Enter location of device: ")
        add_device(server_settings['db_ip'],
                   server_settings['db_user'],
                   server_settings['db_pass'],
                   server_settings['db_name'],
                   device_id, device_name, device_location, logObject)

    if args.list_device:
        # List devices in database
        list_device(server_settings['db_ip'],
                    server_settings['db_user'],
                    server_settings['db_pass'],
                    server_settings['db_name'], logObject)

    if args.add_attribute:
        # Add attribute to the database
        attr_id = raw_input("Enter id: ")
        attr_name = raw_input("Enter Name of attribute: ")
        add_attribute(server_settings['db_ip'],
                      server_settings['db_user'],
                      server_settings['db_pass'],
                      server_settings['db_name'],
                      attr_id, attr_name, logObject)

    if args.list_attribute:
        # List devices in database
        list_attribute(server_settings['db_ip'],
                       server_settings['db_user'],
                       server_settings['db_pass'],
                       server_settings['db_name'], logObject)

    if args.list_attrdev:
        # List attribute to devices in database
        list_attr_dev(server_settings['db_ip'],
                      server_settings['db_user'],
                      server_settings['db_pass'],
                      server_settings['db_name'], logObject)

    if args.attr_to_dev:
        # Associate attribute to device
        attr_id = raw_input("Enter attribute id: ")
        dev_id = raw_input("Enter device id to associate attribute to: ")
        attr_to_dev(server_settings['db_ip'],
                    server_settings['db_user'],
                    server_settings['db_pass'],
                    server_settings['db_name'],
                    attr_id, dev_id, logObject)

    if args.show_status_short:
        print show_status_short()

    if args.show_status_json:
        print show_status_json()

    if args.show_onoff:
        # Show status if alarm is armed or disarmed
        ''' Old method
        import re
        import glob
        for fn in glob.glob('./edoAutoHome.log.*'):
            with open(fn, 'r') as f:
                lines = f.readlines()
                found = [(i, item) for i, item in enumerate(lines) if re.search('armed', item)]
                if str(found[-1:]).find('disarmed'):
                    print "Disarmed"
                    sys.exit(1)
                else:
                    print "Armed"
                    sys.exit(0)
        '''
        try:
            import memcache
        except:
            print "Please install memcache to support reading status"
        else:
            shared = memcache.Client(['127.0.0.1:11211'], debug=1)
            status = shared.get('active')
            print "Get value from memcache %s" % (str(status),)
            if status:
                print "Armed"
                if configObject.get('alarm_sms', 'enable') == 'true':
                    sms_number = configObject.get('alarm_sms', 'sms_number')
                # Add SMS to queue
                shared.set('sms', (sms_number, show_status_short()))
                sys.exit(0)
            else:
                print "Disarmed"
                sys.exit(1)

    if args.pause_hours is not None:
        pause(args.pause_hours)

    if args.show_history:
        print show_history(mail_settings=None, length=100, mailer='no')
        # show_history(mail_settings=None, length=100, mailer='no')

    if args.send_history:
        print show_history(mail_settings=alarm_mail_settings, length=100, mailer='yes')

    if args.start:
        # Get list of cameras
        cameras = getEnabledCameras(configObject, logObject)

        # If server-mode
        if main_settings['mode'] == 'server':
            db_ip = server_settings['db_ip']
            db_user = server_settings['db_user']
            db_pass = server_settings['db_pass']
            db_name = server_settings['db_name']
            objDB = edoClassDB('mysql', (db_ip, 3306, db_user, db_pass, db_name), logObject)

            # Get list of enabled alarm devices
            AlarmDevList = getEnabledAlarms(configObject, logObject)

            # Create Alarm Notifier object
            if alarm_settings['led'] == 'true':
                objLed = edoLed(pin=int(alarm_settings['led_pin']))
                objLed.start()
                objLed.led_on(1)
                objLed.led_off()
            else:
                objLed = None
            objAlarm = alarmClass(configObject, objDB, AlarmDevList, objLed, cameras)
        else:
            objDB = None
            objAlarm = None

        '''
        # Trigger cameras
        thread_list = []
        camera_files = []
        for camera in cameras:
            t = threading.Thread(target=camera.trigger)
            t.start()
            thread_list.append(t)
        # Wait for all cameras to complete
        for thread in thread_list:
            thread.join()
        # Get names of files
        for camera in cameras:
            camera_files += camera.cam_shots
        # Upload files
        print camera_files
        camera.upload_all(True)
        '''

        # Get list of Sensors
        sensors = getEnabledSensors(configObject, logObject)

        # Check for the components to be used
        # LCD, and Button to control
        if main_settings['lcd'] == 'true':
            objLcd = edoLcd()
            objLcd.start()
            localIP = edoGetLocalIP()
            objLcd.text("edoAutoHome\n" + localIP, 2)
            objLcd.change_default("edoAutoHome\n" + localIP)
            # Check for button
            if main_settings['button'] == 'true' and main_settings['mode'] == 'server':
                # 1 click, call displayStatudLcd, print all sensors
                objButton = edoButton(2, {1: [displayStatusLcd, [objLcd, getSensorStatus, objDB]]})
                objButton.start()
        else:
            objLcd = None

        triggerQueue = Queue.Queue()
        startLoop(main_settings['mode'],
                  triggerQueue,
                  deviceId=client_settings['deviceid'],
                  sensors=sensors,
                  listen_port=main_settings['listen_port'],
                  lcd=objLcd,
                  db=objDB,
                  alarm=objAlarm,
                  loggerObject=logObject)

        # End LCD
        if main_settings['lcd'] == 'true':
            objLcd.text("STOP PROGRAM", 3)
            time.sleep(5)
            objLcd.stop()
        # End Button
        if main_settings['button'] == 'true':
            objButton.stop()
        # End led
        if alarm_settings['led'] == 'true':
            objLed.stop()

        # Stop enabled alarm components
        if main_settings['mode'] == 'server':
            for alarm in AlarmDevList:
                alarm.stop()

        # Stop enabled cameras
        for camera in cameras:
            camera.stop()

        # Update memcache if it exists
        try:
            import memcache
        except:
            print "Please install memcache to support inter-process communication"
        else:
            shared = memcache.Client(['127.0.0.1:11211'], debug=1)
            shared.set('active', False)
            shared.set('pause', 0)
