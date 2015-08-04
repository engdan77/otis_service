edoAutoHome
==============

Author
--------------
Very short introduction is that my name is Daniel Engvall and lives in Sweden/Stockholm and have programming as his hobby (amongst other stuff) :)

Background
--------------

This is a project for home automation developed in Python 2.x
Some of the thoughts that I've had in mind when starting this have been 

- Hardware based on Raspbery PI ver. B that has the benefit being cheap and also have GPIO to support sensors of all kind (also supports most Adruino sensors)
- Software developed in Python 2.x which is portable and easy to work with
- Support meassurement-sensors such as door-switches, PIR-sensor, Non-Intrusive PowerMeter and Temperature
- Trigger alerts (e-mail and SMS) when sensors reach defines threshold
- Support TellStick to manager electrical outlets and wireless Temperature sensors
- Web-interface for reading sensors
- Native Mobile Application supporting ios/Android for reading sensors

As a front-end use a framework such as Web2Py, and mobile application developed
![Use-Case](https://github.com/engdan77/edoautohome/blob/master/pics/use_case.jpg)


-------------------------
History
-------------------------

**2014-08-12**

I've been working on this project on my spare time for a few months and thought I would share this to github in case others would be interessted of the work or contribute with ideas.
I will likely spend more time on this documentation but this is in short what have been developed

*Hardware*
* Main Board *[Device 1]* (the device that acts as master to the networked devices)
 * Raspberry Pi
 * Nokia LCD - that display when there are activity
 * Button - when pressed will display current status of the sensors
 * PIR-senosrs - detects motions
 * Magnetic Switch - connect to door and register if open/closed

* Kitchen Board *[Device 2]*
 * Raspberry Pi
 * Non-Intrusive Current Meter - used to determine whether stove is turned on when leaving home

*Software*
  * Master/Client setup
  * Communicates with remote devices (RPI's) with their sensors
  * Clients sends events to Master
  * Master stores data to MySQL

**2014-10-16**
Eventually built the device to be kept in the livingroom with majority of the the sensors, and developed classes for those.

*Hardware*
* Livingroom Board *[Device 3]*
 * Raspberry Pi
 * DHT11 sensor for humidity and temperature
 * MQ2 smoke sensor
 * TSL2561 Lux Sensor for meassure brightness

*Software*
 * Tweaks made to Current Meter class to fix false alerts
 * Classed developed for DHT11, MQ2 and TSL2561 creating threads for monitoring

**2015-02-22**

I've now published my Web frontend that I've developed using the Web2Py framework which you could now use to build graphs for all sensors, please watch it out at https://github.com/engdan77/edoWeb

**2015-02-26**

Now I've finalised the SMS-functionality that currently been tested with Huawei E392, that also supports incoming sms to trigger developed function or bash-command and return its result back as SMS.
I've also included to github the edoWeb-project that includes a web-frontend based on Web2Py framework and PyGal for drawing graphs, see further down for details.

**2015-08-03**

I've now published my mobile application compiled for IOS/Android (as well as Mac OSX/Windows) that communicated with the RaspberryPi server using JSON and draws graphs historically. The intention with this app was to install on cheap tablet that you could install anywhere in the home where you like to read the current status of your sensors, please check out https://github.com/engdan77/edoAutoHomeMobile


----------------------
Rough cost estimation for hardware required
----------------------

This solutions is very affordable in comparison with many commercial solutions, most sensors could be purchased cheap from eg. Asia.

| Item        | ~Cost  |
| ------------- | -----:|
| RaspberryPi Model B |    $25 |
| Wifi-dongle |    $20 |
| Breadboard, GPIO-port |    $9 |
| Jumper wires      | $3 |
| Buzzer |    $3 |
| Display 1.6"      |   $4 |
| Door-switch |    $3 |
| PIR-sensor |    $2 |
| MQ2-gas sensors |    $6 |
| DHT11 - temp/humid |    $4 |
| Current-sensor |    $5 |
| Lux-sensor |    $2 |
| Led |    $1 |
| 3G-dongle |    $? |
| _Total_ |   _~$87_ |


----------------------
Installing the dependencies and edoAutoHome
----------------------
```

[Make placeholder for modules]
# mkdir git
# cd git

[Download edoAutoHome]
# git clone https://github.com/engdan77/edoautohome.git

[Install MySQLdb]
# apt-get install python-mysqldb

[Install wiringpi2 and spidev]
# git clone git://git.drogon.net/wiringPi
# cd wiringPi
# ./build
# cd ..

# apt-get install python-dev python-imaging python-imaging-tk python-pip
# pip install wiringpi
# pip install wiringpi2

The program we will use require spidev to be activated. The kernel module should then be activated. To do so, comment the line blacklist spi-bcm2708 by adding a heading # in the file /etc/modprobe.d/raspi-blacklist.conf then reboot the Raspberry Pi to activate this module.

# pip install spidev

[Installing Adafruit's Raspberry-Pi Python Code Library]
# apt-get install python-smbus
# git clone https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code.git
# cp Adafruit-Raspberry-Pi-Python-Code/Adafruit_I2C/Adafruit_I2C.py edoautohome/

[Install modile for piCamera]
# apt-get install python-picamera

[Installing module for pcd8544 LCD display]
# git clone https://github.com/XavierBerger/pcd8544.git
# cd pcd8544
# ./setup.py clean build 
# sudo ./setup.py install
# cd ..

[Installing memcached - optionally for SMS-gateway]
# sudo apt-get install memcached

[Installing Web-frontend - Optionally]
Read instructions found at https://github.com/engdan77/edoWeb


[Installing Mobile App for readings - Optionally]
Read instructions found at https://github.com/engdan77/edoAutoHomeMobile
```

----------------------
Command Line Arguments
----------------------

```
usage: edoAutoHome.py [-h] [--version] [--sendjson host ip] [--start]
                      [--createdb] [--list_device] [--add_device]
                      [--list_attribute] [--add_attribute]

This pythonscript is used for home-automation

optional arguments:
  -h, --help          show this help message and exit
  --version           show program's version number and exit
  --sendjson host ip  send json-messages to host
  --start             Starts the home-automation
  --createdb          Create initial database
  --list_device       List devices in database
  --add_device        Add device to database
  --list_attribute    List attributes in database
  --add_attribute     Add attribute to database
  --show_status_short  Show all statuses short
  --show_onoff         Return 0 if alarm is armed/on, 1 if it is disarmed/off
```



-------------------------
Keywords
-------------------------

**device**
Represents the device that you run the software on

**attribute**
This represents the sensor or unit that you will recieve or send data to (e.g. TellSteck-Outlet, PIR-sensor)

**larm-mode** 
This is when main board will be monitoring for any threasholds breaches of any sensors, and when that happens trigger e-mail (or SMS)

-------------------------
Currently Support Sensors and Units
-------------------------

* PIR-sensor *[Attribute 1]*  - http://www.kjell.com/sortiment/el/elektronik/mikrokontroller/arduino/rorelsedetektor-p87892
* Magnetic Switch *[Attribute 2]* - http://www.kjell.com/sortiment/hus-halsa-fritid/larm-sakerhet-overvakning/larm/detektorer-sensorer-brytare/magnetkontakt-nc-med-ledning-p50501
* Nokia LCD (currently used on Main Board to display status-changes) - https://learn.adafruit.com/nokia-5110-3310-monochrome-lcd
* Buzzer (currently used to notify when larm is activated, or sensors trigger it) - http://www.kjell.com/sortiment/el/elektronik/mikrokontroller/arduino/aktiv-buzzer-for-arduino-p87881
* Led (this is show when larm-mode is enabled by blinking)
* Non-Intrusive Current Meter *[Attribute 3]* (currently monitoring if stove is left on when leaving house) - https://www.sparkfun.com/products/11005
* RaspberryPI-camera - http://www.raspberrypi.org/product/camera-module/
* DHT11 - https://learn.adafruit.com/dht
* MQ2 -  http://www.seeedstudio.com/depot/datasheet/MQ-2.pdf
* TSL2561 - https://learn.adafruit.com/tsl2561
* 2G/3G Dongle - Send alerts by SMS (tested using Huawei E392)

-------------------------
Planned Support Sensors and Units
-------------------------

* Foscam Wifi Webcam - http://foscam.us/foscam-fi8918w-wireless-ip-camera-11.html
* TellStick Duo - http://www.telldus.se/products/tellstick_duo
* TellStick Temperature Sensors - http://www.clasohlson.com/se/Ekstra-temperaturgiver-hygrometer/Pr365123000


-------------------------
Configuration Example
-------------------------

	[server]
	db_user = edoAutoHome
	db_name = edoAutoHome
	db_pass = xxx
	db_ip = 192.168.200.1

This part describes the credentials and IP of the MySQL datase you use that software store all historical data to

	[client]
	deviceid = 1
	master_ip = 127.0.0.1

If the roles is set as "client" (see in "main" section) you defined the IP of the master device that client will communicate with, otherwise use localhost if Master

	[sensor_motionpir]
	enable = true
	attr_id = 1
	interval = 0.1
	pin = 4

This is the first sensor developed referred as attribite_id 1, which is PIR-sensor polling its data evert 0.1s
And where GPIO port 4 is used to retrieve the data, look at schematics for how to connect wiring

	[sensor_doorswitch]
	enable = true
	attr_id = 2
	interval = 0.1
	pin = 17

This is the second sensor which is magnetic door switch.

	[alarm]
	activate = [{"dev": 1, "attr": 2, "data": "=Door Close"}]
	led = true
	led_pin = 25

This is the defintion what criteria should enable larm-mode to true (see trigger-config), and also if led is wired which GPIO connected to identify by blinking led when active. 

	[alarm_buzzer]
	trigger_when = [{"dev": 1, "attr": 1, "data": "=Motion"}]
	enable = true
	pin = 27

When you have a buzzer connected to main board, you can specify it should be triggere. But in the code it will when enabled be notifying when larm is activated

	[alarm_gmail]
	enable = true
	trigger_when = [{"dev": 1, "attr": 1, "data": "=Motion"}]
	gmail_user = xxx
	gmail_pass = xxx
	from = xxx@gmail.com
	to = xxx@xxx
	cameras = camera_hall

This section is used to define when an mail (currently gmail) should be sent, using which credentials. And also if Cameras are installed the software will take a picture attaching to that message.

	[camera_1]
	name = hall
	enable = true
	type = pi
	ftp_server = 192.168.200.1
	ftp_port = xxx
	ftp_user = xxx
	ftp_pass = xxx
	ftp_dir = xxx/camera

This example is to specify when you have a camera of type=pi, where it should FTP those images.
The naming standard of those sections are [camera_x] where X is numeric.

	[main]
	debug = true
	lcd = true
	button = true
	listen_port = 3000
	mode = server

This section is to define the main options such as

**debug:** enable or disable verbose logging

**lcd:** if you connected lcd to the main board - see schematics

**button:** if button is installed on mainboard - see schematics

**listen_port:** this is the TCP-port that the software listens for incoming events (master for get updates from clients, clients to retieve "update_me" event from master)

**mode:** could either be *"server"* or *"client"*

	[sensor_power]
	enable = false
	adc_in = 0
	minref = 510
	clockpin = 18
	mosipin = 24
	misopin = 23
	cspin = 25
	sleep_int = 0.00001
	attr_id = 3
	limit = 30
	debug = false
	interval = 1

This sections defined the "non-intrusive current meter" currently attached to my stove at home, you may have to tweak the minref to get the proper values. The other parameters defined which pins you've attached the MCP3008 to (ADC).

	[sensor_dht11_humid]
	enable = true
	limit = 2
	type = 0
	pin = 4
	check_int = 10
	attr_id = 4

	[sensor_dht11_temp]
	enable = true
	limit = 1
	type = 1
	pin = 4
	check_int = 10
	attr_id = 5

DHT11 is a combined humid/temp sensor.

	[sensor_mq2]
	enable = true
	adc_in = 0
	clockpin = 18
	mosipin = 24
	misopin = 23
	cspin = 25
	sleep_int = 1
	limit = 3
	sleep_int = 1
	pause_int = 10
	check_int = 1
	attr_id = 6
	debug = false

The configuration for the MQ2-sensor (smoke detection) connected through a MCP3008 (ADC) and is basically the same configuration as for the above power-meter.

	[sensor_luxmeter]
	enable = true
	limit=5
	check_int = 10
	attr_id = 7

Configuration for the lux/brightness-meter that would indicate when it gets bright/dark.

	[alarm_sms]
	enable = true
	trigger_when = [{"dev": 3, "attr": 1, "data": "=Motion"},{"dev": 3, "attr": 4, "data": ">40"},{"dev": 3, "attr": 5, "data": ">33"},{"dev": 2, "attr": 3, "data": ">10"}]
	sms_incoming_cmd = {'files': 'ls', 'status': 'show_status_short'}
	sms_number = 070xxxxxxx
	sms_port = 3001
	sms_tty = /dev/ttyUSB0
	sms_check_int = 10

SMS configuration for those with Huawei 3G/4G dongles (such as E392) and like to use this to get informed when a sensor reaches its threshold or being able to recieve SMS-text with keyword "status" to send sensor-status back in return.

**trigger_when:** Used to define which sensors and what threshold/keyword needs to be matched to send this alert as SMS

**sms_incoming_cmd:** {'sms-keyword receieved': 'python function / external bash-command'}

**sms_number:** The number to whom you would send the messages to

**sms_port:** For future use building a TCP-socket server to listen for SMS to send

**sms_tty:** Determine which device the USB dongle listens to

**sms_check_int:** The interval which the SMS-listener polls queue

**Hints:**

* To test Huawei modem in advance you could install "gammu" for Linux and test as 'echo "All your base are belong to us" | gammu sendsms TEXT 0704xxxx'

* Some modems such as E392 is recognized as mass-storage device, this could be solved by installing "usb_modeswitch" and use it as 'usb_modeswitch -c /usr/share/usb_modeswitch/12d1\:1505 -v 12d1 -p 1505 -W'


-------------------------
Trigger/Activate Definition
-------------------------
Example: 
	activate = [{"dev": 1, "attr": 2, "data": "=Door Close"}]

dev: This is device-number registered
attr: This is the attribute, same as sensor or unit
data: This is the critera where "=" means it should give you that exact data, or > / < would be used to specify a numeric threshold

-------------------------
Adding sensors
-------------------------

*Step 1)* Create class inheriting Threading.thread with the following standard methods and attributes

- self.queue
- run() - to be started  
- stop() - called when stopping application
- get() - called to get the values from queue

ex.

	class edoSwitch(threading.Thread):
	    '''
	    Class object to handle door switch
	    object = edoSwitch(pin=18, check_int=0.5, logObject)
	    '''
	    def __init__(self, loggerObject=None, **kwargs):
		threading.Thread.__init__(self)
		import Queue
		import RPi.GPIO as io

		self.objLog = loggerObject
		self.queue = Queue.Queue()
		self.running = False
		self.status = None

		if 'pin' in kwargs:
		    self.pin = kwargs['pin']

	    def run(self):
		import time
		import os
		import RPi.GPIO as io

		self.running = True
		# Get initial status and supply to queue
		self.queue.put((epoch, self.status))

		while self.running:
		    # Get current door status
		    # Pause for next poll
		    time.sleep(self.check_int)

	    def stop(self):
		self.running = False

	    def get(self, past_seconds=0):
		''' Get the motions within the past seconds '''
		import time
		import Queue
		self.all_status = []
		while True:
		    try:
			switch_status = self.queue.get(block=False)
		    except Queue.Empty:
			break
		    else:
			now = time.time()
			if past_seconds > 0:
			    if switch_status[0] >= now - past_seconds:
				self.all_status.append(switch_status)
			else:
			    self.all_status.append(switch_status)
		return self.all_status


*Step 2)* Add definition of new attribute (sensor) in edoAutoHome.conf with those attribute required 

- Name what you want as long as you add it to configParser
- Assure to assign a unique attr_id (Attribute ID)

ex. 

	[sensor_doorswitch]
	enable = false
	attr_id = 2
	interval = 0.1
	pin = 17

*Step 3)* Add get Enabled Sensors = Handler of parsing configuration file getting actual sensors

ex.

	def getEnabledSensors(configObject, logObject=None):
	....
	if configObject.get('sensor_motionpir', 'enable') == 'true':
	    pin = configObject.get('sensor_motionpir', 'pin')
	    # interval = configObject.get('sensor_motionpir', 'interval')
	    sensor_motionpir = edoPirMotion(logObject, pin=int(pin))
	    sensors.append(sensor_motionpir)
	if configObject.get('sensor_doorswitch', 'enable') == 'true':
	    pin = configObject.get('sensor_doorswitch', 'pin')

*Step 4)* Updating TriggerQueue Handler = Responsible for adding (incoming) “alerts” in queue into Database

ex.

	class triggerQueueHandler(threading.Thread):
	...
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



*Step 5)* Updating SensorCheck Handler = When sensor enabled, this class responsible for starting the thead for this check

ex. 

	class sensorCheck(threading.Thread):
	...
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


*Step 6)* Create attributes to database, associate and associate to device

ex.

	~/git/edoautohome # ./edoAutoHome.py --list_device
	((1L, 1L, 'hall', 'Solna'), 
	 (2L, 2L, 'kitchen', 'Solna'), 
	 (3L, 3L, 'livingroom', 'Solna'))

	~/git/edoautohome # ./edoAutoHome.py --list_attribute
	((1L, 1L, 'Motion'), 
	 (2L, 2L, 'Door'), 
	 (3L, 3L, 'Stove'), 
	 (4L, 4L, 'Humidity'), 
	 (5L, 5L, 'Temperature'))

	~/git/edoautohome # ./edoAutoHome.py --add_attribute
	Enter id: 6
	Enter Name of attribute: Smoke

	~/git/edoautohome # ./edoAutoHome.py --list_attrdev
	((1L, 1L, '2', 'Door Open', '2014-10-17 18:58:46'), 
	 (2L, 2L, '3', '2', '2014-10-18 09:09:13'), 
	 (3L, 1L, '1', 'Motion', '2014-10-18 11:29:26'), 
	 (4L, 3L, '4', '32.0', '2014-10-17 09:04:42'), 
	 (5L, 3L, '5', '27.0', '2014-10-17 09:04:43'))

	~/git/edoautohome # ./edoAutoHome.py --attr_to_dev
	Enter attribute id: 6
	Enter device id to associate attribute to: 3

	~/git/edoautohome # ./edoAutoHome.py --list_attrdev
	((1L, 1L, '2', 'Door Open', '2014-10-17 18:58:46'), 
	 (2L, 2L, '3', '2', '2014-10-18 09:09:13'), 
	 (3L, 1L, '1', 'Motion', '2014-10-18 11:29:26'), 
	 (4L, 3L, '4', '32.0', '2014-10-17 09:04:42'), 
	 (5L, 3L, '5', '27.0', '2014-10-17 09:04:43'), 
	 (6L, 3L, '6', 'None', '2014-10-18 12:16:11'))



-------------------------
Example of Output
-------------------------
	pi@raspberrypi ~/edoAutoHome $ sudo python edoAutoHome.py --start                                                                  
	TriggerListener loop running in thread: Thread-8                                                                                   
	Client started and monitoring sensors: [<edoPirMotion(Thread-4, started -1293638544)>, <edoSwitch(Thread-5, started -1302027152)>] 
	Press Enter to exit                                                                                                                
	2014-08-13 07:18:11: Handling trigger in queue {'data': [(1407907091, 'Open')], 'attr_id': 2, 'deviceId': '1', 'type_id': 1}       
	2014-08-13 07:18:19: Handling trigger in queue {'data': [1407907099], 'attr_id': 1, 'deviceId': '1', 'type_id': 1}                 
	2014-08-13 07:18:33: Recieved - {"data": [[1407907112, 100]], "attr_id": 3, "deviceId": 2, "type_id": 1}                           
	2014-08-13 07:18:33: Handling trigger in queue {u'attr_id': 3, u'data': [[1407907112, 100]], u'deviceId': 2, u'type_id': 1}        
	2014-08-13 07:18:47: Recieved - {"data": [[1407907127, 0]], "attr_id": 3, "deviceId": 2, "type_id": 1}                             
	2014-08-13 07:18:47: Handling trigger in queue {u'attr_id': 3, u'data': [[1407907127, 0]], u'deviceId': 2, u'type_id': 1}          
	2014-08-13 07:18:49: Handling trigger in queue {'data': [1407907128], 'attr_id': 1, 'deviceId': '1', 'type_id': 1}                 

-------------------------
Utilise interprocess SMS-gateway
-------------------------

Because there is a built-in SMS-listener running if enabled in configuration

	[alarm_sms]
	enable = true
	sms_number = 070xxxxxxxx

You can then use memcache and creating a 'sms' entry that would be used as queue the SMS-listener

	# Initiate memcache if it exists
	try:
	    import memcache
	except:
	    print "Please install memcache to support reading status"
	else:
	    shared = memcache.Client(['127.0.0.1:11211'], debug=1)
	    shared.set('sms', ('mobile number', 'SMS message I like to send'))


-------------------------
Adding scheduled job to inform sensor-status by SMS when alarm is armed
-------------------------

Add entry such as below by "crontab -e"

	30 1 * * * . $HOME/.profile; cd $HOME/git/edoautohome ; python ./edoAutoHome.py --show_onoff >> /tmp/edoatuohome_cron.log

You may have to adjust the path to the directory where you've downloaded this script to.
In the above example at 1:30 every night if the alarm is activated (you not being at home) a list of sensors would be sent as sms to defined number in configuration

	30/3 14:39 "5" Lux Solna-livingroom
	30/3 14:37 "24" Smoke Solna-livingroom
	30/3 14:37 "Door Close" Door Solna-hall
	30/3 13:21 "Motion" Motion Solna-livingroom
	30/3 13:20 "Motion" Motion Solna-hall
	30/3 01:52 "26.0" Temperature Solna-livingroom
	28/3 05:13 "1" Stove Solna-kitchen
	8/2 19:59 "33.0" Humidity Solna-livingroom

-------------------------
Data Model
-------------------------

*Database Model*
![Main Board](https://github.com/engdan77/edoautohome/blob/master/pics/IMG_4_database_model.png)

*Class Diagram [Version: 20140809.398]*
![Main Board](https://github.com/engdan77/edoautohome/blob/master/pics/IMG_5_ClassDiagram.jpg)

*Sequence Diagram [Version: 20140809.398]*
![Main Board](https://github.com/engdan77/edoautohome/blob/master/pics/IMG_6_SequenceDiagram.png)


-------------------------
Pictures
-------------------------
*Example of current status of sensors - based on edoWeb*
![Sensors](https://github.com/engdan77/edoWeb/blob/master/pics/edoWeb_sensors.png)
https://github.com/engdan77/edoWeb

*Picture of edoAutoHomeMobile App developed for reading sensors from your mobile device*
![mobile_app](https://github.com/engdan77/edoautohome/blob/master/pics/edoAutoHome_sensors.jpg)
https://github.com/engdan77/edoAutoHomeMobile

*Main Board based on RaspberryPI, NokiaLCD, PIR-sensor and Magnetic Door Switch*
![Main Board](https://github.com/engdan77/edoautohome/blob/master/pics/IMG_1_MainBoard.jpg)

*Scematic over the Main Board [Device 1]*
![Main Board](https://github.com/engdan77/edoautohome/blob/master/pics/IMG_2_Schematic_Main_Board.jpg)

*Scematic over the Kitchen Board [Device 2]*
![Main Board](https://github.com/engdan77/edoautohome/blob/master/pics/IMG_3_Schematic_Kitchen.jpg)

*Scematic over the Livingroom Board [Device 3]*
![Main Board](https://github.com/engdan77/edoautohome/blob/master/pics/IMG_7_Schematic_Livingroom.png)

-------------------------
Reference to other Projects and Modules
-------------------------

Special thanks to everyones excellent work..

- pcd8544
https://github.com/rm-hull/pcd8544

- RPi.GPIO
https://pypi.python.org/pypi/RPi.GPIO

- Adafruit_Python_DHT
https://github.com/adafruit/Adafruit_Python_DHT

- Adafruit_I2C
https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code

