#!/usr/bin/env python2.7

# edo.py - This Module is for the most used classes and methods
# URL: https://github.com/engdan77/edoautohome
# Author: Daniel Engvall (daniel@engvalls.eu)

__version__ = "$Revision: 20150330.1235 $"

import sys
import threading
import SocketServer


def edoGetDateTime():
    import time
    return time.strftime("%Y-%m-%d %H:%M:%S")


def log_stderr(message, level='ERROR', logObject=None):
    ''' This is a function to log to stderr if logObject is missing (not used) '''
    if logObject is None and (level == 'ERROR' or level == 'CRITICAL'):
        sys.stderr.write(str(message) + "\n")
    else:
        logObject.log(message, level)


class edoClassSyslogLogger():
    '''
    This is a class to create a syslog-logger object
    address: ip or address to syslog server
    port: default port udp 514
    '''

    def __init__(self, address, port=514, defaultlevel='INFO'):
        import logging
        from logging.handlers import SysLogHandler

        self.oLogger = logging.getLogger(__name__)

        if defaultlevel == 'INFO':
            self.oLogger.setLevel(logging.INFO)
        elif defaultlevel == 'WARNING':
            self.oLogger.setLevel(logging.WARNING)
        elif defaultlevel == 'ERROR':
            self.oLogger.setLevel(logging.ERROR)
        elif defaultlevel == 'CRITICAL':
            self.oLogger.setLevel(logging.CRITICAL)
        else:
            self.oLogger.setLevel(logging.INFO)

        # create logger handler object
        self.oHandler = SysLogHandler(address=(address, port))

        # create a logging format
        self.oFormatter = logging.Formatter(
            '%(asctime)s -[ %(pathname)s] - [%(levelname)s] - %(message)s')

        # assign formatter to handler
        self.oHandler.setFormatter(self.oFormatter)

        # add the handlers to the logger
        self.oLogger.addHandler(self.oHandler)

    def log(self, message, level='INFO'):
        '''
        Log message to syslog
        message: Message you like to be added
        level: Chose between INFO, WARNING, ERROR, DEBUG
        '''

        if level == 'INFO':
            self.oLogger.info(message)
        elif level == 'WARNING':
            self.oLogger.warning(message)
        elif level == 'ERROR':
            # attribute to dump traceback to logger
            self.oLogger.error(message)
        elif level == 'CRITICAL':
            # attribute to dump traceback to logger
            self.oLogger.critical(message)
        else:
            self.oLogger.info(message)
            # Get verbose stack-information


class edoClassFileLogger():
    '''
    This is a class to create a file-logger object
    logfile: Filename of the file to log to
    maxsize: The maximum size in megabytes before rotating log
    '''

    def __init__(self, logfile, maxsize, count, defaultlevel='INFO'):
        import logging
        import logging.handlers

        self.logfile = logfile
        self.maxsize = maxsize
        self.count = count
        self.oLogger = logging.getLogger(__name__)
        self.defaultlevel = defaultlevel

        if defaultlevel == 'DEBUG' or defaultlevel == 'VERBOSE':
            self.oLogger.setLevel(logging.DEBUG)
        elif defaultlevel == 'INFO':
            self.oLogger.setLevel(logging.INFO)
        elif defaultlevel == 'WARNING':
            self.oLogger.setLevel(logging.WARNING)
        elif defaultlevel == 'ERROR':
            self.oLogger.setLevel(logging.ERROR)
        elif defaultlevel == 'CRITICAL':
            self.oLogger.setLevel(logging.CRITICAL)
        else:
            self.oLogger.setLevel(logging.INFO)

        # create a logging format
        self.oFormatter = logging.Formatter(
            '%(asctime)s -[ %(name)s] - [%(levelname)s] - %(message)s')

        # create a LogRoation handler
        self.oHandler = logging.handlers.RotatingFileHandler(
            self.logfile,
            maxBytes=self.maxsize * 1000000,
            backupCount=self.count)

        # assign formatter to handler
        self.oHandler.setFormatter(self.oFormatter)

        # add the handlers to the logger
        self.oLogger.addHandler(self.oHandler)

        # add information that logger been created
        self.oLogger.info('Logging object initiated for ' + logfile)

    def log(self, message, level='INFO'):
        '''
        Log message to file
        message: Message you like to be added
        level: Chose between INFO, WARNING, ERROR, DEBUG
        '''

        if level == 'INFO':
            self.oLogger.info(message)
        elif level == 'WARNING':
            self.oLogger.warning(message)
        elif level == 'ERROR':
            # attribute to dump traceback to logger
            self.oLogger.error(message, exc_info=True)
        elif level == 'CRITICAL':
            # attribute to dump traceback to logger
            self.oLogger.critical(message, exc_info=True)
        elif level == 'DEBUG' and self.defaultlevel == 'VERBOSE':
            self.oLogger.debug(message)
            # Get verbose stack-information
            import inspect
            try:
                frame, filename, line_number, function_name, lines, index = inspect.getouterframes(inspect.currentframe())[1]
                self.oLogger.debug("Outerframe[1] " + filename + ":" + str(line_number) + " " + str(lines))
                frame, filename, line_number, function_name, lines, index = inspect.getouterframes(inspect.currentframe())[2]
                self.oLogger.debug("Outerframe[2] " + filename + ":" + str(line_number) + " " + str(lines))
                self.oLogger.debug("Outerframe[3] " + filename + ":" + str(line_number) + " " + str(lines))
                frame, filename, line_number, function_name, lines, index = inspect.getouterframes(inspect.currentframe())[4]
                self.oLogger.debug("Outerframe[4] " + filename + ":" + str(line_number) + " " + str(lines))
            except IndexError:
                self.oLogger.debug("Debug, stack index out of range")
        elif level == 'DEBUG' and self.defaultlevel == 'DEBUG':
            self.oLogger.debug(message)


class edoClassDB():
    '''
    This is a class to create database object
    dbtype: either 'sqlite' or 'mysql'
    dbconnect: Filename of the sqlite file or list for mysql ('host', 'port', 'user','password','database')
    '''

    def __init__(self, dbtype, dbconnect, loggerObject=None):
        self.dbtype = dbtype
        self.dbconnect = dbconnect
        self.oLogger = loggerObject

    def create(self, table_columns):
        '''
        Method - Creates the database defined
        Args:
            table_colums (array/tuple):
                ([table1, column1, type], [table1,column2, type])
                ([table1, column1, type],)
        '''
        if self.dbtype == 'sqlite':
            import sqlite3
            connection = sqlite3.connect(self.dbconnect)
            if self.oLogger: self.oLogger.log('Connected to sqlite ' + str(self.dbconnect), 'INFO')
            auto_keyword = 'AUTOINCREMENT'
        elif self.dbtype == 'mysql':
            import MySQLdb
            host, port, user, passwd, db = self.dbconnect
            connection = MySQLdb.connect(host=host, port=int(port), user=user, passwd=passwd, db=db)
            if self.oLogger: self.oLogger.log('Connected to mysql ' + str(self.dbconnect), 'INFO')
            auto_keyword = 'AUTO_INCREMENT'
        else:
            raise ValueError('Wrong dbtype used')

        cursor = connection.cursor()

        # Function to create table
        def createTable(name, idcolumn, tabledef):
            try:
                SQL = "CREATE TABLE " + name + \
                    "(" + idcolumn + " " + tabledef + ")"
                cursor.execute(SQL)
            except Exception as value:
                if self.oLogger: self.oLogger.log(value, 'INFO')
            finally:
                if self.oLogger: self.oLogger.log(SQL, 'DEBUG')

        # Function to create column
        def createColumn(name, columnname, columndef):
            try:
                SQL = "ALTER TABLE " + name + " ADD COLUMN " + \
                    columnname + " " + columndef

                cursor.execute(SQL)
            except Exception as value:
                if self.oLogger: self.oLogger.log(value, 'INFO')
            finally:
                if self.oLogger: self.oLogger.log(SQL, 'DEBUG')

        # Create lits of unique tables
        all_tables = set()
        for element in table_columns:
            if element[0] not in table_columns:
                all_tables.add(element[0])
        all_tables = sorted(all_tables)

        # Create all tables
        for table in all_tables:
            createTable(table, 'id', 'INTEGER PRIMARY KEY ' + auto_keyword)
            if self.oLogger: self.oLogger.log('Creating table ' + table, 'INFO')

        # Create all columns
        for table_column in table_columns:
            createColumn(table_column[0], table_column[1], table_column[2])

            # Correct encoding for column if necessary for sqlite
            if self.dbtype == 'sqlite':
                connection.create_function('FIXENCODING', 1, lambda s: str(s).decode('latin-1'))
                connection.execute("UPDATE " + table_column[0] + " SET " + table_column[1] + "=FIXENCODING(CAST(" + table_column[1] + " AS BLOB))")

        connection.close()
        if self.oLogger: self.oLogger.log('Closing database connection')

    def insert(self, table, values):
        '''
        Method - add data to column(s)
        Args:
            table: String
            values: List or Dict
        Example: object.insert('table1', ('value1',))
        Example: object.insert('table1', {col1: 'value1', col2: 'value2')
        '''
        db_error = False
        if self.dbtype == 'sqlite':
            import sqlite3
            connection = sqlite3.connect(self.dbconnect)
            if self.oLogger: self.oLogger.log('Connected to sqlite ' + str(self.dbconnect), 'INFO')
        elif self.dbtype == 'mysql':
            import MySQLdb
            host, port, user, passwd, db = self.dbconnect
            try:
                connection = MySQLdb.connect(host=host, port=int(port), user=user, passwd=passwd, db=db)
            except MySQLdb.OperationalError as e:
                print "Error connecting to database - insert"
                print e
                db_error = True
            else:
                if self.oLogger: self.oLogger.log('Connected to mysql ' + str(self.dbconnect), 'INFO')

        if not db_error is True:
            cursor = connection.cursor()

            # If the values is list
            if type(values) is list:
                # Create sql_statement
                if len(values) > 0:
                    sql_statement = "?"
                    for i in range(len(values) - 1):
                        sql_statement = sql_statement + ",?"
                    sql_statement = "INSERT INTO " + table + " VALUES (NULL, " + sql_statement + ");"
                else:
                    sys.stderr.write("Missing values for insert into SQL")

            # if the values is dict
            if type(values) is dict:
                # Iterate through the rest of values
                for i, k in enumerate(values.keys(), start=0):
                    if i == 0:
                        columns = k
                        vals = "'" + str(values[k]) + "'"
                    else:
                        columns = columns + ", " + k
                        vals = vals + ", '" + str(values[k]) + "'"
                    sql_statement = "INSERT INTO " + table + "(" + columns + ") VALUES (" + vals + ");"

            if self.oLogger: self.oLogger.log(sql_statement, 'DEBUG')
            cursor.execute(sql_statement)
            connection.commit()
            connection.close()
            if self.oLogger: self.oLogger.log('Closing database connection')

    def update(self, table, condition, values):
        '''
        Method - update column(s)
        Args:
            table: String
            condition: rowid or dict
            values: Dict
            Example: object.update('table1', {col1: 'value1'}, {col2: 'value'})
            Example: object.update('table1', 10, {col2: 'value'})
        '''
        import time

        if self.dbtype == 'sqlite':
            import sqlite3
            connection = sqlite3.connect(self.dbconnect)
            if self.oLogger: self.oLogger.log('Connected to sqlite ' + str(self.dbconnect), 'INFO')
        elif self.dbtype == 'mysql':
            import MySQLdb
            host, port, user, passwd, db = self.dbconnect

            try:
                connection = MySQLdb.connect(host=host, port=int(port), user=user, passwd=passwd, db=db)
            except:
                if self.oLogger:
                    self.oLogger.log('Could not store data to database, wating 30 sec to re-attempt ', 'ERROR')
                else:
                    print "Could not store data to database, waiting 30 sec for re-attempt"
                time.sleep(30)
                try:
                    connection = MySQLdb.connect(host=host, port=int(port), user=user, passwd=passwd, db=db)
                except:
                    if self.oLogger:
                        self.oLogger.log('Could not store data to database, skipping', 'ERROR')
                    else:
                        print "Could not store data to database, skipping"
                return "Fail"

            # Successfully connected
            if self.oLogger: self.oLogger.log('Connected to mysql ' + str(self.dbconnect), 'INFO')

        cursor = connection.cursor()

        # if the condition is dict
        if type(condition) is dict:
            # Iterate through the rest of values
            for i, k in enumerate(condition.keys(), start=0):
                if i == 0:
                    sql_where = k + "='" + str(condition[k]) + "'"
                else:
                    sql_where = sql_where + " AND " + k + "='" + str(condition[k]) + "'"
        elif type(condition) is int:
            sql_where = "id=" + str(condition)
        else:
            if self.oLogger: self.oLogger.log('Wrong condition, require rowid or dict', 'ERROR')
            raise

        # if the values is dict
        if type(values) is dict:
            # Iterate through the rest of values
            for i, k in enumerate(values.keys(), start=0):
                if i == 0:
                    sql_set = k + "='" + str(values[k]) + "'"
                else:
                    sql_set = sql_set + "," + k + "='" + str(values[k]) + "'"
        else:
            if self.oLogger: self.oLogger.log('Wrong values, require dict', 'ERROR')
            raise

        sql_condition = "UPDATE " + table + " SET " + sql_set + " WHERE " + sql_where + ";"
        if self.oLogger: self.oLogger.log(sql_condition, 'DEBUG')
        cursor.execute(sql_condition)
        connection.commit()
        connection.close()
        if self.oLogger: self.oLogger.log('Closing database connection')

    def select(self, table, condition):
        '''
        Method - select and return dict
        Args:
            table: String
            condition: dict or string
            Example: object.select('table1', {col1: 'value1', col2: 'value2'})
        '''
        if self.dbtype == 'sqlite':
            import sqlite3
            connection = sqlite3.connect(self.dbconnect)
            if self.oLogger: self.oLogger.log('Connected to sqlite ' + str(self.dbconnect), 'INFO')
        elif self.dbtype == 'mysql':
            import MySQLdb
            host, port, user, passwd, db = self.dbconnect
            try:
                connection = MySQLdb.connect(host=host, port=int(port), user=user, passwd=passwd, db=db)
            except MySQLdb.OperationalError as e:
                print "Could not access database - select"
                print e
                return None
            else:
                if self.oLogger: self.oLogger.log('Connected to mysql ' + str(self.dbconnect), 'INFO')

        cursor = connection.cursor()

        sql_where = ""
        # if the condition is dict
        if type(condition) is dict:
            # Iterate through the rest of values
            for i, k in enumerate(condition.keys(), start=0):
                if i == 0:
                    sql_where = k + "='" + str(condition[k]) + "'"
                elif i > 0:
                    sql_where = sql_where + " AND " + k + "='" + str(condition[k]) + "'"
        elif type(condition) is str:
            sql_where = condition
        else:
            if self.oLogger: self.oLogger.log('Wrong condition, require dict or string', 'ERROR')
            raise

        sql_condition = "SELECT * FROM " + table + " WHERE " + sql_where + ";"
        if self.oLogger: self.oLogger.log(sql_condition, 'DEBUG')

        cursor.execute(sql_condition)
        data = cursor.fetchall()
        connection.close()
        if self.oLogger: self.oLogger.log('Closing database connection')

        if len(data) <= 0:
            return None
        else:
            return data

    def sql(self, condition):
        '''
        Method - select and return dict
        Args:
            condition: str
            Example: object.('SELECT * FROM tabel WHERE X = Y'})
        '''

        if self.dbtype == 'sqlite':
            import sqlite3
            connection = sqlite3.connect(self.dbconnect)
            if self.oLogger: self.oLogger.log('Connected to sqlite ' + str(self.dbconnect), 'INFO')
        elif self.dbtype == 'mysql':
            import MySQLdb
            host, port, user, passwd, db = self.dbconnect
            connection = MySQLdb.connect(host=host, port=int(port), user=user, passwd=passwd, db=db)
            if self.oLogger: self.oLogger.log('Connected to mysql ' + str(self.dbconnect), 'INFO')

        cursor = connection.cursor()

        sql_condition = condition
        if self.oLogger: self.oLogger.log(sql_condition, 'DEBUG')

        cursor.execute(sql_condition)
        data = cursor.fetchall()
        connection.close()
        if self.oLogger: self.oLogger.log('Closing database connection')

        if len(data) <= 0:
            return None
        else:
            return data

    def delete(self, table, condition):
        '''
        Method - delete
        Args:
            table: String
            condition: dict or string
            Example: object.delete('table1', {col1: 'value1', col2: 'value2'})
            Example: object.delete('table1', 'col1 > 10')
        '''
        if self.dbtype == 'sqlite':
            import sqlite3
            connection = sqlite3.connect(self.dbconnect)
            if self.oLogger: self.oLogger.log('Connected to sqlite ' + str(self.dbconnect), 'INFO')
        elif self.dbtype == 'mysql':
            import MySQLdb
            host, port, user, passwd, db = self.dbconnect
            connection = MySQLdb.connect(host=host, port=int(port), user=user, passwd=passwd, db=db)
            if self.oLogger: self.oLogger.log('Connected to mysql ' + str(self.dbconnect), 'INFO')

        cursor = connection.cursor()

        sql_where = ""
        # if the condition is dict
        if type(condition) is dict:
            # Iterate through the rest of values
            for i, k in enumerate(condition.keys(), start=0):
                if i == 0:
                    sql_where = k + "='" + str(condition[k]) + "'"
                elif i > 0 and type(condition[k]) is str:
                    sql_where = sql_where + " AND " + k + "='" + str(condition[k]) + "'"
        elif type(condition) is str:
            sql_where = condition
        else:
            if self.oLogger: self.oLogger.log('Wrong condition, require dict or string', 'ERROR')
            raise

        sql_condition = "DELETE FROM " + table + " WHERE " + sql_where + ";"
        if self.oLogger: self.oLogger.log(sql_condition, 'DEBUG')

        cursor.execute(sql_condition)
        connection.commit()
        connection.close()
        if self.oLogger: self.oLogger.log('Closing database connection')

    def sync(self, dstDB, srcTable, sync_col, *srcCols):
        '''
        Method - sync to another database
        Args:
            dstDB: object
            srcTable: name of source table
            sync_col: name of table that will either be 'null' or DateTime
            srcCols: array of colums to sync
            Example: object.sync(objTargetDB, 'table', 'sync_col', 'col1', 'col2', 'col3')
        '''

        ID_COL = 'id'

        if self.dbtype == 'sqlite':
            import sqlite3
            connection = sqlite3.connect(self.dbconnect)
            if self.oLogger: self.oLogger.log('Connected to sqlite ' + str(self.dbconnect), 'INFO')
        elif self.dbtype == 'mysql':
            import MySQLdb
            host, port, user, passwd, db = self.dbconnect
            connection = MySQLdb.connect(host=host, port=int(port), user=user, passwd=passwd, db=db)
            if self.oLogger: self.oLogger.log('Connected to mysql ' + str(self.dbconnect), 'INFO')

        cursor = connection.cursor()

        all_cols = ','.join(srcCols)
        sql_where = sync_col + " LIKE '%null%'"
        sql_condition = "SELECT " + ID_COL + "," + all_cols + " FROM " + srcTable + " WHERE " + sql_where + ";"
        if self.oLogger: self.oLogger.log(sql_condition, 'DEBUG')

        cursor.execute(sql_condition)
        data = cursor.fetchall()
        connection.close()
        if self.oLogger: self.oLogger.log('Closing database connection')

        targetData = {}
        row_no = 1

        # Iterate through rows
        for row in data:
            if self.oLogger: self.oLogger.log('Syncing Row ' + str(row_no) + '/' + str(len(data)), 'INFO')
            # Get the ID of the row in source database to update sync column
            # Convert tuple to list to remove element
            row = list(row)
            row_id = row.pop(0)
            i = 0
            # iterate columns to create record
            for col in srcCols:
                targetData[col] = row[i]
                i = i + 1
            # Creating record in the sync database
            targetData[sync_col] = edoGetDateTime()
            dstDB.insert(srcTable, targetData)
            row_no = row_no + 1
            # Update source database sync column
            targetData = {}
            targetData[sync_col] = edoGetDateTime()
            self.update(srcTable, row_id, targetData)


class edoClassConfig():
    ''' Class to manager config-files, return True if found '''

    def __init__(self, configfile, loggerObject=None):
        import ConfigParser

        self.configfile = configfile
        self.oLogger = loggerObject
        self.config = ConfigParser.RawConfigParser()

        try:
            self.oConfigFile = open(self.configfile, 'r')
        except IOError as e:
            if self.oLogger: self.oLogger.log('Could not load config file ' + configfile, 'INFO')
            if self.oLogger: self.oLogger.log(e, 'INFO')
            try:
                self.oConfigFile = open(self.configfile, 'w')
                self.config.write(self.oConfigFile)
            except ValueError as e:
                if self.oLogger: self.oLogger('Could not load/create config file, ' + e, 'ERROR')
                raise
        else:
            self.config.readfp(self.oConfigFile)

    def AddUpdate(self, section, parameters):
        '''
        Args:
            section: the name of the section
            parameters: dict
        '''

        # Check that there are no section yet
        if not self.config.has_section(section):
            if self.oLogger: self.oLogger.log('Creating section ' + section, 'INFO')
            self.config.add_section(section)

        # iterate through options in dict
        if type(parameters) is dict:
            # Iterate through the rest of values
            for k in parameters.keys():
                if not self.config.has_option(section, parameters[k]):
                    if self.oLogger: self.oLogger.log('Adding or updating ' + section +
                                                      ' with value ' + k + '=' + parameters[k], 'INFO')
                    self.config.set(section, k, parameters[k])
            self.oConfigFile = open(self.configfile, 'w')
            self.config.write(self.oConfigFile)
        else:
            if self.oLogger: self.oLogger.log('The parameters has to be a dict', 'ERROR')
            raise

    def getAll(self, section):
        '''
        Args:
            section: the name of the secion
        Return: dict with all parameters
        '''

        # Check that there are no section yet
        if self.config.has_section(section):
            return dict(self.config.items(section))
        else:
            if self.oLogger: self.oLogger.log('Could not read parameters from ' + section, 'INFO')
            return None

    def get(self, section, parameter):
        '''
        Args:
            section: the name of the secion and parameter
        Return: string
        '''

        # Check that there are no section yet
        if self.config.has_section(section):
            return str(self.config.get(section, parameter))
        else:
            if self.oLogger: self.oLogger.log('Could not read parameters from ' + section, 'INFO')
            return None

    def sections(self):
        ''' Get all sections '''
        return self.config.sections()


class edoExpect():
    ''' Expect class '''

    def __init__(self, cmd, timeout=30, loggerObject=None):
        import pexpect

        self.cmd = cmd
        self.timeout = timeout
        self.oLogger = loggerObject

        if type(cmd) is not list:
            if self.oLogger: self.oLogger.log('Spawn command: ' + cmd, 'DEBUG')
            self.child = pexpect.spawn(cmd, timeout=self.timeout)
        elif type(cmd) is list:
            if self.oLogger: self.oLogger.log('Spawn command: ' + str(cmd[0]) + " args=" + str(cmd[1]), 'DEBUG')
            self.child = pexpect.spawn(cmd[0], args=cmd[1], timeout=self.timeout)

    def kill(self, returnCode):
        if self.oLogger: self.oLogger.log('Expect killing thread', 'DEBUG')
        self.child.kill(returnCode)

    def log(self, file):
        import sys

        if file == 'stdout':
            self.child.logfile = sys.stdout
        else:
            f = open(file, 'w')
            self.child.logfile = f
            if self.oLogger: self.oLogger.log('Expect output to: ' + file, 'INFO')

    def expect(self, response):
        ''' Usage: result = oExp.expect(['.+\[\d+\]>', pexpect.TIMEOUT, pexpect.EOF]) '''
        result = self.child.expect(response), self.child.before, self.child.after
        if self.oLogger:
            self.oLogger.log('Expecting: ' + str(response), 'DEBUG')
            self.oLogger.log('Received: ' + str(result[0]), 'DEBUG')
        return result

    def send(self, cmd):
        if self.oLogger: self.oLogger.log('Sendline: ' + cmd, 'DEBUG')
        self.child.send(cmd)

    def sendline(self, cmd):
        if self.oLogger: self.oLogger.log('Sendline: ' + cmd, 'DEBUG')
        self.child.sendline(cmd)

    def isalive(self):
        return self.child.isalive()


def edoTestSocket(host, port, loggerObject=None):
    ''' Function to test host:port for connection and return 0 or 1 '''
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.shutdown(2)
        if loggerObject:
            loggerObject.log('Connection success, socket ' + host + ':' + str(port), 'INFO')
        return 0
    except:
        if loggerObject:
            loggerObject.log('Connection faile socket ' + host + ':' + str(port), 'INFO')
        return 1


class edoProcess():
    '''
    Class to start a subprocess
    example: command = edoProcess("/bin/sh", "-c", "while true; do omxplayer " + self.song + " ; done")
    '''
    def __init__(self, *args):
        import subprocess
        self.commands = args
        self.process = subprocess.Popen(tuple(args), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.pid = self.process.pid
        self.stdout = self.process.stdout
        self.stderr = self.process.stderr

    def kill(self):
        import subprocess
        get_gpid = subprocess.Popen(['/bin/sh', '-c', 'ps x -o  "%p %r" | egrep "\s*' + str(self.pid) + '"'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        gpid = str(get_gpid.stdout.read().split()[1])
        # print("gpid: " + gpid)
        kill_cmd = subprocess.Popen(['pkill', '-g', gpid], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print kill_cmd.stdout.read()
        # print kill_cmd.stderr.read()


class edoLcd(threading.Thread):
    '''
    Class object to display text on lcd-display
    lcd = edoLcd(sleep_time=0.5)
    '''
    def __init__(self, loggerObject=None, **kwargs):
        threading.Thread.__init__(self)
        import Queue
        self.counter = 0
        self.objLog = loggerObject
        self.queue = Queue.Queue()
        if 'default' in kwargs:
            self.default = kwargs['default']
        else:
            self.default = None

        self.running = False
        if 'sleep_time' in kwargs:
            self.sleep_time = kwargs['sleep_time']
        else:
            self.sleep_time = 0.5

    def text(self, argString, argTime, argLight=True):
        ''' Add text to display to queue '''
        self.queue.put([argString, argTime, argLight])

    def run(self):
        # import pcd8544.lcd as lcd
        import time
        import os
        import pcd8544.lcd as lcd

        if not os.geteuid() == 0:
            if self.objLog:
                self.objLog.log('edoLcd - has to be run as root', 'CRITICAL')
            else:
                print('edoLcd - has to be run as root')
            return 1

        ON, OFF = [1, 0]
        lcd.init()
        lcd.cls()
        lcd.text('')
        if self.default is not None:
            lcd.text(self.default)

        self.running = True
        while self.running is True:
            if self.queue.qsize() > 0:
                # Get next text and time
                lcdText, lcdTime, lcdLight = self.queue.get()
                try:
                    # lcd.init()
                    lcd.cls()
                    if lcdLight:
                        lcd.backlight(ON)
                    else:
                        lcd.backlight(OFF)
                    # Handle linebreak
                    if lcdText.find('\n'):
                        tmp = lcdText.split('\n')
                        line_no = 0
                        for line in tmp:
                            lcd.gotorc(line_no, 0)
                            lcd.text(line)
                            line_no += 1
                    else:
                        lcd.text(lcdText)
                    # Wait
                    time.sleep(lcdTime)
                    # Increase counter
                    self.counter += 1
                finally:
                    lcd.cls()
                    if self.queue.qsize() == 0:
                        lcd.backlight(OFF)
                        if self.default is not None:
                            # Handle linebreak
                            if self.default.find('\n'):
                                tmp = self.default.split('\n')
                                line_no = 0
                                for line in tmp:
                                    lcd.gotorc(line_no, 0)
                                    lcd.text(line)
                                    line_no += 1
                            else:
                                lcd.text(self.default)
            # Pause for next poll
            time.sleep(self.sleep_time)
            # Reset LCD
            '''
            if self.counter > 10:
                lcd.spi.close()
                time.sleep(1)
                lcd.init()
                lcd.cls()
                lcd.text('')
                if self.default is not None:
                    lcd.text(self.default)
                self.counter = 0
                print "RESET LCD"
            '''

    def change_default(self, argString):
        ''' Change and update default '''
        import pcd8544.lcd as lcd
        self.default = argString
        lcd.cls()
        lcd.text(self.default)

    def blink(self, times=3):
        ''' Blink - period in seconds '''
        for i in range(times):
            self.queue.put(['', self.sleep_time, True])
            self.queue.put(['', self.sleep_time, False])

    def blank(self):
        ''' Empty queue '''
        while self.queue.qsize() > 0:
            lcdText, lcdTime, lcdLight = self.queue.get()

    def stop(self):
        import pcd8544.lcd as lcd
        self.running = False
        lcd.cls()


class edoPirMotion(threading.Thread):
    '''
    Class object to handle pir motion sensor
    object = edoPirMotion(pin=4, check_int=0.5, logObject)
    '''
    def __init__(self, loggerObject=None, **kwargs):
        threading.Thread.__init__(self)
        import Queue
        import RPi.GPIO as io

        self.objLog = loggerObject
        self.queue = Queue.Queue()
        self.running = False
        self.motion = False

        if 'pin' in kwargs:
            self.pin = kwargs['pin']
        else:
            self.pin = 4
        if 'check_int' in kwargs:
            self.check_int = kwargs['check_int']
        else:
            self.check_int = 0.5

        io.setmode(io.BCM)
        io.setup(self.pin, io.IN)

    def run(self):
        import time
        import os
        import RPi.GPIO as io

        if not os.geteuid() == 0:
            if self.objLog:
                self.objLog.log('edoPirMotion - has to be run as root', 'CRITICAL')
            else:
                print('edoPirMotion - has to be run as root')
            return 1

        self.running = True
        while self.running:
            # Get pir alarm
            if io.input(self.pin) and self.motion is not True:
                if self.objLog:
                    self.objLog.log('edoPirMotion - Motion Detected', 'INFO')
                else:
                    print('edoPirMotion - Motion Detected')
                self.motion = True
                epoch = int(time.time())
                self.queue.put(epoch)
            elif not io.input(self.pin) and self.motion is True:
                self.motion = False
            # Pause for next poll
            time.sleep(self.check_int)

    def stop(self):
        self.running = False

    def get(self, past_seconds=0):
        ''' Get the motions within the past seconds '''
        import time
        import Queue
        self.all_motions = []
        while True:
            try:
                motion_time = self.queue.get(block=False)
            except Queue.Empty:
                break
            else:
                now = time.time()
                if past_seconds > 0:
                    if motion_time >= now - past_seconds:
                        self.all_motions.append(motion_time)
                else:
                    self.all_motions.append(motion_time)
        return self.all_motions


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
        else:
            self.pin = 17
        if 'check_int' in kwargs:
            self.check_int = kwargs['check_int']
        else:
            self.check_int = 0.5

        io.setmode(io.BCM)
        # Activate input with PullUp
        io.setup(self.pin, io.IN, pull_up_down=io.PUD_UP)

    def run(self):
        import time
        import os
        import RPi.GPIO as io

        if not os.geteuid() == 0:
            if self.objLog:
                self.objLog.log('edoSwitch - has to be run as root', 'CRITICAL')
            else:
                print('edoSwitch - has to be run as root')
            return 1

        self.running = True
        # Get initial status and supply to queue
        if io.input(self.pin):
            self.status = "Open"
        else:
            self.status = "Close"
        epoch = int(time.time())
        self.queue.put((epoch, self.status))

        while self.running:
            # Get current door status
            if io.input(self.pin) and self.status == "Close":
                if self.objLog:
                    self.objLog.log('edoSwitch - Open', 'INFO')
                else:
                    print('edoSwitch - Open')
                self.status = "Open"
                epoch = int(time.time())
                self.queue.put((epoch, self.status))
            elif not io.input(self.pin) and self.status == "Open":
                if self.objLog:
                    self.objLog.log('edoSwitch - Close', 'INFO')
                else:
                    print('edoSwitch - Close')
                self.status = "Close"
                epoch = int(time.time())
                self.queue.put((epoch, self.status))
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


class edoDHT(threading.Thread):
    '''
    Class object to read temp or humid from DHT_11 sensor
    object = edoDHT_humid(pin=4, limit=1, check_int=10, type=0(humid)/1(temp), logObject)
    '''
    def __init__(self, loggerObject=None, **kwargs):
        threading.Thread.__init__(self)
        import Queue
        import Adafruit_DHT

        self.objLog = loggerObject
        self.queue = Queue.Queue()
        self.running = False
        self.value = 0
        self.type = kwargs.get('type', 1)
        self.limit = float(kwargs.get('limit', 0.5))
        self.verify_times = 3
        self.sensor = kwargs.get('sensor', Adafruit_DHT.DHT11)

        if 'pin' in kwargs:
            self.pin = kwargs['pin']
        else:
            self.pin = 4
        if 'check_int' in kwargs:
            self.check_int = kwargs['check_int']
        else:
            self.check_int = 10

    def run(self):
        import Adafruit_DHT
        import time
        import os

        if not os.geteuid() == 0:
            if self.objLog:
                self.objLog.log('edoDHT - has to be run as root', 'CRITICAL')
            else:
                print('edoDHT - has to be run as root')
            return 1

        def changed(old, new, limit):
            if new > old + limit:
                return True
            elif new < old - limit:
                return True
            else:
                return False

        self.running = True
        # Get initial status and supply to queue
        self.value = Adafruit_DHT.read_retry(self.sensor, self.pin)[self.type]

        epoch = int(time.time())
        self.queue.put((epoch, self.value))

        while self.running:
            # Get new value
            new_value = Adafruit_DHT.read_retry(self.sensor, self.pin)[self.type]

            # Read and ignore miss-readings
            verified = [changed(self.value, Adafruit_DHT.read_retry(self.sensor, self.pin)[self.type], self.limit) for i in range(1, self.verify_times)]

            # print "debug: type %s ((%s > %s + %s) or (%s < %s - %s)) and (%s)" % (self.type, new_value, self.value, self.limit, new_value, self.value, self.limit, verified)
            if ((new_value > self.value + self.limit) or (new_value < self.value - self.limit)) and all(verified):
                if self.objLog:
                    self.objLog.log('DHT Type %s exceeds limit of %s, new value %s' % (self.type, self.limit, new_value))
                else:
                    print 'DHT Type %s exceeds limit of %s, new value %s' % (self.type, self.limit, new_value)
                self.value = new_value
                epoch = int(time.time())
                self.queue.put((epoch, self.value))
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


def readadc(adcnum, clockpin=18, mosipin=24, misopin=23, cspin=25):
    # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # set up the SPI interface pins
    GPIO.setup(mosipin, GPIO.OUT)
    GPIO.setup(misopin, GPIO.IN)
    GPIO.setup(clockpin, GPIO.OUT)
    GPIO.setup(cspin, GPIO.OUT)

    if ((adcnum > 7) or (adcnum < 0)):
            return -1
    GPIO.output(cspin, True)

    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)     # bring CS low

    commandout = adcnum
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3    # we only need to send 5 bits here
    for i in range(5):
            if (commandout & 0x80):
                    GPIO.output(mosipin, True)
            else:
                    GPIO.output(mosipin, False)
            commandout <<= 1
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)

    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)
            adcout <<= 1
            if (GPIO.input(misopin)):
                    adcout |= 0x1

    GPIO.output(cspin, True)

    adcout >>= 1       # first bit is 'null' so drop it
    return adcout


class edoMCPvalue(threading.Thread):
    '''
    Class object to read MCP3008
    object = edoMCPvalue(minref, adc_in, **kwargs)
    object = edoMCPvalue(510, 0, clockpin=18, mosipin=24, misopin=23, cspin=25, check_int=1, sleep_int=0.000001, check_times=100, loggerObject=loggerObject)
    '''
    def __init__(self, minref=510, adc_in=0, **kwargs):
        threading.Thread.__init__(self)
        import Queue
        import RPi.GPIO as io

        self.minref = minref
        self.adc_in = adc_in
        self.clockpin = kwargs.get('clockpin', 18)
        self.mosipin = kwargs.get('mosipin', 24)
        self.misopin = kwargs.get('misopin', 23)
        self.cspin = kwargs.get('cspin', 25)
        self.check_int = kwargs.get('check_int', 1)
        self.sleep_int = kwargs.get('sleep_int', 0.000001)
        self.check_times = kwargs.get('check_times', 100)
        self.loggerObject = kwargs.get('loggerObject', None)
        self.objLog = kwargs.get('loggerObject', None)
        self.queue = Queue.Queue()
        self.running = False
        self.status = None

        io.setmode(io.BCM)
        io.setwarnings(False)

    def poll_value(self, minref=0, adc_in=0, debug=False, sleep_int=0.000001, max_retry=10):
        ''' Poll value '''
        import time
        count = 0
        retry = 0
        result = 0
        peak = 0
        while retry < max_retry:
            for x in range(0, self.check_times):
                value_in = readadc(self.adc_in, self.clockpin, self.mosipin, self.misopin, self.cspin)
                if value_in > minref and value_in <= 1023 and value_in > 0:
                    count += 1
                    result += value_in - minref
                    if value_in > peak:
                        peak = value_in
                time.sleep(self.sleep_int)
            if count > 0:
                try:
                    # avg_val = int(round(float(result) / float(count) / minref * 100))
                    avg_val = int(round(float(result) / float(count) / (1023 - minref) * 100))
                    max_val = int(round(float(peak - minref) / (1023 - minref) * 100))
                except Exception:
                    avg_val = 0
                    max_val = 0
                count_val = count
                if debug is True:
                    print 'MIN_REF: %s, AVG: (%s/%s)/1023=%s%%, MAX: (%s-%s)/1023=%s%%, COUNT: %s' % (minref, result, count, avg_val, peak, minref, max_val, count_val)
                # Return value
                return avg_val, max_val, count
            else:
                time.sleep(self.check_int)
                result = 0
                peak = 0
                count = 0
                retry += 1
                # Restart next attempt


class edoPowerMeter(edoMCPvalue):
    '''
    Class object to Non-Intrusive Current Meter through MCP3008
    object = edoPowerMeter(minref, adc_in, **kwargs)
    object = edoPowerMeter(510, 0, clockpin=18, mosipin=24, misopin=23, cspin=25, check_int=1, sleep_int=0.000001, loggerObject=loggerObject)
    '''
    def __init__(self, minref, adc_in, **kwargs):
        import Queue
        edoMCPvalue.__init__(self)
        self.minref = minref
        self.adc_in = adc_in
        self.clockpin = kwargs.get('clockpin', 18)
        self.mosipin = kwargs.get('mosipin', 24)
        self.misopin = kwargs.get('misopin', 23)
        self.cspin = kwargs.get('cspin', 25)
        self.check_int = kwargs.get('check_int', 1)
        self.sleep_int = kwargs.get('sleep_int', 0.000001)
        self.objLog = kwargs.get('loggerObject', None)
        self.limit = kwargs.get('limit', 5)
        self.debug = kwargs.get('debug', False)
        self.queue = Queue.Queue()
        self.running = False
        self.avg_val = 0
        self.max_val = 0
        self.count = 0
        self.verify_times = 3

    def run(self):
        import time
        import os

        def changed(old, new, limit):
            if old + limit > 100:
                if new < old - limit: return True
            if old - limit < 0:
                if new > old + limit: return True
            if new > old + limit or new < old - limit:
                return True
            else:
                return False

        device_type = 'edoPowerMeter'
        if not os.geteuid() == 0:
            if self.objLog:
                self.objLog.log('%s - has to be run as root' % device_type, 'CRITICAL')
            else:
                print('%s - has to be run as root' % device_type)
            return 1

        self.running = True
        # Get initial status and supply to queue
        self.avg_val, self.max_val, self.count = self.poll_value(self.minref, self.adc_in, debug=self.debug, sleep_int=0.000001, max_retry=10)
        epoch = int(time.time())
        self.queue.put((epoch, self.avg_val))

        while self.running:
            '''
            # For Average
            current_power = self.poll_value(self.minref, self.adc_in, debug=self.debug, sleep_int=0.000001, max_retry=10)[0]
            if changed(self.avg_val, current_power, self.limit):
                self.avg_val = current_power
                if self.objLog:
                    self.objLog.log('edoPowerMeter: ' + str(self.avg_val), 'INFO')
                else:
                    print('edoPowerMeter: ' + str(self.avg_val))
                epoch = int(time.time())
                self.queue.put((epoch, self.avg_val))
            '''
            # For Max
            current_power = self.poll_value(self.minref, self.adc_in, debug=self.debug, sleep_int=0.000001, max_retry=10)[1]

            # Returns a list of True/False based on verify_times used to
            # determine false switch
            verified = [changed(self.max_val, self.poll_value(self.minref, self.adc_in, debug=self.debug, sleep_int=0.000001, max_retry=10)[1], self.limit) for i in range(1, self.verify_times)]

            if changed(self.max_val, current_power, self.limit) and all(verified):
                self.max_val = current_power
                if self.objLog:
                    self.objLog.log('edoPowerMeter: ' + str(self.max_val), 'INFO')
                else:
                    print('edoPowerMeter: ' + str(self.max_val))
                epoch = int(time.time())
                self.queue.put((epoch, self.max_val))

    def stop(self):
        self.running = False

    def reset(self):
        ''' Reset current status to force update to Queue '''
        self.avg_val = 0
        self.max_val = 0
        self.count = 0

    def get(self, past_seconds=0):
        ''' Get the power changes within the past seconds '''
        import time
        import Queue
        self.all_status = []
        while True:
            try:
                power_status = self.queue.get(block=False)
            except Queue.Empty:
                break
            else:
                now = time.time()
                if past_seconds > 0:
                    if power_status[0] >= now - past_seconds:
                        self.all_status.append(power_status)
                else:
                    self.all_status.append(power_status)
        return self.all_status


class edoADCmeter(edoMCPvalue):
    '''
    Class object to Messure percantage through MCP3008
    object = edoADCmeter(adc_in, **kwargs)
    object = edoADCmeter(0, clockpin=18, mosipin=24, misopin=23, cspin=25, check_int=1, sleep_int=0.000001, pause_int=1, loggerObject=loggerObject)
    '''
    def __init__(self, adc_in=0, **kwargs):
        import Queue
        edoMCPvalue.__init__(self)
        self.minref = 0
        self.adc_in = adc_in
        self.clockpin = kwargs.get('clockpin', 18)
        self.mosipin = kwargs.get('mosipin', 24)
        self.misopin = kwargs.get('misopin', 23)
        self.cspin = kwargs.get('cspin', 25)
        self.check_int = kwargs.get('check_int', 1)
        self.sleep_int = kwargs.get('sleep_int', 1)
        self.objLog = kwargs.get('loggerObject', None)
        self.limit = kwargs.get('limit', 5)
        self.check_times = kwargs.get('check_times', 1)
        self.pause_int = kwargs.get('pause_int', 1)
        self.debug = kwargs.get('debug', False)
        self.queue = Queue.Queue()
        self.running = False
        self.avg_val = 0
        self.max_val = 0
        self.count = 0
        self.verify_times = 1

    def run(self):
        import time
        import os

        def changed(old, new, limit):
            if old + limit > 100:
                if new < old - limit: return True
            if old - limit < 0:
                if new > old + limit: return True
            if new > old + limit or new < old - limit:
                return True
            else:
                return False

        device_type = 'edoADCpercantage'
        if not os.geteuid() == 0:
            if self.objLog:
                self.objLog.log('%s - has to be run as root' % device_type, 'CRITICAL')
            else:
                print('%s - has to be run as root' % device_type)
            return 1

        self.running = True
        # Get initial status and supply to queue
        self.avg_val, self.max_val, self.count = self.poll_value(self.minref, self.adc_in, debug=self.debug, sleep_int=1, max_retry=1)
        epoch = int(time.time())
        self.queue.put((epoch, self.avg_val))

        while self.running:
            # For Average
            current_value = self.poll_value(self.minref, self.adc_in, debug=self.debug, sleep_int=1, max_retry=1)[0]
            if changed(self.avg_val, current_value, self.limit):
                self.avg_val = current_value
                if self.objLog:
                    self.objLog.log('edoValueMeter: ' + str(self.avg_val), 'INFO')
                else:
                    print('edoValueMeter: ' + str(self.avg_val))
                epoch = int(time.time())
                self.queue.put((epoch, self.avg_val))
            # Pause the time
            time.sleep(self.pause_int)

    def stop(self):
        self.running = False

    def reset(self):
        ''' Reset current status to force update to Queue '''
        self.avg_val = 0
        self.max_val = 0
        self.count = 0

    def get(self, past_seconds=0):
        ''' Get the ADC changes within the past seconds '''
        import time
        import Queue
        self.all_status = []
        while True:
            try:
                value_status = self.queue.get(block=False)
            except Queue.Empty:
                break
            else:
                now = time.time()
                if past_seconds > 0:
                    if value_status[0] >= now - past_seconds:
                        self.all_status.append(value_status)
                else:
                    self.all_status.append(value_status)
        return self.all_status


def edoEpochToDate(argEpoch):
    ''' Function to convert epoch to DateTime '''
    import time
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(argEpoch)))


def edoGetLocalIP():
    ''' Returns local IP-address '''
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com", 80))
        ip = s.getsockname()[0]
    except ValueError:
        ip = None
    return ip


class edoButton(threading.Thread):
    '''
    Class object to handle button
    object = edoButton(3, {1: [function1,args], 2: [function2,args]}, pin=22, check_int=0.1, logObject)
    '''
    def __init__(self, timeout=1, functions=None, loggerObject=None, **kwargs):
        threading.Thread.__init__(self)
        import RPi.GPIO as io

        self.objLog = loggerObject
        self.running = False
        self.status = None
        self.timeout = timeout
        self.count = 0
        self.timer = 0
        self.functions = functions

        if 'pin' in kwargs:
            self.pin = kwargs['pin']
        else:
            self.pin = 22
        if 'check_int' in kwargs:
            self.check_int = kwargs['check_int']
        else:
            self.check_int = 0.01

        io.setmode(io.BCM)
        # Activate input with PullUp
        io.setup(self.pin, io.IN, pull_up_down=io.PUD_UP)

    def run(self):
        import time
        import os
        import RPi.GPIO as io

        if not os.geteuid() == 0:
            if self.objLog:
                self.objLog.log('edoButton - has to be run as root', 'CRITICAL')
            else:
                print('edoButton - has to be run as root')
            return 1

        self.running = True

        while self.running:
            # Get current door status
            # GPIO.add_event_detect(22, GPIO.RISING, callback=printFunction, bouncetime=300)
            if not io.input(self.pin):
                io.wait_for_edge(self.pin, io.RISING)
                self.count += 1
                while self.timer < self.timeout and self.running:
                    time.sleep(self.check_int)
                    self.timer += self.check_int
                    if not io.input(self.pin):
                        io.wait_for_edge(self.pin, io.RISING)
                        self.count += 1
                        self.timer = 0
            if self.timer > self.timeout:
                # Check what to do, if one click e.g {1: function1}
                print "Button pressed " + str(self.count) + " times"
                if self.functions is not None:
                    if self.count in self.functions.keys():
                        # Get func and args from dict
                        func, args = self.functions[self.count]
                        # Run function and depack args
                        func(*args)
                self.count = 0
                self.timer = 0
            # Pause for next poll
            time.sleep(self.check_int)

    def stop(self):
        self.running = False


class edoLed(threading.Thread):
    '''
    Class object to blink led in background
    object = edoLed(pin=25, check_int=0.1, logObject)
    '''
    def __init__(self, blink_type=None, loggerObject=None, **kwargs):
        threading.Thread.__init__(self)
        import RPi.GPIO as io

        self.objLog = loggerObject
        self.running = False
        self.status = None
        self.blink_type = blink_type
        self.kwargs = kwargs

        if 'on' in kwargs:
            self.on = kwargs['on']
        else:
            self.on = 1

        if 'off' in kwargs:
            self.off = kwargs['off']
        else:
            self.off = 1

        if 'pin' in kwargs:
            self.pin = kwargs['pin']
        else:
            self.pin = 25
        if 'check_int' in kwargs:
            self.check_int = kwargs['check_int']
        else:
            self.check_int = 0.1

        self.off_time = 1
        self.on_time = 1

        # Disable warnings
        io.setwarnings(False)
        io.setmode(io.BCM)
        io.setup(self.pin, io.OUT)
        io.output(self.pin, io.HIGH)

    def run(self):
        import time
        import os
        import RPi.GPIO as io

        if not os.geteuid() == 0:
            if self.objLog:
                self.objLog.log('edoLed - has to be run as root', 'CRITICAL')
            else:
                print('edoLed - has to be run as root')
            return 1

        self.running = True

        while self.running:
            # Get current sort of led
            if self.blink_type == 'blink':
                if self.status == 'on':
                    io.output(self.pin, io.HIGH)
                    self.status = 'off'
                    time.sleep(self.off_time)
                if self.status == 'off':
                    io.output(self.pin, io.LOW)
                    self.status = 'on'
                    time.sleep(self.on_time)
            if self.blink_type == 'on':
                io.output(self.pin, io.LOW)
                self.status = 'on'
            if self.blink_type == 'off':
                io.output(self.pin, io.HIGH)
                self.status = 'off'

            # Wait for next check
            time.sleep(self.check_int)
        # Stop led
        io.output(self.pin, io.HIGH)

    def blink(self, on=1, off=1):
        ''' Start blinking '''
        self.blink_type = 'blink'
        self.on_time = on
        self.off_time = off

    def led_on(self, period=0):
        ''' Turn on for a period '''
        import time
        self.blink_type = 'on'
        if period > 0:
            time.sleep(period)
            self.status = 'off'

    def led_off(self):
        ''' Turn off led '''
        self.blink_type = 'off'

    def stop(self):
        self.blink_type = 'off'
        self.running = False


class edoBuzzer(threading.Thread):
    '''
    Class object to make noise with piezo speaker
    object = edoBuzzer(pin=27, check_int=0.1, logObject)
    '''
    def __init__(self, buzz_type=None, loggerObject=None, **kwargs):
        threading.Thread.__init__(self)
        import RPi.GPIO as io

        self.objLog = loggerObject
        self.running = False
        self.status = None
        self.buzz_type = buzz_type
        self.kwargs = kwargs

        if 'pin' in kwargs:
            self.pin = kwargs['pin']
        else:
            self.pin = 27
        if 'check_int' in kwargs:
            self.check_int = kwargs['check_int']
        else:
            self.check_int = 0.1

        io.setwarnings(False)
        io.setmode(io.BCM)
        io.setup(self.pin, io.OUT)

    def run(self):
        import time
        import os
        import RPi.GPIO as io

        if not os.geteuid() == 0:
            if self.objLog:
                self.objLog.log('edoBuzzer - has to be run as root', 'CRITICAL')
            else:
                print('edoBuzzer - has to be run as root')
            return 1

        self.running = True

        while self.running:
            # Get current sort of buzz
            if self.buzz_type == 'on':
                io.output(self.pin, io.HIGH)
                self.status = 'on'
            if self.buzz_type == 'off':
                io.output(self.pin, io.LOW)
                self.status = 'off'
            if self.buzz_type == 'sos':
                io.output(self.pin, io.HIGH)
                time.sleep(0.5)
                io.output(self.pin, io.LOW)
                time.sleep(0.5)
                io.output(self.pin, io.HIGH)
                time.sleep(0.5)
                io.output(self.pin, io.LOW)
                time.sleep(0.5)
                io.output(self.pin, io.HIGH)
                time.sleep(0.5)
                io.output(self.pin, io.LOW)
                time.sleep(0.5)
                io.output(self.pin, io.HIGH)
                time.sleep(1)
                io.output(self.pin, io.LOW)
                time.sleep(0.5)
                io.output(self.pin, io.HIGH)
                time.sleep(1)
                io.output(self.pin, io.LOW)
                time.sleep(0.5)
                io.output(self.pin, io.HIGH)
                time.sleep(1)
                io.output(self.pin, io.LOW)
                time.sleep(0.5)
                io.output(self.pin, io.HIGH)
                time.sleep(1)
                io.output(self.pin, io.LOW)
                time.sleep(0.5)
                io.output(self.pin, io.HIGH)
                time.sleep(0.5)
                io.output(self.pin, io.LOW)
                time.sleep(0.5)
                io.output(self.pin, io.HIGH)
                time.sleep(0.5)
                io.output(self.pin, io.LOW)
                time.sleep(0.5)
                io.output(self.pin, io.HIGH)
                time.sleep(0.5)
                io.output(self.pin, io.LOW)
                time.sleep(0.5)
                self.buzz_type = 'off'
            # Wait for next check
            time.sleep(self.check_int)
        # Complete turn off buzzer
        io.output(self.pin, io.LOW)

    def buzz_on(self, period=0):
        ''' Turn on for a period '''
        import time
        self.buzz_type = 'on'
        if period > 0:
            time.sleep(period)
            self.buzz_type = 'off'

    def buzz_off(self):
        ''' Turn off  '''
        self.buzz_type = 'off'

    def buzz_sos(self):
        ''' Play SOS '''
        self.buzz_type = 'sos'

    def stop(self):
        self.running = False


def funcSendGMail(argServer, argPort, argUser, argPass, argTo, argFrom, argSubject, argBody, **kwargs):
    ''' Function to send a mail with attachments through gmail '''

    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
    from email.MIMEImage import MIMEImage
    from email.mime.application import MIMEApplication
    import smtplib
    import re
    import os

    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = argSubject
    msgRoot['From'] = argFrom
    msgRoot['To'] = argTo
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    msgText = MIMEText('Your mail-client doesnt support HTML')
    msgAlternative.attach(msgText)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    varBodyText = argBody

    # Create list of images
    if 'Files' in kwargs.keys():
        argFiles = kwargs['Files']
        listImages = [x for x in argFiles if re.match(".+\.(jpg|jpeg|png)$", x, re.IGNORECASE)]
        listNonImages = [x for x in argFiles if not re.match(".+\.(jpg|jpeg|png)$", x, re.IGNORECASE)]

        for i, varImage in enumerate(listImages, start=1):
            varBodyText = varBodyText + '<img src="cid:image' + str(i) + '"><br>'

        msgText = MIMEText(varBodyText, 'html')
        msgAlternative.attach(msgText)

        # Attach Images
        for i, varImage in enumerate(listImages, start=1):
            fp = open(varImage, 'rb')
            msgImage = MIMEImage(fp.read())
            fp.close()
            # Define the image's ID as referenced above
            msgImage.add_header('Content-ID', '<image' + str(i) + '>')
            msgRoot.attach(msgImage)

        # Attach other files
        for i, varFile in enumerate(listNonImages, start=1):
            fp = open(varFile, 'rb')
            msgAttach = MIMEApplication(fp.read())
            fp.close()
            msgAttach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(varFile))
            msgRoot.attach(msgAttach)

    msgText = MIMEText(varBodyText, 'html')
    msgAlternative.attach(msgText)

    gmailUser = argUser
    gmailPassword = argPass

    if argServer is None: argServer = "smtp.gmail.com"
    if argPort is None: argPort = 587

    mailServer = smtplib.SMTP(argServer, argPort)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmailUser, gmailPassword)
    mailServer.sendmail(gmailUser, argTo, msgRoot.as_string())
    mailServer.close()


class edoGmail():
    '''
    Class object to queue and send gmail
    '''
    def __init__(self, argUser, argPass, argFrom=None, argServer=None, argPort=None, loggerObject=None):
        self.objLog = loggerObject
        self.running = False
        self.user = argUser
        self.password = argPass
        if argFrom is None: argFrom = argUser
        self.mail_from = argFrom
        if argServer is None: argServer = "smtp.gmail.com"
        if argPort is None: argPort = 587
        self.server = argServer
        self.port = argPort

    def send(*func_arg):
        import threading
        t = threading.Thread(target=edoGmail.worker, args=func_arg)
        t.start()

    def worker(self, argTo, argSubject, argBody, argFiles=None):
        from email.MIMEMultipart import MIMEMultipart
        from email.MIMEText import MIMEText
        from email.MIMEImage import MIMEImage
        from email.mime.application import MIMEApplication
        import smtplib
        import re
        import os

        # Create the root message and fill in the from, to, and subject headers
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = argSubject
        msgRoot['From'] = self.mail_from
        msgRoot['To'] = argTo
        msgRoot.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)

        msgText = MIMEText('Your mail-client doesnt support HTML')
        msgAlternative.attach(msgText)

        # We reference the image in the IMG SRC attribute by the ID we give it below
        varBodyText = argBody

        # Create list of images
        if argFiles is not None:
            listImages = [x for x in argFiles if re.match(".+\.(jpg|jpeg|png)$", x, re.IGNORECASE)]
            listNonImages = [x for x in argFiles if not re.match(".+\.(jpg|jpeg|png)$", x, re.IGNORECASE)]

            for i, varImage in enumerate(listImages, start=1):
                varBodyText = varBodyText + '<img src="cid:image' + str(i) + '"><br>'

            msgText = MIMEText(varBodyText, 'html')
            msgAlternative.attach(msgText)

            # Attach Images
            for i, varImage in enumerate(listImages, start=1):
                fp = open(varImage, 'rb')
                msgImage = MIMEImage(fp.read())
                fp.close()
                # Define the image's ID as referenced above
                msgImage.add_header('Content-ID', '<image' + str(i) + '>')
                msgRoot.attach(msgImage)

            # Attach other files
            for i, varFile in enumerate(listNonImages, start=1):
                fp = open(varFile, 'rb')
                msgAttach = MIMEApplication(fp.read())
                fp.close()
                msgAttach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(varFile))
                msgRoot.attach(msgAttach)

        msgText = MIMEText(varBodyText, 'html')
        msgAlternative.attach(msgText)

        gmailUser = self.user
        gmailPassword = self.password

        mailServer = smtplib.SMTP(self.server, self.port)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(gmailUser, gmailPassword)
        mailServer.sendmail(gmailUser, argTo, msgRoot.as_string())
        mailServer.close()


class edoFTP(threading.Thread):
    ''' Class for using FTP '''
    def __init__(self, ftpServer, ftpUser, ftpPass, loggerObject=None, **kwargs):
        threading.Thread.__init__(self)
        import Queue
        self.queue = Queue.Queue()
        self.objLog = loggerObject
        self.running = False
        self.server = ftpServer
        self.user = ftpUser
        self.ftpPass = ftpPass
        self.loggerObject = loggerObject
        self.status = None

        if not 'port' in kwargs:
            self.port = 21
        else:
            self.port = kwargs['port']

    def chdir(self, ftp_path, ftp_conn):
        ''' function to iterate through dirs using ftplib '''
        def check_dir(dir, ftp_conn):
            ''' Assure all dirs exists '''
            filelist = []
            ftp_conn.retrlines('LIST', filelist.append)
            found = False
            for f in filelist:
                if f.split()[-1] == dir and f.lower().startswith('d'):
                    found = True
            if not found:
                ftp_conn.mkd(dir)
            ftp_conn.cwd(dir)
        dirs = [d for d in ftp_path.split('/') if d != '']
        for p in dirs:
            check_dir(p, ftp_conn)

    def run(self):
        import ftplib
        import os
        import time
        self.running = True

        while self.running:
            if self.queue.qsize() > 0:
                self.status = "transfer"
                command, nextFileList, nextFileDir = self.queue.get()
                # Initiate FTP object
                self.ftp = ftplib.FTP()
                try:
                    self.ftp.connect(self.server, self.port)
                    self.ftp.login(self.user, self.ftpPass)
                    if command == 'upload':
                        for ftpFile in nextFileList:
                            if nextFileDir is not None: self.chdir(nextFileDir, self.ftp)
                            file = open(ftpFile, 'rb')
                            self.ftp.storbinary('STOR ' + os.path.basename(ftpFile), file)
                            file.close()
                    if command == 'download':
                        for ftpFile in nextFileList:
                            if nextFileDir is not None: self.chdir(nextFileDir, self.ftp)
                            if nextFileDir is not None:
                                self.ftp.retrbinary("RETR " + ftpFile, open(os.path.dirname(nextFileDir) + "/" + os.path.basename(ftpFile), 'wb').write)
                            else:
                                self.ftp.retrbinary("RETR " + ftpFile, open(os.path.basename(ftpFile), 'wb').write)
                    if self.objLog:
                        self.objLog.log("FTP command: " + command + ", Files: " + str(nextFileList), 'INFO')
                    else:
                        print("FTP command: " + command + ", Files: " + str(nextFileList))
                    self.ftp.quit()
                except ValueError:
                    self.objLog.log("FTP fail " + str(ValueError), "ERROR")
                time.sleep(3)
            self.status = None

    def upload(self, fileList, fileDir=None):
        ''' Add files for upload to queue '''
        self.queue.put(['upload', fileList, fileDir])

    def download(self, fileList, fileDir=None):
        ''' Add files for download to queue '''
        self.queue.put(['download', fileList, fileDir])

    def dir(self, ftpDir='.'):
        ''' List directory '''
        import ftplib
        self.ftp = ftplib.FTP()
        self.ftp.connect(self.server, self.port)
        self.ftp.login(self.user, self.ftpPass)
        dirList = self.ftp.dir(ftpDir)
        self.ftp.quit()
        return dirList

    def stop(self):
        self.running = False


def edoPiCamera(filename, res=None):
    import picamera
    import time
    with picamera.PiCamera() as camera:
        if res is not None: camera.resolution = (800, 600)
        camera.start_preview()
        # Camera warm-up time
        time.sleep(2)
        camera.capture(filename)
        camera.stop_preview()


class Luxmeter:
    i2c = None

    def __init__(self, address=0x39, debug=0, pause=0.8):
        from Adafruit_I2C import Adafruit_I2C
        self.i2c = Adafruit_I2C(address)
        self.address = address
        self.pause = pause
        self.debug = debug
        self.gain = 0  # no gain preselected
        self.i2c.write8(0x80, 0x03)     # enable the device

    def setGain(self, gain=1):
        """ Set the gain """
        import time
        if (gain != self.gain):
            if (gain == 1):
                self.i2c.write8(0x81, 0x02)
                if (self.debug):
                    print "Setting low gain"
            else:
                self.i2c.write8(0x81, 0x12)
                if (self.debug):
                    print "Setting high gain"
            self.gain = gain
            # set gain = 1X and timing
            # set gain = 16X and timing
            # safe gain for calculation
            time.sleep(self.pause)

    def readWord(self, reg):
        """Reads a word from the I2C device"""
        try:
            wordval = self.i2c.readU16(reg)
            newval = self.i2c.reverseByteOrder(wordval)
            if (self.debug):
                print("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address, wordval & 0xFFFF, reg))
            return newval
        except IOError:
            print("Error accessing 0x%02X: Check your I2C address" % self.address)
            return -1

    def readFull(self, reg=0x8C):
        """Reads visible+IR diode from the I2C device"""
        return self.readWord(reg)

    def readIR(self, reg=0x8E):
        """Reads IR only diode from the I2C device"""
        return self.readWord(reg)

    def getLux(self, gain=1):
        """Grabs a lux reading either with autoranging (gain=0) or with a specified gain (1, 16)"""
        if (gain == 1 or gain == 16):
            self.setGain(gain)  # low/highGain
            ambient = self.readFull()
            IR = self.readIR()
        elif (gain == 0):  # auto gain
            self.setGain(16)  # first try highGain
            ambient = self.readFull()
            if (ambient < 65535):
                IR = self.readIR()

        if (ambient >= 65535 or IR >= 65535):  # value(s) exeed(s) data
            self.setGain(1)  # set lowGain
            ambient = self.readFull()
            IR = self.readIR()

        if (self.gain == 1):
            ambient *= 16    # scale 1x to 16x
            IR *= 16         # scale 1x to 16x

        try:
            ratio = (IR / float(ambient))  # changed to make it run under python
        except ZeroDivisionError:
            ratio = 0

        if (self.debug):
                print "IR Result", IR
                print "Ambient Result", ambient
        if ((ratio >= 0) & (ratio <= 0.52)):
            lux = (0.0315 * ambient) - (0.0593 * ambient * (ratio ** 1.4))
        elif (ratio <= 0.65):
            lux = (0.0229 * ambient) - (0.0291 * IR)
        elif (ratio <= 0.80):
            lux = (0.0157 * ambient) - (0.018 * IR)
        elif (ratio <= 1.3):
            lux = (0.00338 * ambient) - (0.0026 * IR)
        elif (ratio > 1.3):
            lux = 0
        return lux


class edoLuxMeter(threading.Thread):
    '''
    Class object to read lux from a TSL2561
    object = edoLuxMeter(limit=1, check_int=10, logObject)
    '''
    def __init__(self, loggerObject=None, **kwargs):
        threading.Thread.__init__(self)
        import Queue

        self.objLog = loggerObject
        self.queue = Queue.Queue()
        self.running = False
        self.value = 0
        self.limit = kwargs.get('limit', 5)

        if 'check_int' in kwargs:
            self.check_int = kwargs['check_int']
        else:
            self.check_int = 10

        self.luxmeter = Luxmeter()

    def run(self):
        import time
        import os

        if not os.geteuid() == 0:
            if self.objLog:
                self.objLog.log('edoLux - has to be run as root', 'CRITICAL')
            else:
                print('edoLux - has to be run as root')
            return 1

        self.running = True
        # Get initial status and supply to queue
        self.value = int(self.luxmeter.getLux())
        if self.value > 50:
            self.value = 50

        epoch = int(time.time())
        self.queue.put((epoch, self.value))

        while self.running:
            # Get new value
            new_value = int(self.luxmeter.getLux())
            if new_value > 50:
                new_value = 50
            if (new_value > self.value + self.limit) or (new_value < self.value - self.limit):
                if self.objLog:
                    self.objLog.log('Luxmeter exceeds limit of %s, new value %s' % (self.limit, new_value))
                else:
                    print 'Luxmeter exceeds limit of %s, new value %s' % (self.limit, new_value)
                self.value = new_value
                epoch = int(time.time())
                self.queue.put((epoch, self.value))
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


class edoModemDongle(threading.Thread):
    '''
    Class object to handle 3G Dongle
    object = edoModemDongle(logObject, tty='/dev/ttyUSB0')
    object = edoModemDongle(incoming_cmd={'search_for_word_in_sms': 'function_or_external_script_with_rest_as_args'})
    '''
    def __init__(self, loggerObject=None, **kwargs):
        threading.Thread.__init__(self)
        import Queue
        import sms
        import ast
        import time

        self.objLog = loggerObject
        self.queue = Queue.Queue()
        self.running = False
        self.status = None
        # self.tty = kwargs.get('tty', '/dev/tty.HUAWEIMobile-Modem')
        self.tty = kwargs.get('tty', '/dev/ttyUSB0')
        self.check_int = int(kwargs.get('check_int', 10))
        self.incoming_cmd = kwargs.get('incoming_cmd', {})
        self.functions = kwargs.get('functions', None)

        # Change string to dict if required
        if type(self.incoming_cmd) is str:
            self.incoming_cmd = ast.literal_eval(self.incoming_cmd)

        # Initiate modem
        self.m = sms.Modem(self.tty)
        # Change SMS mode
        self.m._command('AT+CMGF=1')

        # Initiate memcache if it exists
        try:
            import memcache
        except:
            print "Please install memcache to support reading status"
        else:
            self.shared = memcache.Client(['127.0.0.1:11211'], debug=1)

    def run(self):
        import time
        import re
        import subprocess
        from datetime import datetime
        import _strptime
        self.running = True

        # Bugfix
        datetime.strptime('2012-01-01', '%Y-%m-%d')

        while self.running:
            # Check if memcache exists and with sms in queue
            if 'shared' in dir(self):
                sms_memcache = self.shared.get('sms')
                if sms_memcache:
                    number, message = sms_memcache
                    if self.objLog:
                        print "Found sms in memcache queue for %s with body %s" % (number, message[:30])
                    self.send(number, message)
                    self.shared.set('sms', None)

            # Check if any new incoming SMS
            msgs = self.m.messages()
            if len(msgs) > 0:
                for sms in msgs:
                    if self.objLog:
                        self.objLog.log('Incoming SMS from %s with body: %s' % (sms.number, sms.text), 'INFO')
                    else:
                        print 'Incoming SMS from %s with body: %s' % (sms.number, sms.text)
                    # Handle incoming sms
                    if self.objLog:
                        self.objLog.log("Checking incoming SMS against rules %s" % (str(self.incoming_cmd),), 'INFO')
                    print "Checking incoming SMS against rules %s" % (str(self.incoming_cmd),)
                    for key in self.incoming_cmd.keys():
                        cmd = self.incoming_cmd[key]
                        if re.search("^%s\s*(.*)" % (key,), sms.text):
                            args = re.search("^%s\s*(.*)" % (key,), sms.text).groups()[0]
                            if self.objLog:
                                self.objLog.log('Found string "%s" in SMS' % (key,), 'INFO')
                            print 'Found string "%s" in SMS' % (key,)
                            # Check if function
                            cmd_func = cmd
                            if cmd_func in self.functions.keys():
                                print "Found %s in list of passed functions" % (cmd_func,)
                                cmd_func = self.functions[cmd_func]
                            if callable(cmd_func):
                                print "Command is existing function, calling %s with args: %s" % (cmd, args)
                                args = args.split(",")
                                # Might add arguments in the future
                                result = cmd_func()
                                if self.objLog:
                                    self.objLog.log('Sending message to %s with body: %s' % (sms.number, str(result)), 'INFO')
                                else:
                                    print 'Sending SMS to %s with body: %s' % (sms.number, str(result)[:50])
                                self.send(sms.number, str(result))
                            else:
                                print "No function, trying to call external script %s" % (cmd,)
                                try:
                                    result = subprocess.Popen('%s' % (cmd,), stdout=subprocess.PIPE).stdout.read()
                                    self.send(sms.number, str(result).encode('ascii', 'replace')[:160])
                                except:
                                    print "Could not find function nor external script - skip"
                    if self.objLog:
                        self.objLog.log('Deleting message', 'INFO')
                    else:
                        print 'Deleting message'
                    sms.delete()

            # Send any messages in queue
            if self.queue.qsize() > 0:
                number, message = self.queue.get()
                # self.m.send(number, message)
                if self.objLog:
                    self.objLog.log('Sending message to %s with message: %s' % (number, str(message)[:160]), 'INFO')
                self.m.send(number, str(message)[:160])
                if len(message) > 160:
                    if self.objLog:
                        self.objLog.log('Sending parial message 160-320 to %s: %s' % (number, str(message)[160:][:160]), 'INFO')
                    time.sleep(10)
                    self.m.send(number, str(message)[160:][:160])
                    if len(message) > 320:
                        if self.objLog:
                            self.objLog.log('Sending parial message 320-480 to %s: %s' % (number, str(message)[320:][:160]), 'INFO')
                        time.sleep(10)
                        self.m.send(number, str(message)[320:][:160])

            # Pause for next poll
            time.sleep(self.check_int)

    def stop(self):
        self.running = False

    def send(self, number, message):
        ''' Add sms message to send '''
        self.queue.put((number, message))


class edoDongleTCPRequestHandler(SocketServer.BaseRequestHandler):
    ''' BaseRequestHandler uses TCPserver and does the actual work '''
    def handle(self):
        import json

        data = self.request.recv(1024)

        # Check if json
        try:
            data = json.loads(data)
        except Exception:
            pass
        else:
            self.server.dongle.send(data)
            print(edoGetDateTime() + ": Sending SMS - " + str(data))

        response = "ok"
        self.request.sendall(response)


class edoDongleTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, dongleObject):
        ''' Extend init to handle Dongle object '''
        self.dongle = dongleObject
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)
