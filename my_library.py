#!/usr/bin/env python2.7

# my_library.py - This Module is for the most used classes and methods
# URL: https://github.com/engdan77/otis_service
# Author: Daniel Engvall (daniel@engvalls.eu)

__version__ = "$Revision: 20190123.1251 $"

import SocketServer
import sys
import threading
import smbus
import time


def get_datetime():
    import time
    return time.strftime("%Y-%m-%d %H:%M:%S")


def log_stderr(message, level='ERROR', log_object=None):
    """ This is a function to log to stderr if log_object is missing (not used) """
    if log_object is None and (level == 'ERROR' or level == 'CRITICAL'):
        sys.stderr.write(str(message) + "\n")
    else:
        log_object.log(message, level)


class ClassSyslogLogger:
    """
    This is a class to create a syslog-logger object
    address: ip or address to syslog server
    port: default port udp 514
    """

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
        """
        Log message to syslog
        message: Message you like to be added
        level: Chose between INFO, WARNING, ERROR, DEBUG
        """

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


class ClassFileLogger:
    """
    This is a class to create a file-logger object
    logfile: Filename of the file to log to
    maxsize: The maximum size in megabytes before rotating log
    """

    def __init__(self, logfile, maxsize, count, defaultlevel='INFO'):
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
        """
        Log message to file
        message: Message you like to be added
        level: Chose between INFO, WARNING, ERROR, DEBUG
        """

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
                # noinspection PyPep8
                frame, filename, line_number, function_name, lines, index = \
                inspect.getouterframes(inspect.currentframe())[1]
                self.oLogger.debug("Outerframe[1] " + filename + ":" + str(line_number) + " " + str(lines))
                # noinspection PyPep8
                frame, filename, line_number, function_name, lines, index = \
                inspect.getouterframes(inspect.currentframe())[2]
                self.oLogger.debug("Outerframe[2] " + filename + ":" + str(line_number) + " " + str(lines))
                self.oLogger.debug("Outerframe[3] " + filename + ":" + str(line_number) + " " + str(lines))
                # noinspection PyPep8
                frame, filename, line_number, function_name, lines, index = \
                inspect.getouterframes(inspect.currentframe())[4]
                self.oLogger.debug("Outerframe[4] " + filename + ":" + str(line_number) + " " + str(lines))
            except IndexError:
                self.oLogger.debug("Debug, stack index out of range")
        elif level == 'DEBUG' and self.defaultlevel == 'DEBUG':
            self.oLogger.debug(message)


# noinspection Annotator,Annotator,Annotator,Annotator,PyUnresolvedReferences
class ClassDB:
    """
    This is a class to create database object
    dbtype: either 'sqlite' or 'mysql'
    dbconnect: Filename of the sqlite file or list for mysql ('host', 'port', 'user','password','database')
    """

    def __init__(self, dbtype, dbconnect, logger_object=None):
        self.dbtype = dbtype
        self.dbconnect = dbconnect
        self.oLogger = logger_object

    def create(self, table_columns):
        """
        Method - Creates the database defined
        Args:
            table_colums (array/tuple):
                ([table1, column1, type], [table1,column2, type])
                ([table1, column1, type],)
                :param table_columns:
        """
        if self.dbtype == 'sqlite':
            import sqlite3
            connection = sqlite3.connect(self.dbconnect)
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Connected to sqlite ' + str(self.dbconnect), 'INFO')
            auto_keyword = 'AUTOINCREMENT'
        elif self.dbtype == 'mysql':
            import MySQLdb
            host, port, user, passwd, db = self.dbconnect
            # noinspection PyPep8
            connection = MySQLdb.connect(host=host, port=int(port), user=user, passwd=passwd, db=db,
                                         connection_timeout=120, buffered=True)
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Connected to mysql ' + str(self.dbconnect), 'INFO')
            auto_keyword = 'AUTO_INCREMENT'
        else:
            raise ValueError('Wrong dbtype used')

        cursor = connection.cursor()

        # Function to create table
        def create_table(name, idcolumn, tabledef):
            try:
                sql = "CREATE TABLE " + name + \
                      "(" + idcolumn + " " + tabledef + ")"
                cursor.execute(sql)
            except Exception as value:
                # noinspection PyPep8
                if self.oLogger: self.oLogger.log(value, 'INFO')
            finally:
                # noinspection PyPep8
                if self.oLogger: self.oLogger.log(sql, 'DEBUG')

        # Function to create column
        def create_column(name, columnname, columndef):
            try:
                sql = "ALTER TABLE " + name + " ADD COLUMN " + \
                      columnname + " " + columndef

                cursor.execute(sql)
            except Exception as value:
                # noinspection PyPep8
                if self.oLogger: self.oLogger.log(value, 'INFO')
            finally:
                # noinspection PyPep8
                if self.oLogger: self.oLogger.log(sql, 'DEBUG')

        # Create lits of unique tables
        all_tables = set()
        for element in table_columns:
            if element[0] not in table_columns:
                all_tables.add(element[0])
        all_tables = sorted(all_tables)

        # Create all tables
        for table in all_tables:
            create_table(table, 'id', 'INTEGER PRIMARY KEY ' + auto_keyword)
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Creating table ' + table, 'INFO')

        # Create all columns
        for table_column in table_columns:
            create_column(table_column[0], table_column[1], table_column[2])

            # Correct encoding for column if necessary for sqlite
            if self.dbtype == 'sqlite':
                connection.create_function('FIXENCODING', 1, lambda s: str(s).decode('latin-1'))
                # noinspection PyPep8
                connection.execute(
                    "UPDATE " + table_column[0] + " SET " + table_column[1] + "=FIXENCODING(CAST(" + table_column[
                        1] + " AS BLOB))")

        connection.close()
        # noinspection PyPep8
        if self.oLogger: self.oLogger.log('Closing database connection')

    def insert(self, table, values):
        """
        Method - add data to column(s)
        Args:
            table: String
            values: List or Dict
        Example: object.insert('table1', ('value1',))
        Example: object.insert('table1', {col1: 'value1', col2: 'value2')
        """
        db_error = False
        if self.dbtype == 'sqlite':
            import sqlite3
            connection = sqlite3.connect(self.dbconnect)
            # noinspection PyPep8
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
                # noinspection PyPep8
                if self.oLogger: self.oLogger.log('Connected to mysql ' + str(self.dbconnect), 'INFO')

        # noinspection PyPep8
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

            # noinspection PyPep8
            if self.oLogger: self.oLogger.log(sql_statement, 'DEBUG')
            cursor.execute(sql_statement)
            connection.commit()
            connection.close()
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Closing database connection')

    def update(self, table, condition, values):
        """
        Method - update column(s)
        Args:
            table: String
            condition: rowid or dict
            values: Dict
            Example: object.update('table1', {col1: 'value1'}, {col2: 'value'})
            Example: object.update('table1', 10, {col2: 'value'})
        """
        import time

        if self.dbtype == 'sqlite':
            import sqlite3
            connection = sqlite3.connect(self.dbconnect)
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Connected to sqlite ' + str(self.dbconnect), 'INFO')
        elif self.dbtype == 'mysql':
            import MySQLdb
            host, port, user, passwd, db = self.dbconnect

            # noinspection PyPep8
            try:
                connection = MySQLdb.connect(host=host, port=int(port), user=user, passwd=passwd, db=db)
            except:
                if self.oLogger:
                    self.oLogger.log('Could not store data to database, wating 30 sec to re-attempt ', 'ERROR')
                else:
                    print "Could not store data to database, waiting 30 sec for re-attempt"
                time.sleep(30)
                # noinspection PyPep8
                try:
                    connection = MySQLdb.connect(host=host, port=int(port), user=user, passwd=passwd, db=db)
                except:
                    if self.oLogger:
                        self.oLogger.log('Could not store data to database, skipping', 'ERROR')
                    else:
                        print "Could not store data to database, skipping"
                return "Fail"

            # Successfully connected
            # noinspection PyPep8
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
            # noinspection PyPep8
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
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Wrong values, require dict', 'ERROR')
            raise

        sql_condition = "UPDATE " + table + " SET " + sql_set + " WHERE " + sql_where + ";"
        # noinspection PyPep8
        if self.oLogger: self.oLogger.log(sql_condition, 'DEBUG')
        cursor.execute(sql_condition)
        connection.commit()
        connection.close()
        # noinspection PyPep8
        if self.oLogger: self.oLogger.log('Closing database connection')

    def select(self, table, condition):
        """
        Method - select and return dict
        Args:
            table: String
            condition: dict or string
            Example: object.select('table1', {col1: 'value1', col2: 'value2'})
        """
        if self.dbtype == 'sqlite':
            import sqlite3
            connection = sqlite3.connect(self.dbconnect)
            # noinspection PyPep8
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
                # noinspection PyPep8
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
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Wrong condition, require dict or string', 'ERROR')
            raise

        sql_condition = "SELECT * FROM " + table + " WHERE " + sql_where + ";"
        # noinspection PyPep8
        if self.oLogger: self.oLogger.log(sql_condition, 'DEBUG')

        cursor.execute(sql_condition)
        data = cursor.fetchall()
        connection.close()
        # noinspection PyPep8
        if self.oLogger: self.oLogger.log('Closing database connection')

        if len(data) <= 0:
            return None
        else:
            return data

    def sql(self, condition):
        """
        Method - select and return dict
        Args:
            condition: str
            Example: object.('SELECT * FROM tabel WHERE X = Y'})
        """

        if self.dbtype == 'sqlite':
            import sqlite3
            connection = sqlite3.connect(self.dbconnect)
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Connected to sqlite ' + str(self.dbconnect), 'INFO')
        elif self.dbtype == 'mysql':
            import MySQLdb
            host, port, user, passwd, db = self.dbconnect
            connection = MySQLdb.connect(host=host, port=int(port), user=user, passwd=passwd, db=db)
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Connected to mysql ' + str(self.dbconnect), 'INFO')

        cursor = connection.cursor()

        sql_condition = condition
        # noinspection PyPep8
        if self.oLogger: self.oLogger.log(sql_condition, 'DEBUG')

        cursor.execute(sql_condition)
        data = cursor.fetchall()
        connection.close()
        # noinspection PyPep8
        if self.oLogger: self.oLogger.log('Closing database connection')

        if len(data) <= 0:
            return None
        else:
            return data

    def delete(self, table, condition):
        """
        Method - delete
        Args:
            table: String
            condition: dict or string
            Example: object.delete('table1', {col1: 'value1', col2: 'value2'})
            Example: object.delete('table1', 'col1 > 10')
        """
        if self.dbtype == 'sqlite':
            import sqlite3
            connection = sqlite3.connect(self.dbconnect)
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Connected to sqlite ' + str(self.dbconnect), 'INFO')
        elif self.dbtype == 'mysql':
            import MySQLdb
            host, port, user, passwd, db = self.dbconnect
            connection = MySQLdb.connect(host=host, port=int(port), user=user, passwd=passwd, db=db)
            # noinspection PyPep8
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
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Wrong condition, require dict or string', 'ERROR')
            raise

        sql_condition = "DELETE FROM " + table + " WHERE " + sql_where + ";"
        # noinspection PyPep8
        if self.oLogger: self.oLogger.log(sql_condition, 'DEBUG')

        cursor.execute(sql_condition)
        connection.commit()
        connection.close()
        # noinspection PyPep8
        if self.oLogger: self.oLogger.log('Closing database connection')

    def sync(self, dst_db, src_table, sync_col, *src_cols):
        """
        Method - sync to another database
        Args:
            dst_db: object
            src_table: name of source table
            sync_col: name of table that will either be 'null' or DateTime
            src_cols: array of colums to sync
            Example: object.sync(objTargetDB, 'table', 'sync_col', 'col1', 'col2', 'col3')
        """

        id_col = 'id'

        if self.dbtype == 'sqlite':
            import sqlite3
            connection = sqlite3.connect(self.dbconnect)
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Connected to sqlite ' + str(self.dbconnect), 'INFO')
        elif self.dbtype == 'mysql':
            import MySQLdb
            host, port, user, passwd, db = self.dbconnect
            connection = MySQLdb.connect(host=host, port=int(port), user=user, passwd=passwd, db=db)
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Connected to mysql ' + str(self.dbconnect), 'INFO')

        cursor = connection.cursor()

        all_cols = ','.join(src_cols)
        sql_where = sync_col + " LIKE '%null%'"
        sql_condition = "SELECT " + id_col + "," + all_cols + " FROM " + src_table + " WHERE " + sql_where + ";"
        # noinspection PyPep8
        if self.oLogger: self.oLogger.log(sql_condition, 'DEBUG')

        cursor.execute(sql_condition)
        data = cursor.fetchall()
        connection.close()
        # noinspection PyPep8
        if self.oLogger: self.oLogger.log('Closing database connection')

        target_data = {}
        row_no = 1

        # Iterate through rows
        for row in data:
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Syncing Row ' + str(row_no) + '/' + str(len(data)), 'INFO')
            # Get the ID of the row in source database to update sync column
            # Convert tuple to list to remove element
            row = list(row)
            row_id = row.pop(0)
            i = 0
            # iterate columns to create record
            for col in src_cols:
                target_data[col] = row[i]
                i = i + 1
            # Creating record in the sync database
            target_data[sync_col] = get_datetime()
            dst_db.insert(src_table, target_data)
            row_no = row_no + 1
            # Update source database sync column
            target_data = {sync_col: get_datetime()}
            self.update(src_table, row_id, target_data)


# noinspection Annotator
class ClassConfig:
    """ Class to manager config-files, return True if found """

    def __init__(self, configfile, logger_object=None):
        import ConfigParser

        self.configfile = configfile
        self.oLogger = logger_object
        self.config = ConfigParser.RawConfigParser()

        try:
            self.oConfigFile = open(self.configfile, 'r')
        except IOError as e:
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Could not load config file ' + configfile, 'INFO')
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log(e, 'INFO')
            try:
                self.oConfigFile = open(self.configfile, 'w')
                self.config.write(self.oConfigFile)
            except ValueError as e:
                # noinspection PyPep8
                if self.oLogger: self.oLogger('Could not load/create config file, ' + e, 'ERROR')
                raise
        else:
            self.config.readfp(self.oConfigFile)

    def add_update(self, section, parameters):
        """
        Args:
            section: the name of the section
            parameters: dict
        """

        # Check that there are no section yet
        if not self.config.has_section(section):
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Creating section ' + section, 'INFO')
            self.config.add_section(section)

        # iterate through options in dict
        if type(parameters) is dict:
            # Iterate through the rest of values
            for k in parameters.keys():
                if not self.config.has_option(section, parameters[k]):
                    # noinspection PyPep8
                    if self.oLogger: self.oLogger.log('Adding or updating ' + section +
                                                      ' with value ' + k + '=' + parameters[k], 'INFO')
                    self.config.set(section, k, parameters[k])
            self.oConfigFile = open(self.configfile, 'w')
            self.config.write(self.oConfigFile)
        else:
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('The parameters has to be a dict', 'ERROR')
            raise

    def get_all(self, section):
        """
        Args:
            section: the name of the secion
        Return: dict with all parameters
        """

        # Check that there are no section yet
        if self.config.has_section(section):
            return dict(self.config.items(section))
        else:
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Could not read parameters from ' + section, 'INFO')
            return None

    def get(self, section, parameter):
        """
        Args:
            section: the name of the secion and parameter
        Return: string
        :param parameter:
        """

        # Check that there are no section yet
        if self.config.has_section(section):
            return str(self.config.get(section, parameter))
        else:
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Could not read parameters from ' + section, 'INFO')
            return None

    def sections(self):
        """ Get all sections """
        return self.config.sections()


class MyExpect:
    """ Expect class """

    def __init__(self, cmd, timeout=30, logger_object=None):
        import pexpect

        self.cmd = cmd
        self.timeout = timeout
        self.oLogger = logger_object

        if type(cmd) is not list:
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Spawn command: ' + cmd, 'DEBUG')
            self.child = pexpect.spawn(cmd, timeout=self.timeout)
        elif type(cmd) is list:
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Spawn command: ' + str(cmd[0]) + " args=" + str(cmd[1]), 'DEBUG')
            self.child = pexpect.spawn(cmd[0], args=cmd[1], timeout=self.timeout)

    def kill(self, return_code):
        # noinspection PyPep8
        if self.oLogger: self.oLogger.log('Expect killing thread', 'DEBUG')
        self.child.kill(return_code)

    def log(self, file):
        import sys

        if file == 'stdout':
            self.child.logfile = sys.stdout
        else:
            f = open(file, 'w')
            self.child.logfile = f
            # noinspection PyPep8
            if self.oLogger: self.oLogger.log('Expect output to: ' + file, 'INFO')

    def expect(self, response):
        """ Usage: result = oExp.expect(['.+\[\d+\]>', pexpect.TIMEOUT, pexpect.EOF]) """
        result = self.child.expect(response), self.child.before, self.child.after
        if self.oLogger:
            self.oLogger.log('Expecting: ' + str(response), 'DEBUG')
            self.oLogger.log('Received: ' + str(result[0]), 'DEBUG')
        return result

    def send(self, cmd):
        # noinspection PyPep8
        if self.oLogger: self.oLogger.log('Sendline: ' + cmd, 'DEBUG')
        self.child.send(cmd)

    def sendline(self, cmd):
        # noinspection PyPep8
        if self.oLogger: self.oLogger.log('Sendline: ' + cmd, 'DEBUG')
        self.child.sendline(cmd)

    def isalive(self):
        return self.child.isalive()


def test_socket(host, port, logger_object=None):
    """ Function to test host:port for connection and return 0 or 1 """
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # noinspection PyPep8
    try:
        s.connect((host, port))
        s.shutdown(2)
        if logger_object:
            logger_object.log('Connection success, socket ' + host + ':' + str(port), 'INFO')
        return 0
    except:
        if logger_object:
            logger_object.log('Connection faile socket ' + host + ':' + str(port), 'INFO')
        return 1


class Process:
    """
    Class to start a subprocess
    example: command = Process("/bin/sh", "-c", "while true; do omxplayer " + self.song + " ; done")
    """

    def __init__(self, *args):
        import subprocess
        self.commands = args
        # noinspection PyPep8
        self.process = subprocess.Popen(tuple(args), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        self.pid = self.process.pid
        self.stdout = self.process.stdout
        self.stderr = self.process.stderr

    def kill(self):
        import subprocess
        # noinspection PyPep8
        get_gpid = subprocess.Popen(['/bin/sh', '-c', 'ps x -o  "%p %r" | egrep "\s*' + str(self.pid) + '"'],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        gpid = str(get_gpid.stdout.read().split()[1])
        # print("gpid: " + gpid)
        # noinspection PyPep8
        kill_cmd = subprocess.Popen(['pkill', '-g', gpid], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        print kill_cmd.stdout.read()
        # print kill_cmd.stderr.read()


class Lcd(threading.Thread):
    """
    Class object to display text on lcd-display
    lcd = Lcd(sleep_time=0.5)
    """

    def __init__(self, logger_object=None, **kwargs):
        threading.Thread.__init__(self)
        import Queue
        self.counter = 0
        self.objLog = logger_object
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

    def text(self, arg_string, arg_time, arg_light=True):
        """ Add text to display to queue """
        self.queue.put([arg_string, arg_time, arg_light])

    def run(self):
        # import pcd8544.lcd as lcd
        import time
        import os
        import pcd8544.lcd as lcd

        if not os.geteuid() == 0:
            if self.objLog:
                self.objLog.log('Lcd - has to be run as root', 'CRITICAL')
            else:
                print('Lcd - has to be run as root')
            return 1

        on, off = [1, 0]
        lcd.init()
        lcd.cls()
        lcd.text('')
        if self.default is not None:
            lcd.text(self.default)

        self.running = True
        while self.running is True:
            if self.queue.qsize() > 0:
                # Get next text and time
                lcd_text, lcd_time, lcd_light = self.queue.get()
                try:
                    # lcd.init()
                    lcd.cls()
                    if lcd_light:
                        lcd.backlight(on)
                    else:
                        lcd.backlight(off)
                    # Handle linebreak
                    if lcd_text.find('\n'):
                        tmp = lcd_text.split('\n')
                        line_no = 0
                        for line in tmp:
                            lcd.gotorc(line_no, 0)
                            lcd.text(line)
                            line_no += 1
                    else:
                        lcd.text(lcd_text)
                    # Wait
                    time.sleep(lcd_time)
                    # Increase counter
                    self.counter += 1
                finally:
                    lcd.cls()
                    if self.queue.qsize() == 0:
                        lcd.backlight(off)
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

    def change_default(self, arg_string):
        """ Change and update default """
        import pcd8544.lcd as lcd
        self.default = arg_string
        lcd.cls()
        lcd.text(self.default)

    def blink(self, times=3):
        """ Blink - period in seconds """
        for i in range(times):
            self.queue.put(['', self.sleep_time, True])
            self.queue.put(['', self.sleep_time, False])

    def blank(self):
        """ Empty queue """
        while self.queue.qsize() > 0:
            lcd_text, lcd_time, lcd_light = self.queue.get()

    def stop(self):
        import pcd8544.lcd as lcd
        self.running = False
        lcd.cls()


class PirMotion(threading.Thread):
    """
    Class object to handle pir motion sensor
    object = PirMotion(pin=4, check_int=0.5, log_object)
    """

    def __init__(self, logger_object=None, **kwargs):
        threading.Thread.__init__(self)
        self.all_motions = []
        import Queue
        import RPi.GPIO as io

        self.objLog = logger_object
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
                self.objLog.log('PirMotion - has to be run as root', 'CRITICAL')
            else:
                print('PirMotion - has to be run as root')
            return 1

        self.running = True
        while self.running:
            # Get pir alarm
            if io.input(self.pin) and self.motion is not True:
                if self.objLog:
                    self.objLog.log('PirMotion - Motion Detected', 'INFO')
                else:
                    print('PirMotion - Motion Detected')
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
        """ Get the motions within the past seconds """
        import time
        import Queue
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
        r = self.all_motions
        self.all_motions = []
        return r


class Switch(threading.Thread):
    """
    Class object to handle door switch
    object = Switch(pin=18, check_int=0.5, log_object)
    """

    def __init__(self, logger_object=None, **kwargs):
        threading.Thread.__init__(self)
        self.all_status = []
        import Queue
        import RPi.GPIO as io

        self.objLog = logger_object
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
                self.objLog.log('Switch - has to be run as root', 'CRITICAL')
            else:
                print('Switch - has to be run as root')
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
                    self.objLog.log('Switch - Open', 'INFO')
                else:
                    print('Switch - Open')
                self.status = "Open"
                epoch = int(time.time())
                self.queue.put((epoch, self.status))
            elif not io.input(self.pin) and self.status == "Open":
                if self.objLog:
                    self.objLog.log('Switch - Close', 'INFO')
                else:
                    print('Switch - Close')
                self.status = "Close"
                epoch = int(time.time())
                self.queue.put((epoch, self.status))
            # Pause for next poll
            time.sleep(self.check_int)

    def stop(self):
        self.running = False

    def get(self, past_seconds=0):
        """ Get the motions within the past seconds """
        import time
        import Queue
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
        r = self.all_status
        self.all_status = []
        return r


class DHT(threading.Thread):
    """
    Class object to read temp or humid from DHT_11 sensor
    object = DHT_humid(pin=4, limit=1, check_int=10, type=0(humid)/1(temp), log_object)
    """

    def __init__(self, logger_object=None, **kwargs):
        threading.Thread.__init__(self)
        self.all_status = []
        import Queue
        import Adafruit_DHT

        self.objLog = logger_object
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
                self.objLog.log('DHT - has to be run as root', 'CRITICAL')
            else:
                print('DHT - has to be run as root')
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

        # noinspection PyPep8
        while self.running:
            # Get new value
            new_value = Adafruit_DHT.read_retry(self.sensor, self.pin)[self.type]

            # Read and ignore miss-readings
            # noinspection PyPep8
            verified = [changed(self.value, Adafruit_DHT.read_retry(self.sensor, self.pin)[self.type], self.limit) for i
                        in range(1, self.verify_times)]

            # print "debug: type %s ((%s > %s + %s) or (%s < %s - %s)) and (%s)" % (self.type, new_value, self.value, self.limit, new_value, self.value, self.limit, verified)
            condition = ((new_value > self.value + self.limit) or (new_value < self.value - self.limit)) and all(
                verified)
            if ((new_value > self.value + self.limit) or (new_value < self.value - self.limit)) and all(verified):
                if self.objLog:
                    # noinspection PyPep8
                    self.objLog.log(
                        'DHT Type %s exceeds limit of %s, new value %s' % (self.type, self.limit, new_value))
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
        """ Get the motions within the past seconds """
        import time
        import Queue
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
        r = self.all_status
        self.all_status = []
        return r


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

    if (adcnum > 7) or (adcnum < 0):
        return -1
    GPIO.output(cspin, True)

    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)  # bring CS low

    commandout = adcnum
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3  # we only need to send 5 bits here
    for i in range(5):
        if commandout & 0x80:
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
        if GPIO.input(misopin):
            adcout |= 0x1

    GPIO.output(cspin, True)

    adcout >>= 1  # first bit is 'null' so drop it
    return adcout


class McpValue(threading.Thread):
    # noinspection PyPep8
    """
        Class object to read MCP3008
        object = MCPvalue(minref, adc_in, **kwargs)
        object = MCPvalue(510, 0, clockpin=18, mosipin=24, misopin=23, cspin=25, check_int=1, sleep_int=0.000001, check_times=100, logger_object=logger_object)
        """

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
        self.logger_object = kwargs.get('logger_object', None)
        self.objLog = kwargs.get('logger_object', None)
        self.queue = Queue.Queue()
        self.running = False
        self.status = None

        io.setmode(io.BCM)
        io.setwarnings(False)

    def poll_value(self, minref=0, adc_in=0, debug=False, sleep_int=0.000001, max_retry=10):
        """ Poll value """
        import time
        count = 0
        retry = 0
        result = 0
        peak = 0
        while retry < max_retry:
            for x in range(0, self.check_times):
                value_in = readadc(self.adc_in, self.clockpin, self.mosipin, self.misopin, self.cspin)
                if minref < value_in <= 1023 and value_in > 0:
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
                    # noinspection PyPep8
                    print 'MIN_REF: %s, AVG: (%s/%s)/1023=%s%%, MAX: (%s-%s)/1023=%s%%, COUNT: %s' % (
                    minref, result, count, avg_val, peak, minref, max_val, count_val)
                # Return value
                return avg_val, max_val, count
            else:
                time.sleep(self.check_int)
                result = 0
                peak = 0
                count = 0
                retry += 1
                # Restart next attempt


class PowerMeter(McpValue):
    # noinspection PyPep8
    """
        Class object to Non-Intrusive Current Meter through MCP3008
        object = PowerMeter(minref, adc_in, **kwargs)
        object = PowerMeter(510, 0, clockpin=18, mosipin=24, misopin=23, cspin=25, check_int=1, sleep_int=0.000001, logger_object=logger_object)
        """

    def __init__(self, minref, adc_in, **kwargs):
        self.all_status = []
        import Queue
        McpValue.__init__(self)
        self.minref = minref
        self.adc_in = adc_in
        self.clockpin = kwargs.get('clockpin', 18)
        self.mosipin = kwargs.get('mosipin', 24)
        self.misopin = kwargs.get('misopin', 23)
        self.cspin = kwargs.get('cspin', 25)
        self.check_int = kwargs.get('check_int', 1)
        self.sleep_int = kwargs.get('sleep_int', 0.000001)
        self.objLog = kwargs.get('logger_object', None)
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
                # noinspection PyPep8
                if new < old - limit: return True
            if old - limit < 0:
                # noinspection PyPep8
                if new > old + limit: return True
            if new > old + limit or new < old - limit:
                return True
            else:
                return False

        device_type = 'PowerMeter'
        if not os.geteuid() == 0:
            if self.objLog:
                self.objLog.log('%s - has to be run as root' % device_type, 'CRITICAL')
            else:
                print('%s - has to be run as root' % device_type)
            return 1

        self.running = True
        # Get initial status and supply to queue
        # noinspection PyPep8
        self.avg_val, self.max_val, self.count = self.poll_value(self.minref, self.adc_in, debug=self.debug,
                                                                 sleep_int=0.000001, max_retry=10)
        epoch = int(time.time())
        self.queue.put((epoch, self.avg_val))

        while self.running:
            # For Max
            # noinspection PyPep8
            current_power = \
            self.poll_value(self.minref, self.adc_in, debug=self.debug, sleep_int=0.000001, max_retry=10)[1]

            # Returns a list of True/False based on verify_times used to
            # determine false switch
            # noinspection PyPep8
            verified = [changed(self.max_val,
                                self.poll_value(self.minref, self.adc_in, debug=self.debug, sleep_int=0.000001,
                                                max_retry=10)[1], self.limit) for i in range(1, self.verify_times)]

            if changed(self.max_val, current_power, self.limit) and all(verified):
                self.max_val = current_power
                if self.objLog:
                    self.objLog.log('PowerMeter: ' + str(self.max_val), 'INFO')
                else:
                    print('PowerMeter: ' + str(self.max_val))
                epoch = int(time.time())
                self.queue.put((epoch, self.max_val))

    def stop(self):
        self.running = False

    def reset(self):
        """ Reset current status to force update to Queue """
        self.avg_val = 0
        self.max_val = 0
        self.count = 0

    def get(self, past_seconds=0):
        """ Get the power changes within the past seconds """
        import time
        import Queue
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


class AdcMeter(McpValue):
    # noinspection PyPep8
    """
        Class object to Messure percantage through MCP3008
        object = ADCmeter(adc_in, **kwargs)
        object = ADCmeter(0, clockpin=18, mosipin=24, misopin=23, cspin=25, check_int=1, sleep_int=0.000001, pause_int=1, logger_object=logger_object)
        """

    def __init__(self, adc_in=0, **kwargs):
        self.all_status = []
        import Queue
        McpValue.__init__(self)
        self.minref = 0
        self.adc_in = adc_in
        self.clockpin = kwargs.get('clockpin', 18)
        self.mosipin = kwargs.get('mosipin', 24)
        self.misopin = kwargs.get('misopin', 23)
        self.cspin = kwargs.get('cspin', 25)
        self.check_int = kwargs.get('check_int', 1)
        self.sleep_int = kwargs.get('sleep_int', 1)
        self.objLog = kwargs.get('logger_object', None)
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
                # noinspection PyPep8
                if new < old - limit: return True
            if old - limit < 0:
                # noinspection PyPep8
                if new > old + limit: return True
            if new > old + limit or new < old - limit:
                return True
            else:
                return False

        device_type = 'ADCpercantage'
        if not os.geteuid() == 0:
            if self.objLog:
                self.objLog.log('%s - has to be run as root' % device_type, 'CRITICAL')
            else:
                print('%s - has to be run as root' % device_type)
            return 1

        self.running = True
        # Get initial status and supply to queue
        # noinspection PyPep8
        self.avg_val, self.max_val, self.count = self.poll_value(self.minref, self.adc_in, debug=self.debug,
                                                                 sleep_int=1, max_retry=1)
        epoch = int(time.time())
        self.queue.put((epoch, self.avg_val))

        while self.running:
            # For Average
            current_value = self.poll_value(self.minref, self.adc_in, debug=self.debug, sleep_int=1, max_retry=1)[0]
            if changed(self.avg_val, current_value, self.limit):
                self.avg_val = current_value
                if self.objLog:
                    self.objLog.log('ValueMeter: ' + str(self.avg_val), 'INFO')
                else:
                    print('ValueMeter: ' + str(self.avg_val))
                epoch = int(time.time())
                self.queue.put((epoch, self.avg_val))
            # Pause the time
            time.sleep(self.pause_int)

    def stop(self):
        self.running = False

    def reset(self):
        """ Reset current status to force update to Queue """
        self.avg_val = 0
        self.max_val = 0
        self.count = 0

    def get(self, past_seconds=0):
        """ Get the ADC changes within the past seconds """
        import time
        import Queue
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
        r = self.all_status
        self.all_status = []
        return r


def epoch_to_date(arg_epoch):
    """ Function to convert epoch to DateTime """
    import time
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(arg_epoch)))


def get_local_ip():
    """ Returns local IP-address """
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com", 80))
        ip = s.getsockname()[0]
    except ValueError:
        ip = None
    return ip


class Button(threading.Thread):
    """
    Class object to handle button
    object = Button(3, {1: [function1,args], 2: [function2,args]}, pin=22, check_int=0.1, log_object)
    """

    def __init__(self, timeout=1, functions=None, logger_object=None, **kwargs):
        threading.Thread.__init__(self)
        import RPi.GPIO as io

        self.objLog = logger_object
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
                self.objLog.log('Button - has to be run as root', 'CRITICAL')
            else:
                print('Button - has to be run as root')
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


class Led(threading.Thread):
    """
    Class object to blink led in background
    object = Led(pin=25, check_int=0.1, log_object)
    """

    def __init__(self, blink_type=None, logger_object=None, **kwargs):
        threading.Thread.__init__(self)
        import RPi.GPIO as io

        self.objLog = logger_object
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
                self.objLog.log('Led - has to be run as root', 'CRITICAL')
            else:
                print('Led - has to be run as root')
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
        """ Start blinking """
        self.blink_type = 'blink'
        self.on_time = on
        self.off_time = off

    def led_on(self, period=0):
        """ Turn on for a period """
        import time
        self.blink_type = 'on'
        if period > 0:
            time.sleep(period)
            self.status = 'off'

    def led_off(self):
        """ Turn off led """
        self.blink_type = 'off'

    def stop(self):
        self.blink_type = 'off'
        self.running = False


class Buzzer(threading.Thread):
    """
    Class object to make noise with piezo speaker
    object = Buzzer(pin=27, check_int=0.1, log_object)
    """

    def __init__(self, buzz_type=None, logger_object=None, **kwargs):
        threading.Thread.__init__(self)
        import RPi.GPIO as io

        self.objLog = logger_object
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
                self.objLog.log('Buzzer - has to be run as root', 'CRITICAL')
            else:
                print('Buzzer - has to be run as root')
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
        """ Turn on for a period """
        import time
        self.buzz_type = 'on'
        if period > 0:
            time.sleep(period)
            self.buzz_type = 'off'

    def buzz_off(self):
        """ Turn off  """
        self.buzz_type = 'off'

    def buzz_sos(self):
        """ Play SOS """
        self.buzz_type = 'sos'

    def stop(self):
        self.running = False


def send_gmail(arg_server, arg_port, arg_user, arg_pass, arg_to, arg_from, arg_subject, arg_body, **kwargs):
    """ Function to send a mail with attachments through gmail """

    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
    from email.MIMEImage import MIMEImage
    from email.mime.application import MIMEApplication
    import smtplib
    import re
    import os

    # Create the root message and fill in the from, to, and subject headers
    msg_root = MIMEMultipart('related')
    msg_root['Subject'] = arg_subject
    msg_root['From'] = arg_from
    msg_root['To'] = arg_to
    msg_root.preamble = 'This is a multi-part message in MIME format.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msg_alternative = MIMEMultipart('alternative')
    msg_root.attach(msg_alternative)

    msg_text = MIMEText('Your mail-client doesnt support HTML')
    msg_alternative.attach(msg_text)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    var_body_text = arg_body

    # Create list of images
    if 'Files' in kwargs.keys():
        arg_files = kwargs['Files']
        list_images = [x for x in arg_files if re.match(".+\.(jpg|jpeg|png)$", x, re.IGNORECASE)]
        list_non_images = [x for x in arg_files if not re.match(".+\.(jpg|jpeg|png)$", x, re.IGNORECASE)]

        for i, varImage in enumerate(list_images, start=1):
            var_body_text = var_body_text + '<img src="cid:image' + str(i) + '"><br>'

        msg_text = MIMEText(var_body_text, 'html')
        msg_alternative.attach(msg_text)

        # Attach Images
        for i, varImage in enumerate(list_images, start=1):
            print "Attaching {} to mail".format(varImage)
            fp = open(varImage, 'rb')
            msg_image = MIMEImage(fp.read())
            fp.close()
            # Define the image's ID as referenced above
            msg_image.add_header('Content-ID', '<image' + str(i) + '>')
            msg_root.attach(msg_image)

        # Attach other files
        for i, varFile in enumerate(list_non_images, start=1):
            print "Attaching {} to mail".format(varFile)
            fp = open(varFile, 'rb')
            msg_attach = MIMEApplication(fp.read())
            fp.close()
            msg_attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(varFile))
            msg_root.attach(msg_attach)

    msg_text = MIMEText(var_body_text, 'html')
    msg_alternative.attach(msg_text)

    gmail_user = arg_user
    gmail_password = arg_pass

    # noinspection PyPep8
    if arg_server is None: arg_server = "smtp.gmail.com"
    # noinspection PyPep8
    if arg_port is None: arg_port = 587

    print "Start sending mail"
    mail_server = smtplib.SMTP(arg_server, arg_port)
    mail_server.ehlo()
    mail_server.starttls()
    mail_server.ehlo()
    mail_server.login(gmail_user, gmail_password)
    mail_server.sendmail(gmail_user, arg_to, msg_root.as_string())
    mail_server.close()
    print "Done sending mail"


class Gmail:
    """
    Class object to queue and send gmail
    """

    def __init__(self, arg_user, arg_pass, arg_from=None, arg_server=None, arg_port=None, logger_object=None):
        self.objLog = logger_object
        self.running = False
        self.user = arg_user
        self.password = arg_pass
        # noinspection PyPep8
        if arg_from is None: arg_from = arg_user
        self.mail_from = arg_from
        # noinspection PyPep8
        if arg_server is None: arg_server = "smtp.gmail.com"
        # noinspection PyPep8
        if arg_port is None: arg_port = 587
        self.server = arg_server
        self.port = arg_port

    def send(*func_arg):
        import threading
        t = threading.Thread(target=Gmail.worker, args=func_arg)
        t.start()

    def worker(self, arg_to, arg_subject, arg_body, arg_file=None):
        from email.MIMEMultipart import MIMEMultipart
        from email.MIMEText import MIMEText
        from email.MIMEImage import MIMEImage
        from email.mime.application import MIMEApplication
        import smtplib
        import re
        import os

        # Create the root message and fill in the from, to, and subject headers
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = arg_subject
        msgRoot['From'] = self.mail_from
        msgRoot['To'] = arg_to
        msgRoot.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msg_alternative = MIMEMultipart('alternative')
        msgRoot.attach(msg_alternative)

        msg_text = MIMEText('Your mail-client doesnt support HTML')
        msg_alternative.attach(msg_text)

        # We reference the image in the IMG SRC attribute by the ID we give it below
        var_body_text = arg_body

        # Create list of images
        if arg_file is not None:
            list_images = [x for x in arg_file if re.match(".+\.(jpg|jpeg|png)$", x, re.IGNORECASE)]
            list_non_images = [x for x in arg_file if not re.match(".+\.(jpg|jpeg|png)$", x, re.IGNORECASE)]

            for i, varImage in enumerate(list_images, start=1):
                var_body_text = var_body_text + '<img src="cid:image' + str(i) + '"><br>'

            msg_text = MIMEText(var_body_text, 'html')
            msg_alternative.attach(msg_text)

            # Attach Images
            for i, varImage in enumerate(list_images, start=1):
                fp = open(varImage, 'rb')
                msg_image = MIMEImage(fp.read())
                fp.close()
                # Define the image's ID as referenced above
                msg_image.add_header('Content-ID', '<image' + str(i) + '>')
                msgRoot.attach(msg_image)

            # Attach other files
            for i, varFile in enumerate(list_non_images, start=1):
                fp = open(varFile, 'rb')
                msg_attach = MIMEApplication(fp.read())
                fp.close()
                msg_attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(varFile))
                msgRoot.attach(msg_attach)

        msg_text = MIMEText(var_body_text, 'html')
        msg_alternative.attach(msg_text)

        gmail_user = self.user
        gmail_password = self.password

        mail_server = smtplib.SMTP(self.server, self.port)
        mail_server.ehlo()
        mail_server.starttls()
        mail_server.ehlo()
        mail_server.login(gmail_user, gmail_password)
        mail_server.sendmail(gmail_user, arg_to, msgRoot.as_string())
        mail_server.close()


# noinspection PyMethodMayBeStatic
class FTP(threading.Thread):
    """ Class for using FTP """

    def __init__(self, ftp_server, ftp_user, ftp_pass, logger_object=None, **kwargs):
        threading.Thread.__init__(self)
        import ftplib
        self.ftp = ftplib.FTP()
        self.ftp = ftplib.FTP()
        import Queue
        self.queue = Queue.Queue()
        self.objLog = logger_object
        self.running = False
        self.server = ftp_server
        self.user = ftp_user
        self.ftpPass = ftp_pass
        self.logger_object = logger_object
        self.status = None

        # noinspection PyPep8
        if not 'port' in kwargs:
            self.port = 21
        else:
            self.port = kwargs['port']

    def chdir(self, ftp_path, ftp_conn):
        """ function to iterate through dirs using ftplib """

        def check_dir(dir, ftp_conn):
            """ Assure all dirs exists """
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
        import os
        import time
        self.running = True

        while self.running:
            if self.queue.qsize() > 0:
                self.status = "transfer"
                command, next_file_list, next_file_dir = self.queue.get()
                # Initiate FTP object
                try:
                    self.ftp.connect(self.server, self.port)
                    self.ftp.login(self.user, self.ftpPass)
                    if command == 'upload':
                        for ftpFile in next_file_list:
                            # noinspection PyPep8
                            if next_file_dir is not None: self.chdir(next_file_dir, self.ftp)
                            file = open(ftpFile, 'rb')
                            self.ftp.storbinary('STOR ' + os.path.basename(ftpFile), file)
                            file.close()
                    if command == 'download':
                        for ftpFile in next_file_list:
                            # noinspection PyPep8
                            if next_file_dir is not None: self.chdir(next_file_dir, self.ftp)
                            if next_file_dir is not None:
                                # noinspection PyPep8
                                self.ftp.retrbinary("RETR " + ftpFile, open(
                                    os.path.dirname(next_file_dir) + "/" + os.path.basename(ftpFile), 'wb').write)
                            else:
                                self.ftp.retrbinary("RETR " + ftpFile, open(os.path.basename(ftpFile), 'wb').write)
                    if self.objLog:
                        self.objLog.log("FTP command: " + command + ", Files: " + str(next_file_list), 'INFO')
                    else:
                        print("FTP command: " + command + ", Files: " + str(next_file_list))
                    self.ftp.quit()
                except ValueError:
                    self.objLog.log("FTP fail " + str(ValueError), "ERROR")
                time.sleep(3)
            self.status = None

    def upload(self, file_list, file_dir=None):
        """ Add files for upload to queue """
        self.queue.put(['upload', file_list, file_dir])

    def download(self, file_list, file_dir=None):
        """ Add files for download to queue """
        self.queue.put(['download', file_list, file_dir])

    def dir(self, ftp_dir='.'):
        """ List directory """
        self.ftp.connect(self.server, self.port)
        self.ftp.login(self.user, self.ftpPass)
        dir_list = self.ftp.dir(ftp_dir)
        self.ftp.quit()
        return dir_list

    def stop(self):
        self.running = False


def PiCamera(filename, res=None):
    import picamera
    import time
    with picamera.PiCamera() as camera:
        # noinspection PyPep8
        if res is not None: camera.resolution = (800, 600)
        camera.start_preview()
        # Camera warm-up time
        time.sleep(2)
        camera.capture(filename)
        camera.stop_preview()


def read_lux_meter():
    # Get I2C bus
    bus = smbus.SMBus(1)

    bus.write_byte_data(0x39, 0x00 | 0x80, 0x03)
    bus.write_byte_data(0x39, 0x01 | 0x80, 0x02)

    time.sleep(0.5)
    data = bus.read_i2c_block_data(0x39, 0x0C | 0x80, 2)
    data1 = bus.read_i2c_block_data(0x39, 0x0E | 0x80, 2)

    # Convert the data
    ch0 = data[1] * 256 + data[0]
    ch1 = data1[1] * 256 + data1[0]

    # Output data to screen
    # print "Full Spectrum(IR + Visible) :%d lux" % ch0
    # print "Infrared Value :%d lux" % ch1
    # print "Visible Value :%d lux" % (ch0 - ch1)
    return ch0


class Luxmeter:
    i2c = None

    def __init__(self, address=0x39, debug=0, pause=0.8):
        # from Adafruit_I2C import Adafruit_I2C
        import Adafruit_GPIO.I2C as I2C
        self.i2c = I2C.Device(address, 1)
        self.address = address
        self.pause = pause
        self.debug = debug
        self.gain = 0  # no gain preselected
        self.i2c.write8(0x80, 0x03)  # enable the device

    def set_gain(self, gain=1):
        """ Set the gain """
        import time
        if gain != self.gain:
            if gain == 1:
                self.i2c.write8(0x81, 0x02)
                if self.debug:
                    print "Setting low gain"
            else:
                self.i2c.write8(0x81, 0x12)
                if self.debug:
                    print "Setting high gain"
            self.gain = gain
            # set gain = 1X and timing
            # set gain = 16X and timing
            # safe gain for calculation
            time.sleep(self.pause)

    def read_word(self, reg):
        """Reads a word from the I2C device"""
        try:
            wordval = self.i2c.readU16(reg)
            newval = self.i2c.reverseByteOrder(wordval)
            if self.debug:
                print("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address, wordval & 0xFFFF, reg))
            return newval
        except IOError:
            print("Error accessing 0x%02X: Check your I2C address" % self.address)
            return -1

    def read_full(self, reg=0x8C):
        """Reads visible+IR diode from the I2C device"""
        return self.read_word(reg)

    def read_ir(self, reg=0x8E):
        """Reads IR only diode from the I2C device"""
        return self.read_word(reg)

    def get_lux(self, gain=1):
        """Grabs a lux reading either with autoranging (gain=0) or with a specified gain (1, 16)"""
        if gain == 1 or gain == 16:
            self.set_gain(gain)  # low/highGain
            ambient = self.read_full()
            ir = self.read_ir()
        elif gain == 0:  # auto gain
            self.set_gain(16)  # first try highGain
            ambient = self.read_full()
            if ambient < 65535:
                ir = self.read_ir()

        if ambient >= 65535 or ir >= 65535:  # value(s) exeed(s) data
            self.set_gain(1)  # set lowGain
            ambient = self.read_full()
            ir = self.read_ir()

        if self.gain == 1:
            ambient *= 16  # scale 1x to 16x
            ir *= 16  # scale 1x to 16x

        try:
            ratio = (ir / float(ambient))  # changed to make it run under python
        except ZeroDivisionError:
            ratio = 0

        if self.debug:
            print "IR Result", ir
            print "Ambient Result", ambient
        if (ratio >= 0) & (ratio <= 0.52):
            lux = (0.0315 * ambient) - (0.0593 * ambient * (ratio ** 1.4))
        elif ratio <= 0.65:
            lux = (0.0229 * ambient) - (0.0291 * ir)
        elif ratio <= 0.80:
            lux = (0.0157 * ambient) - (0.018 * ir)
        elif ratio <= 1.3:
            lux = (0.00338 * ambient) - (0.0026 * ir)
        elif ratio > 1.3:
            lux = 0
        return lux


class LuxMeter(threading.Thread):
    """
    Class object to read lux from a TSL2561
    object = LuxMeter(limit=1, check_int=10, log_object)
    """

    def __init__(self, logger_object=None, **kwargs):
        threading.Thread.__init__(self)
        self.all_status = []
        import Queue

        self.objLog = logger_object
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
                self.objLog.log('Lux - has to be run as root', 'CRITICAL')
            else:
                print('Lux - has to be run as root')
            return 1

        self.running = True
        # Get initial status and supply to queue
        self.value = int(read_lux_meter())
        if self.value > 50:
            self.value = 50

        epoch = int(time.time())
        self.queue.put((epoch, self.value))

        while self.running:
            # Get new value
            new_value = int(read_lux_meter())
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
        """ Get the motions within the past seconds """
        import time
        import Queue
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
        r = self.all_status
        self.all_status = []
        return r


class ModemDongle(threading.Thread):
    """
    Class object to handle 3G Dongle
    object = ModemDongle(log_object, tty='/dev/ttyUSB0')
    object = ModemDongle(incoming_cmd={'search_for_word_in_sms': 'function_or_external_script_with_rest_as_args'})
    """

    # noinspection PyProtectedMember
    def __init__(self, logger_object=None, **kwargs):
        threading.Thread.__init__(self)
        import Queue
        import sms
        import ast
        import time

        time.sleep(60)

        self.objLog = logger_object
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
        # noinspection PyPep8
        try:
            import m
        except:
            print "Please install memcache to support reading status"
        else:
            self.shared = m.Client(['127.0.0.1:11211'], debug=1)

    def run(self):
        import time
        import re
        import subprocess
        from datetime import datetime
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
            try:
                msgs = self.m.messages()
            except SerialException:
                self.objLog.log('SMS DONGLE ERROR - REBOOTING in 3 hours', 'ERROR')
                time.sleep(10800)
                import subprocess
                command = "/usr/bin/sudo /sbin/shutdown -r now"
                process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
                output = process.communicate()[0]
                print output

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
                                args = args.split()
                                print "Command is existing function, calling %s with args: %s" % (cmd, str(args))
                                # Might add arguments in the future
                                result = cmd_func(*args)
                                if self.objLog:
                                    # noinspection PyPep8
                                    self.objLog.log('Sending message to %s with body: %s' % (sms.number, str(result)),
                                                    'INFO')
                                else:
                                    print 'Sending SMS to %s with body: %s' % (sms.number, str(result)[:50])
                                self.send(sms.number, str(result))
                            else:
                                print "No function, trying to call external script %s" % (cmd,)
                                # noinspection PyPep8
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
                        # noinspection PyPep8
                        self.objLog.log('Sending parial message 160-320 to %s: %s' % (number, str(message)[160:][:160]),
                                        'INFO')
                    time.sleep(10)
                    self.m.send(number, str(message)[160:][:160])
                    if len(message) > 320:
                        if self.objLog:
                            # noinspection PyPep8
                            self.objLog.log(
                                'Sending parial message 320-480 to %s: %s' % (number, str(message)[320:][:160]), 'INFO')
                        time.sleep(10)
                        self.m.send(number, str(message)[320:][:160])

            # Pause for next poll
            time.sleep(self.check_int)

    def stop(self):
        self.running = False

    def send(self, number, message):
        """ Add sms message to send """
        self.queue.put((number, message))


class DongleTCPRequestHandler(SocketServer.BaseRequestHandler):
    """ BaseRequestHandler uses TCPserver and does the actual work """

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
            print(get_datetime() + ": Sending SMS - " + str(data))

        response = "ok"
        self.request.sendall(response)


class DongleTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, server_address, request_handler_class, dongle_object):
        """ Extend init to handle Dongle object """
        self.dongle = dongle_object
        SocketServer.TCPServer.__init__(self, server_address, request_handler_class)
