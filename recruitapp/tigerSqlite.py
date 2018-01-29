import sqlite3
import os
import pickle
import json
import re
#TODO: instead of manual 'text', 'int', use builtins i.e int, str, dict, str
from abc import ABCMeta, abstractmethod
class TableNotFoundError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
class EmptyDictParamters(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
class DeletionWithEmptyParameters(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
converter = {dict:'text', list:'text', str:'text', int:'int'} #default: 'text'
def run_custom(initial):
    """`custom` WILL NOT JSONIFY INPUT IN ARGS"""
    def wrapper(cls, command,  *args):
        new_command, args = initial(cls, command, *args)
        if command.lower().startswith('select'):
            if not args:
                return list(sqlite3.connect(cls.filename).cursor().execute(command))
            return list(sqlite3.connect(cls.filename).cursor().execute(command, args))
        if not args:
            conn = sqlite3.connect(cls.filename)
            conn.execute(command)
            conn.commit()
            conn.close()
        else:
            conn = sqlite.connect(cls.filename)
            conn.execute(command, args)
            conn.commit()
            conn.close()
    return wrapper
class SQL:
    __metaclass__ = ABCMeta

    @abstractmethod
    def select(self, table, values = [], *args):
        """`values` stores the columns to be select, and `args` stores the colums whose values must correspond to those in `args`"""


    @abstractmethod
    def insert(self, tablename, *args):
        """`args` stores the variables in key-value type"""

    @abstractmethod
    def update(self, tablename, targets, new_vals):
        """targets stores the variables with values to be updated, and new_vals stores the variable conditions that must be met"""


    @abstractmethod
    def create(self, tablename, *args):
        """creates new table with args storing the column names and column value types

        create('table1.db', [('name', 'text'), ('age', int)])

        """

    @abstractmethod
    def delete(self, tablname, *args):
        #removes the specified columns
        pass

class Sqlite(SQL):
    '''
    tigerSqlite3 provides an intuitive, Pythonic, sqlite3 wrapper

    '''
    def __init__(self, filename):
        self.filename = filename
        self.table_name = None

    @classmethod
    def select_all(cls, tablename, filename):
        command = 'SELECT * FROM {}'.format(tablename)
        data = list(sqlite3.connect(filename).cursor().execute(command))
        for row in data:
            current = []
            for val in row:
                try:
                    new_data = json.loads(val)
                except:
                    current.append(val)
                else:
                    current.append(new_data)
            yield current
        #return [[json.loads(b) if not isinstance(b, int) else b for b in i] for i in list(sqlite3.connect(filename).cursor().execute(command))]

    @property
    def dbfile(self):
        if self.table_name:
            return list(sqlite3.connect(self.filename).cursor().execute('SELECT * FROM {}'.format(self.table_name)))
        raise TypeError('Must assign the tablename')

    @dbfile.setter
    def dbfile(self, tablename):
        self.table_name = tablename

    def select(self, table, values = [], *args): #now, pass list of tuples

        command = 'SELECT {} FROM {}'.format('*' if not values else ', '.join(values), table) if not args else 'SELECT {} FROM {} WHERE {}'.format('*' if not values else ', '.join(values), table, ', '.join('{}=?'.format(a) for a, b in args))

        data = list(sqlite3.connect(self.filename).cursor().execute(command))
        for row in data:
            current = []
            for val in row:
                try:
                    new_data = json.loads(val)
                except:
                    current.append(val)
                else:
                    current.append(new_data)
            yield current
        #return [[json.loads(b) if not isinstance(b, int) and not isinstance(b, str) else b for b in i] for i in sqlite3.connect(self.filename).cursor().execute(command)]

    @run_custom
    def custom(self, command, *args):
        return command, args

    def insert(self, tablename, *args):
        if not args:
            raise  EmptyDictParamters("Parameters must not contain empty dictionaries")

        command = 'INSERT INTO {} ({}) VALUES ({})'.format(tablename, ', '.join([a for a, b in args]), ', '.join(['?']*len(args)))
        print command
        conn = sqlite3.connect(self.filename)
        conn.execute(command, [json.dumps(b) if not isinstance(b, int) and not isinstance(b, float) else b for a, b in args])
        conn.commit()
        conn.close()

    def update(self, tablename, targets, new_vals):

        if not (targets or new_vals):
            raise  EmptyDictParamters("Parameters must not contain empty dictionaries")

        command = 'UPDATE {} SET {} WHERE {}'.format(tablename, ", ".join("{}=?".format(a) for a, b in targets), ", ".join("{}=?".format(a) for a, b in new_vals))
        print "command", command
        conn = sqlite3.connect(self.filename)
        #print [json.dumps(b) if not isinstance(b, int) else b for a, b in data1]+[json.dumps(b) if not isinstance(b, int) or not isinstance(b, float) else b for a, b in data2]
        
        conn.execute(command, [json.dumps(b) if not isinstance(b, int) else b for a, b in targets]+[json.dumps(b) if not isinstance(b, int) or not isinstance(b, float) else b for a, b in new_vals])
        conn.commit()
        conn.close()



    def create(self, tablename, *args):

        if self.filename not in os.listdir(os.getcwd()):
            os.system('touch {}'.format(self.filename))

        conn = sqlite3.connect(self.filename)
        command = 'CREATE TABLE {} ({})'.format(tablename, ', '.join("{} {}".format(a, b) for a, b in args))
        conn.execute(command)
        conn.commit()
        conn.close()
    def delete(self, tablename, *args):
        print "deletion args", args
        if not args:
            raise DeletionWithEmptyParameters('function parameter must include at least one deletion condition')
        command = "DELETE FROM {} WHERE {}".format(tablename, ', '.join("{}=?".format(a) for a, b in args))
        print "deletion command", command
        print "deletion data results", [json.dumps(b) if not isinstance(b, int) and not isinstance(b, str) else b.decode('unicode-escape') if isinstance(b, str) else b for a, b in args]
        conn = sqlite3.connect(self.filename)
        #print [json.dumps(b) if not isinstance(b, int) and not isinstance(b, str) else b for a, b in args]

        conn.execute(command, [json.dumps(b) if not isinstance(b, int) and not isinstance(b, str) else b.decode('unicode-escape') if isinstance(b, str) else b for a, b in args])
        conn.commit()
        conn.close()

    def __iter__(self):
        for db_file in [i for i in os.listdir(os.getcwd()) if i.endswith('.txt')]:
            yield db_file

    def __getattr__(self, name):
        '''easy column access'''
        if not name.startswith('get_'):
            raise AttributeError("'get' method must begin with 'get_'")
        def wrapper(tablename):
            values = re.findall('[a-zA-Z]+', name[len('get_'):])
            data = list(sqlite3.connect(self.filename).cursor().execute('SELECT {} FROM {}'.format(', '.join(values), tablename)))
            final_data = []
            for row in data:
                s = []
                for item in row:
                    try:
                        new_data = json.loads(item)
                    except:
                        s.append(item)
                    else:
                        s.append(new_data)
                final_data.append(s)

            return final_data
        return wrapper


'''
#perhaps use json
db = Sqlite('testdb.db')
#db.create('testing_table', *[('name', 'text'), ('id', 'int'), ('age', 'int')])


db.insert('testing_table', *[('name', 'James'), ('id', 34324), ('age', 17)])
db.insert('testing_table', *[('name', {'first':'James', 'last':'Petullo'}), ('id', 40000), ('age', 18)])
db.insert('testing_table', *[('name', 'James'), ('age', 18), ('id', [574026, 978422])])
#db.update('testing_table', [('name', [{'james':17}, 'funny!!'])], [('age', 18)])

#print list(Sqlite.select_all('testing_table', 'testdb.db'))
print db.custom('SELECT * FROM testing_table')
'''
