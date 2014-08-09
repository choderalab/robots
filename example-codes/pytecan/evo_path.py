import sys, os, csv
import numpy as np
from argparse import ArgumentParser
from toolbox.database import MySQLDatabase
from pytecan.evo_is_active import read_exp_id_csv


def Header():
    """
    Creates a worklist file and writes the first init command (tip size to be used in the fllowing commands)
    """
    header = [] 
    header += ['S;1']
    return header
    
def Footer():
    """
    Creates a worklist file and writes the first init command (tip size to be used in the fllowing commands)
    """
    footer = []
    return footer
    
def Comm(x,labware,row,col,vol,liq):
    """
    Append a command into the worklist file
    Params --> x='A' for aspiarte or x='D' for dispense (char)
               labware = labware position tag on the robot table (string)
               row , col = well cordintates --> converted into 1..96 well position via (col-1)*8+row (int)
               vol = volume in ul  (int)
               liq = liquid class (string)
    """
    pos = (col)*8+row + 1
    return '%s;%s;;;%d;;%d;%s;;;' % (x,labware,pos,vol,liq)
    
def Tip():
    """
    Append a change tup command to worklist file
    """
    return 'W;'
    
def UserPrompt(msg):
    """
    Append a UserPrompt evoke command to the worklist file
    text will be displayed to evoware user while executing this worklist command
    """
    return 'B;UserPrompt("%s",0,10);' % (msg)

def MakeOpts():
    """Returns an OptionParser object with all the default options."""
    parser = ArgumentParser()

    parser.add_argument('worklist', nargs=1,
                        help='the path to the worklist that will be written')
    parser.add_argument('-o', '--host', dest='host', default='hldbv02',
                        help='the hostname for the MySQL database')
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help='debug mode, store results in dummy DB')
    parser.add_argument('-t', '--threshold', dest='threshold', default=0.2, type=float,
                        help='the OD threshold for dilution')
    parser.add_argument('-v', '--volume', dest='vol', default=15, type=int,
                        help='volume for diluation in ul')
    parser.add_argument('-l', '--liquid_class', dest='liquid_class', default='TurbidoClass',
                        help='liquid class to be used in pipetation')
    parser.add_argument('-r', '--reading_label', dest='reading_label', default='OD600',
                        help='the label of the measurements used for turbidity tracking')
    parser.add_argument('-p', '--plate', default=None, type=int, required=True,
                        help="The plate number (usually between 1-10) in the robot script")
    parser.add_argument('-x', '--exp', dest='exp_id_csv', default=None, required=True,
                        help='the name of the CVS file where the exp_ids are')
    parser.add_argument('-a', '--path', dest='path_csv', default=None, required=True,
                        help='the name of the CVS file where the dilution paths are')

    return parser

def ReadPathCsv(options):
    if not os.path.exists(options.path_csv):
        error("cannot find the CVS file with the experiment names: " + options.path_csv)

    path_dict = {}
    for row, line in enumerate(csv.reader(open(options.path_csv, 'r'))):
        for col, cell in enumerate(line):
            path_label, path_step = cell.split('__')
            path_step = int(path_step)
            path_dict.setdefault(path_label, {})
            path_dict[path_label][path_step] = (row, col)
            
    for path_label, d in path_dict.iteritems():
        path_dict[path_label] = [d[i] for i in sorted(d.keys())]

    return path_dict

def GetLastPlate(db, exp_id, plate_num, reading_label):
    max_time = None
    for res in db.Execute('SELECT time FROM tecan_readings WHERE exp_id="%s" AND reading_label="%s" AND plate=%d ORDER BY time DESC LIMIT 1'
                          % (exp_id, reading_label, plate_num)):
        max_time = res[0]
        break
    
    if max_time is None:
        print "Error in database"
        sys.exit(-1)

    print "Exp ID: %s, Plate: %d, Time: %d" % (exp_id, plate_num, max_time)
    return max_time

def GetMeasuredData(db, exp_id, time, plate, reading_label):
    data = np.zeros((8, 12))
    query = 'SELECT row, col, measurement FROM tecan_readings WHERE exp_id="%s" AND plate=%d AND time=%d AND reading_label="%s"' % (exp_id, plate, time, reading_label)
    print query
    for res in db.Execute(query):
        row, col, measurement = res
        data[row, col] = measurement
    return data
        
def GetPathSteps(db, exp_id, plate, time, path_dict):
    """
        returns a vector (length 12) of the current rows that should be
        checked for dilution. If they don't exist returns zeros.
    """

    res = db.Execute('SELECT COUNT(*) FROM evo_path_trajectory WHERE exp_id="%s" AND plate=%d'%  (exp_id, plate))
    if res[0][0] == 0:
        for path_label in path_dict.keys():
            db.Execute('INSERT INTO evo_path_trajectory(exp_id, plate, path_label, path_step, time, row_from, col_from, row_to, col_to)' + 
                       'VALUES ("%s", %d, "%s", %d, %d, %d, %d, %d, %d)' % (exp_id, plate, path_label, 0, time, None, None, 0, 0))

    path_step_dict = {}
   
    # if the exp_id doesn't exist this loop will not be skipped and the result
    # will be only 0s
    query = 'SELECT path_label, max(path_step) FROM evo_path_trajectory WHERE exp_id="%s" AND plate=%d GROUP BY path_label' % (exp_id, plate)
    print query
    for res in db.Execute(query):
        path_label, path_step = res
        path_step_dict[path_label] = path_step
    return path_step_dict

def IncrementRow(db, exp_id, plate, path_label, path_step, time, row, col, next_row, next_col):
    query = 'INSERT INTO evo_path_trajectory(exp_id, plate, path_label, path_step, time, row_from, col_from, row_to, col_to)' + \
            'VALUES ("%s", %d, "%s", %d, %d, %d, %d, %d, %d)' % (exp_id, plate, path_label, path_step, time, row, col, next_row, next_col)
    print query
    db.Execute(query)

def error(s):
    print s
    sys.exit(-1)

def main():

    options = MakeOpts().parse_args()
    path_dict = ReadPathCsv(options)
    
    VOL = options.vol
    MEDIA_VOL = 150-VOL #volune of fresh media in designated well
    
    LABWARE = 'GRID40SITE3' 
    EPNSTAND = 'EpnStand'
    
    LIQ = options.liquid_class
    
    # We should also state which directory where the evoware could find the worklist file

    db = MySQLDatabase(host=options.host, user='ronm', port=3306,
                       passwd='a1a1a1', db='tecan')
    
    exp_id_dict, plate_id = read_exp_id_csv(options.exp_id_csv)

    if options.plate not in exp_id_dict:
        error('The measured plate (%d) does not have an exp_id in the CSV file' % options.plate)

    exp_id = exp_id_dict[options.plate]

    max_time = GetLastPlate(db, exp_id, plate_id, options.reading_label)
    data = GetMeasuredData(db, exp_id, max_time, plate_id, options.reading_label)
    path_step_dict = GetPathSteps(db, exp_id, plate_id, max_time, path_dict)
    
    worklist = []
    for path_label, path_step in path_step_dict.iteritems():
        row, col = path_dict[path_label][path_step]
        meas = data[row, col]
        print path_label, path_step, col, row, meas
        if (meas > options.threshold) and (path_step < len(path_dict[path_label])-1):
            next_row, next_col = path_dict[path_label][path_step+1]
            msg = "Current plate is : %d ) %s __ OD = %f --> dilute cell %s%d into cell %s%d" % (options.plate, exp_id, meas, chr(ord('A') + row), col+1, chr(ord('A') + next_row), next_col+1)
            print msg
            worklist += [UserPrompt(msg)]
            worklist += [Comm('A',EPNSTAND,0,0,MEDIA_VOL,LIQ)]
            worklist += [Comm('D',LABWARE,next_row,next_col,MEDIA_VOL,LIQ)]
            worklist += [Comm('A',LABWARE,row,col,VOL,LIQ)]
            worklist += [Comm('D',LABWARE,next_row,next_col,VOL,LIQ)]
            #labware,volume and liquid_class would be hard coded for now ...
            worklist += [Tip()]
            IncrementRow(db, exp_id, plate_id, path_label, path_step+1, max_time, row, col, next_row, next_col)
    
    db.Commit()
    
    if len(worklist) == 0:
        sys.exit(0)
    
    worklist = Header() + worklist + Footer()
    f = open(options.worklist[0], 'w')
    f.write('\n'.join(worklist))
    f.close()
    print "Done!"
    sys.exit(1)
   
if __name__ == '__main__':
    main()
#    """SELECT e.path_label, e.path_step, t.row, t.col, max(t.measurement) w FROM evo_path_trajectory e, tecan_readings t
#        WHERE e.exp_id=t.exp_id AND t.exp_id="%s" AND e.plate=t.plate AND plate=%d AND t.reading_label="%s"
#              e.row_from=t.row AND e.col_from=t.col AND e.time < t.time
#     GROUP BY e.path_label, e.path_step, t.row, t.col
#     ORDER BY e.path_label, e.path_step """ % (exp_id, plate, reading_label)