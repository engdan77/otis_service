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

As a front-end use a framework such as Web2Py


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
```

-------------------------
History
-------------------------

**2014-08-12**
I've been working on this project on my spare time for a few months and thought I would share this to github in case others would be interessted of the work or contribute with ideas.
I will likely spend more time on this documentation but this is in short what have been developed

*Hardware*
* Main Board (the device that acts as master to the networked devices)
* Raspberry Pi
 * Nokia LCD - that display when there are activity
 * Button - when pressed will display current status of the sensors
 * PIR-senosrs - detects motions
 * Magnetic Switch - connect to door and register if open/closed

**Too sleepy to add more this time..**

*Software*
  * Master/Client setup
  * Communicates with remote devices (RPI's) with their sensors
  * Clients sends events to Master
  * Master stores data to MySQL

-------------------------
Keywords
-------------------------

device: Represents the device that you run the software on
attribute: This represents the sensor or unit that you will recieve or send data to (e.g. TellSteck-Outlet, PIR-sensor)
larm-mode: This is when main board will be monitoring for any threasholds breaches of any sensors, and when that happens trigger e-mail (or SMS)

-------------------------
Currently Support Sensors and Units
-------------------------

* PIR-sensor [Attribute 1]  - http://www.kjell.com/sortiment/el/elektronik/mikrokontroller/arduino/rorelsedetektor-p87892
* Magnetic Switch [Attribute 2]
* Nokia LCD (currently used on Main Board to display status-changes)
* Buzzer (currently used to notify when larm is activated, or sensors trigger it)
* Led (this is show when larm-mode is enabled by blinking)
* Non-Intrusive Current Meter [Attribute 3] (currently monitoring if stove is left on when leaving house)
* RaspberryPI-camera

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
debug: enable or disable verbose logging
lcd: if you connected lcd to the main board - see schematics
button: if button is installed on mainboard - see schematics
listen_port: this is the TCP-port that the software listens for incoming events (master for get updates from clients, clients to retieve "update_me" event from master)
mode: could either be "server" or "client"


-------------------------
Trigger/Activate Definition
-------------------------
Example:
	activate = [{"dev": 1, "attr": 2, "data": "=Door Close"}]

dev: This is device-number registered
attr: This is the attribute, same as sensor or unit
data: This is the critera where "=" means it should give you that exact data, or > / < would be used to specify a numeric threshold


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
Data Model
-------------------------

Document to be supplied soon


-------------------------
Pictures
-------------------------
*Main Board based on RaspberryPI, NokiaLCD, PIR-sensor and Magnetic Door Switch*
![Main Board](https://github.com/engdan77/edoautohome/blob/master/pics/IMG_1_MainBoard.jpg)

*Scematic over the Main Board*
![Main Board](https://github.com/engdan77/edoautohome/blob/master/pics/IMG_2_Schematic_Main_Board.jpg)

