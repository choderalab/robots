"""
    This program requires the xlrd package, which can be found at: http://pypi.python.org/pypi/xlrd
"""
from xlrd import open_workbook
import numpy as np
import types, re, time
from time import strptime, strftime

class VictorParser():
    # all Victor experiments have only one plate, so their ID is 0
    PLATE_ID = 0

    def __init__(self):
        self.data = []
        self.measurement_names = []
        self.plate = {}
        
        self.reading_label_map = {'Absorbance @ 600 (1.0s) (A)': 'OD600'}
    
    def ParseExcel(self, fp):
        wd = open_workbook(file_contents=fp.read())
        
        # Get the date and time of the experiment from the Excel sheet
        # called "Protocol".
        protocol_sheet = wd.sheet_by_index(2)
        
        self.measurement_time = None
        self.serial_number = None
        
        for r in xrange(protocol_sheet.nrows):
            row = protocol_sheet.row_values(r)[0]
            
            serial_num = re.findall('Instrument serial number: \.* ([0-9]+)', row)
            if len(serial_num) > 0:
                self.serial_number = serial_num[0]
                continue
            
            measured_on = re.findall('Measured on \.* ([0-9\s\-\/:]+)$', row)
            if len(measured_on) > 0:
                self.measurement_time = strptime(measured_on[0], '%d/%m/%Y %H:%M:%S')
                continue
            
            measured_on = re.findall('Measured on \.* ([0-9\s\-\/:]+ [A|P]M)$', row)
            if len(measured_on) > 0:
                self.measurement_time = strptime(measured_on[0], '%m/%d/%Y %H:%M:%S %p')
                continue

        if self.measurement_time is None:
            raise Exception("cannot get measurement date in XLS file: " + fname)
        
        # Get the values of all the measurements from the "List" Excel sheet
        sheet = wd.sheet_by_index(0)
        titles = sheet.row_values(0) # [Plate, Repeat, Well, Type] + [Time, Measurement] * n
        self.measurement_names = []
        for c in range(5, len(titles), 2):
            m_name = str(titles[c])
            if m_name in self.reading_label_map:
                m_name = self.reading_label_map[m_name]
            if titles[c] not in self.measurement_names:
                self.measurement_names.append(m_name)
        
        for m_name in self.measurement_names:
            self.plate[m_name] = {}
            for r in range(8):
                for c in range(12):
                    self.plate[m_name][(r,c)] = []
            
        for r in range(1, sheet.nrows):
            row = sheet.row_values(r)
            _plate, _repeat, well, _type = row[0:4]
            
            well_row = ord(well[0]) - ord('A')
            well_col = int(well[1:]) - 1
            
            for c in range(4, len(row), 2):
                try:
                    time = float(row[c]) * 24 # convert days to hours
                    value = float(row[c+1])
                    m_name = str(titles[c+1])
                    if m_name in self.reading_label_map:
                        m_name = self.reading_label_map[m_name]
                    self.plate[m_name][(well_row, well_col)].append((time, value))
                except ValueError:
                    continue

    def GetData(self, m_name, row, col):
        """
            m_name - the type of measurement. Can be an index (int) according to
                     the order the measurements have been done.
        """
        if type(m_name) == types.IntType:
            m_name = self.measurement_names[m_name]
        data_series = self.plate[m_name][(row, col)]
        times = np.array([t for (t, v) in data_series])
        values = np.array([v for (t, v) in data_series])
        return times, values
    
    def WriteToDB(self, db, exp_id, plate_id=0):
        for m_name in sorted(self.plate.keys()):
            for row, col in sorted(self.plate[m_name].keys()):
                for t, v in self.plate[m_name][(row, col)]:
                    time_in_sec = time.mktime(self.measurement_time) + 3600.0*t
                    db_row = [exp_id, plate_id, m_name, row, col, time_in_sec, v]
                    #print ', '.join(['%s' % x for x in db_row])
                    db.Insert('tecan_readings', db_row)

    @staticmethod
    def GetTimeString(t=None):
        t = t or time.localtime()
        return time.strftime('%Y-%m-%d %H:%M:%S', t)

    @staticmethod
    def ImportFileToDB(fp, db, exp_id=None):
        vp = VictorParser()
        vp.ParseExcel(fp)
        
        exp_id = exp_id or VictorParser.GetTimeString(vp.measurement_time)   
        print "Experiment ID: " + exp_id
    
        # delete any previous data regarding this exp_id
        db.Execute("DELETE FROM tecan_readings WHERE exp_id='%s'" % exp_id)
        q2 = "DELETE FROM tecan_experiments WHERE exp_id='" + exp_id + \
             "' AND serial_number='" + vp.serial_number + "'"
        print q2
        db.Execute(q2)
        db.Execute("DELETE FROM tecan_plates WHERE exp_id='%s'" % exp_id)
        
        desc = "Imported from Victor on " + VictorParser.GetTimeString()
        db.Insert('tecan_experiments', [exp_id, vp.serial_number, desc])
        db.Insert('tecan_plates', [exp_id, vp.PLATE_ID, "", None, None])
        vp.WriteToDB(db, exp_id)
        db.Commit()
        
        return exp_id