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
..* Raspberry Pi
..* Nokia LCD - that display when there are activity
..* Button - when pressed will display current status of the sensors
..* PIR-senosrs - detects motions
..* Magnetic Switch - connect to door and register if open/closed

**Too sleepy to add more this time..**

*Software*
* Master/Client setup
* Communicates with remote devices (RPI's) with their sensors
* Clients sends events to Master
* Master stores data to MySQL


-------------------------
Pictures
-------------------------
*Main Board based on RaspberryPI, NokiaLCD, PIR-sensor and Magnetic Door Switch*
![Main Board](https://github.com/engdan77/edoautohome/blob/master/IMG_1_MainBoard.jpg)

*Scematic over the Main Board*
![Main Board](https://github.com/engdan77/edoautohome/blob/master/IMG_1_MainBoard.jpg)

