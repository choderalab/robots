import sys
import numpy as np
from argparse import ArgumentParser
from toolbox.database import MySQLDatabase

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
    return 'B;UserPrompt("%s",1,-5);' % (msg)

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
    parser.add_argument("-p", "--num_plates", default=None, type=int, required=True,
                        help="The number of plates in the experiment")
    parser.add_argument("-i", "--iteration", default=None, type=int, required=True,
                        help="The iteration number in the robot script")
    parser.add_argument('-l', '--liquid_class', dest='liquid_class', default='TurbidoClass',
                        help='liquid class to be used in pipetation')
    parser.add_argument('-r', '--reading_label', dest='reading_label', default='OD600',
                        help='the label of the measurements used for turbidity tracking')
    parser.add_argument('-s', '--split_rows', dest='row_split', default=1, type=int,
                        help='by how much to split the plate''s rows to have more repetitions')
    return parser

def GetLastPlate(db, plate_num, reading_label):
    max_time = None
    for res in db.Execute('SELECT exp_id, time FROM tecan_readings WHERE reading_label="%s" AND plate=%d ORDER BY time DESC LIMIT 1'
                          % (reading_label, plate_num)):
        exp_id, max_time = res
        break
    
    if max_time is None:
        print "Error in database"
        sys.exit(-1)

    print "Exp ID: %s, Plate: %d, Time: %d" % (exp_id, plate_num, max_time)
    return exp_id, max_time

def GetMeasuredData(db, exp_id, time, plate, reading_label):
    data = np.zeros((8, 12))
    for res in db.Execute('SELECT row, col, measurement FROM tecan_readings WHERE exp_id="%s" AND plate=%d AND time=%d AND reading_label="%s"'
                          % (exp_id, plate, time, reading_label)):
        row, col, measurement = res
        data[row, col] = measurement
    return data
        
def GetDilutionRows(db, exp_id, plate, time, row_split):
    """
        returns a vector (length 12) of the current rows that should be
        checked for dilution. If they don't exist returns zeros.
    """

    res = db.Execute('SELECT COUNT(*) FROM exp_dilution_columns WHERE exp_id="%s" AND plate=%d'%  (exp_id, plate))
    if res[0][0] == 0:
        for i in xrange(row_split):
            for col in xrange(12):
                db.Execute('INSERT INTO exp_dilution_columns(exp_id, plate, col, row, time) VALUES ("%s", %d, %d, %d, %d)' %
                           (exp_id, plate, col, i * (8/row_split), time))

    dilution_rows = np.zeros((row_split, 12))
   
    # if the exp_id doesn't exist this loop will not be skipped and the result
    # will be only 0s
    print 'SELECT col, row FROM exp_dilution_columns WHERE exp_id="%s" AND plate=%d' % (exp_id, plate)
    for res in db.Execute('SELECT col, floor(row / %d) split, max(row) FROM exp_dilution_columns WHERE exp_id="%s" AND plate=%d GROUP BY col, split'
                          % (8/row_split, exp_id, plate)):
        col, split, row = res
        dilution_rows[split, col] = row
    return dilution_rows

def IncrementRow(db, exp_id, plate, col, row, time):
    db.Execute('INSERT INTO exp_dilution_columns(exp_id, plate, col, row, time)  VALUES ("%s", %d, %d, %d, %d)' %
               (exp_id, plate, col, row, time))

def main():

    options = MakeOpts().parse_args()
    VOL = options.vol
    LABWARE = 'GRID40SITE3' 
    LIQ = options.liquid_class
    
    # We should also state which directory where the evoware could find the worklist file

    db = MySQLDatabase(host=options.host, user='ronm', port=3306,
                       passwd='a1a1a1', db='tecan')
    
    plate_id = options.iteration % options.num_plates

    exp_id, max_time = GetLastPlate(db, plate_id, options.reading_label)
    data = GetMeasuredData(db, exp_id, max_time, plate_id, options.reading_label)
    dilution_rows = GetDilutionRows(db, exp_id, plate_id, max_time, options.row_split)
    print "dilution_rows:\n", dilution_rows
    
    worklist = []
    for split in xrange(dilution_rows.shape[0]):
        for col in xrange(dilution_rows.shape[1]):
            row = dilution_rows[split, col]
            meas = data[row, col]
            print col, row, meas
            if (meas > options.threshold) and ( (row+1) % (8/options.row_split) != 0 ):
                msg = "OD = %f --> dilute cell %s%d into cell %s%d" % (meas, chr(ord('A') + row), col+1, chr(ord('A') + row + 1), col+1)
                print msg
                worklist += [UserPrompt(msg)]
                worklist += [Comm('A',LABWARE,row,col,VOL,LIQ)]
                worklist += [Comm('D',LABWARE,row+1,col,VOL,LIQ)]
                #labware,volume and liquid_class would be hard coded for now ...
                worklist += [Tip()]
                IncrementRow(db, exp_id, plate_id, col, row+1, max_time)
    
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
