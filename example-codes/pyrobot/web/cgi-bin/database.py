import sqlite3, csv
import os
import types
import logging
import pymysql
import numpy as np

class Database(object):
    """Abstract base Database class."""
    
    def __init__(self):
        raise NotImplementedError("class Database is an abstract class and cannot be instantiated")
    
    def CreateTable(self, table_name, columns, drop_if_exists=True):
        raise NotImplementedError("CreateTable not implemented")
            
    def Insert(self, table_name, l):
        raise NotImplementedError("Insert not implemented")
    
    def DoesTableExist(self, table_name):
        raise NotImplementedError("DoesTableExist not implemented")
    
    
class SQLDatabase(Database):
    """Abstract base SQLDatabase class."""
    
    def __init__(self, filename):
        raise NotImplementedError("class SQLDatabase is an abstract class and cannot be instantiated")
    
    def Execute(self, command, arguments=None):
        raise NotImplementedError("Execute not implemented")
    
    def Commit(self):
        raise NotImplementedError("Commit not implemented")
    
    def Insert(self, table_name, l):
        raise NotImplementedError("Commit not implemented")

    def CreateTable(self, table_name, columns, drop_if_exists=True):
        if drop_if_exists:
            self.Execute("DROP TABLE IF EXISTS %s" % table_name)
        #elif self.DoesTableExist(table_name):
        #    return
        
        if type(columns) == types.ListType:
            columns = ','.join(['%s TEXT' % col for col in columns])    
        
        self.Execute("CREATE TABLE IF NOT EXISTS %s (%s)" % (table_name, columns))
    
    def CreateIndex(self, index_name, table_name, columns, unique=True, drop_if_exists=True):
        if drop_if_exists:
            self.Execute("DROP INDEX IF EXISTS %s" % index_name)
        if unique:
            self.Execute("CREATE UNIQUE INDEX IF NOT EXISTS %s ON %s (%s)" % (index_name, table_name, columns))
        else:
            self.Execute("CREATE INDEX IF NOT EXISTS %s ON %s (%s)" % (index_name, table_name, columns))
            
    def DoesTableExist(self, table_name):
        raise NotImplementedError("DoesTableExist not implemented")
    
    def Query2String(self, query, column_names=None):
        s = ""
        if column_names:
            s += ','.join(column_names) + "\n"
        for row in self.Execute(query):
            s += ','.join([str(x) for x in row]) + "\n"
        return s

    def Query2CSV(self, filename, query, column_names=None):
        writer = csv.writer(open(filename, 'w'))
        if column_names:
            writer.writerow(column_names)
        for row in self.Execute(query):
            writer.writerow(list(row))
    
    def Query2HTML(self, html_writer, query, column_names=None):
        html_writer.write('<table border="1">\n')
        if column_names:
            html_writer.write('  <tr>' + "".join([('<td><b>' + str(s) + '</b></td>') for s in column_names]) + '</tr>\n')
        for row in self.Execute(query):
            html_writer.write('  <tr>' + "".join([('<td>' + str(s) + '</td>') for s in row]) + '</tr>\n')
        html_writer.write('</table>\n')

    def GetColumnNames(self, table_name):        
        column_names = []
        for unused_index, name, unused_type, unused_can_be_null, unused_default_value, unused_stam \
            in self.Execute("PRAGMA table_info(%s)" % table_name):
            
            column_names.append(name)
        
        return column_names
    
    def Table2String(self, table_name, write_titles=True):
        if write_titles:
            column_names = self.GetColumnNames(table_name)
        else:
            column_names = None
        return self.Query2String("SELECT * FROM %s" % table_name, column_names)
    
    def Table2CSV(self, filename, table_name, write_titles=True):
        if write_titles:
            column_names = self.GetColumnNames(table_name)
        else:
            column_names = None
        self.Query2CSV(filename, "SELECT * FROM %s" % table_name, column_names)
    
    def Table2HTML(self, html_writer, table_name, write_titles=True):
        if write_titles:
            column_names = self.GetColumnNames(table_name)
        else:
            column_names = None
        self.Query2HTML(html_writer, "SELECT * FROM %s" % table_name, column_names)

    def DictReader(self, table_name):
        titles = self.GetColumnNames(table_name)
        table_data = []
        for row in self.Execute("SELECT * FROM %s" % table_name):
            row_dict = {}
            for i, title in enumerate(titles):
                row_dict[title] = row[i]
            table_data.append(row_dict)
        return table_data    
    
    def SaveSparseNumpyMatrix(self, table_name, mat, dtype='REAL'):
        """
            Creates a new table and saves a 2D array in the database
            in a sparse notation.
        """
        if len(mat.shape) != 2:
            raise ValueError("Can only save 2D arrays in a database")
        
        if mat.dtype in ('int', 'int64', 'int32', 'int16'):
            dtype = 'INT'
        elif mat.dtype in ('float', 'float64', 'float32'):
            dtype = 'FLOAT'
        else:
            raise ValueError("Can only save int or float matrices in a database")
        columns = "row INT, column INT, value %s" % dtype
        self.CreateTable(table_name, columns, drop_if_exists=True)
        
        # insert the first entry which contains the dimensions of the matrix
        self.Insert(table_name, [mat.shape[0], mat.shape[1], 0])
        
        # insert all non-zero values
        r_nonzero, c_nonzero = np.nonzero(mat)
        for r, c in zip(r_nonzero.flat, c_nonzero.flat):
            if dtype == 'INT':
                self.Insert(table_name, [int(r), int(c), int(mat[r, c])])
            else:
                self.Insert(table_name, [int(r), int(c), float(mat[r, c])])

    def LoadSparseNumpyMatrix(self, table_name):
        """
            Loads the values of a matrix stored in the database as a table.
        """
        mat = None
        for r, c, v in self.Execute("SELECT row, column, value FROM %s" % table_name):
            if mat is None:
                if type(v) == types.IntType:
                    mat = np.zeros((r, c), dtype='int')
                elif type(v) == types.FloatType:
                    mat = np.zeros((r, c), dtype='float')
                else:
                    raise ValueError('The values of a sparse matrix must be Int or Float')
            else:
                mat[r, c] = v
        return np.matrix(mat)
            
    def LoadNumpyMatrix(self, table_name):
        """
            Loads the values of a matrix stored in the database as a table.
        """
        mat = []
        for row in self.Execute("SELECT * FROM %s" % table_name):
            mat.append(row)
        return np.matrix(mat)

    def SaveNumpyMatrix(self, table_name, mat, dtype='REAL'):
        """
            Creates a new table and saves a 2D array in the database.
        """
        if len(mat.shape) != 2:
            raise ValueError("Can only save 2D arrays in a database")
        
        if mat.dtype in ('int', 'int64', 'int32', 'int16'):
            dtype = 'INT'
        elif mat.dtype in ('float', 'float64', 'float32'):
            dtype = 'REAL'
        else:
            raise ValueError("Can only save int or float matrices in a database")
        columns = ', '.join('col%d %s' % (i, dtype)
                            for i in xrange(mat.shape[1]))
        self.CreateTable(table_name, columns, drop_if_exists=True)
        for j in xrange(mat.shape[0]):
            if dtype == 'INT':
                self.Insert(table_name, [int(x) for x in mat[j, :].flat])
            else:
                self.Insert(table_name, [float(x) for x in mat[j, :].flat])
        
class SqliteDatabase(SQLDatabase):
    
    def __init__(self, filename, flag='w'):
        """
            Connects to a Sqlite database.
            filename - the name of the file containing the database
            flag - can only be 'w' or 'r'.
                   use 'r' to verify that the file already exists (throws IOError otherwise)
                   use 'w' to create the file if it doesn't exist
        """
        self.filename = filename
        
        if flag.lower() == 'r':
            if not os.path.exists(filename):
                raise IOError('No such file or directory: %s' % filename)
            self.comm = sqlite3.connect(filename)
        elif flag.lower() == 'w':
            self.comm = sqlite3.connect(filename)
        else:
            raise ValueError('Illegal flag: %s' % str(flag))
    
    def Execute(self, command, arguments=None):
        if arguments:
            try:
                return self.comm.execute(command, arguments)
            except sqlite3.InterfaceError, e:
                logging.error('Failed to execute database command: %s - %s' % \
                              (command, str(arguments)))
                raise e
        else:
            try:
                return self.comm.execute(command)
            except sqlite3.InterfaceError, e:
                logging.error('Failed to execute database command: %s' % \
                              command)
                raise e
        
    def Insert(self, table_name, l):
        sql_command = "INSERT INTO %s VALUES(%s)" % (table_name, ','.join(["?"]*len(l)))
        return self.Execute(sql_command, l)
    
    def DoesTableExist(self, table_name):
        for unused_row in self.Execute("SELECT name FROM sqlite_master WHERE name='%s'" % table_name):
            return True
        return False

    def Commit(self):
        self.comm.commit()

    def __del__(self):
        self.comm.commit()
        self.comm.close()
    
    def __str__(self):
        return '<SqliteDatabase: %s>' % self.filename

class MySQLDatabase(SQLDatabase):
    """
        To grant privileges to more users and IP addresses use the following command:
            GRANT ALL PRIVILEGES ON *.* TO <remoteuser>@'%' IDENTIFIED BY "<userpassword>";
        
    """
    
    def __init__(self, host, user, passwd, db, port=3306):
        self.comm = pymysql.connect(host=host, user=user, passwd=passwd, db=db,
                                    port=port)
        
    def Execute(self, command, arguments=None):
        try:
            cursor = self.comm.cursor()
            cursor.execute(command, args=arguments)
            return cursor.fetchall()
        except (pymysql.ProgrammingError, pymysql.OperationalError) as e:
            if not arguments:
                logging.error('Failed to execute database command: %s' % command)
            else:
                logging.error('Failed to execute database command: %s - %s' % \
                              (command, str(arguments)))
            raise e

    def Insert(self, table_name, l):
        str_l = []
        for x in l:
            if x is None:
                str_l.append('NULL')
            else:
                str_l.append("'" + str(x) + "'")
        values = ','.join(str_l)
        
        sql_command = "INSERT INTO %s VALUES(%s)" % (table_name, values)
        return self.Execute(sql_command)
        
    def Commit(self):
        self.comm.commit()
        
    def __del__(self):
        self.comm.commit()
        self.comm.close()
        
    def __str__(self):
        return '<MySQLDatabase: %s>' % self.filename

    def DoesTableExist(self, table_name):
        for unused_row in self.Execute("SELECT name FROM sqlite_master WHERE name='%s'" % table_name):
            return True
        return False