from optparse import OptionParser
import sys
from toolbox.database import MySQLDatabase
import time
import csv

def MakeOpts():
    """Returns an OptionParser object with all the default options."""
    opt_parser = OptionParser()
    #opt_parser.add_option("-d", "--sqlite_db_filename",
    #                      dest="sqlite_db_filename",
    #                      default="../res/tecan.sqlite",
    #                      help="The filename of the Sqlite database")
    opt_parser.add_option("-p", "--plate_num",
                          type='int',
                          dest="plate_num",
                          default=None,
                          help="The number for the plate that is to be exported")
    opt_parser.add_option("-e", "--exp_id",
                          dest="exp_id",
                          default=None,
                          help="The expID for the data")
    opt_parser.add_option("-r", "--reading_label",
                          dest="reading_label",
                          default=None,
                          help="The Reading Label for the data")
    opt_parser.add_option("-c", "--csv",
                          action="store_true",
                          dest='csv',
                          default=False,
                          help="Format the output as CSV")
    opt_parser.add_option("-o", "--output_fname",
                          dest='output_fname',
                          default=None,
                          help="Filename for the output")
    return opt_parser

def main():
    opt_parser = MakeOpts()
    options, _ = opt_parser.parse_args(sys.argv)
    if not options.exp_id:
        opt_parser.print_help(sys.stderr)
        sys.exit(-1)

    #print "Importing into database: " + options.sqlite_db_filename
    sys.stderr.write("Experiment ID: %s\n" % options.exp_id)
    if options.plate_num is not None:
        sys.stderr.write("Plate num: %d\n" % options.plate_num)
    
    db = MySQLDatabase(host='hldbv02', user='ronm', 
                       passwd='a1a1a1', db='tecan')
    
    query = 'SELECT plate,reading_label,row,col,time,measurement ' + \
            'FROM tecan_readings WHERE exp_id="%s"' % options.exp_id
    if options.plate_num is not None:
        query += ' AND plate=%d' % options.plate_num
    if options.reading_label is not None:
        query += ' AND reading_label="%s"' % options.reading_label
        
    query += ' ORDER BY exp_id, plate, reading_label, row, col;'

    if options.output_fname is not None:
        f_out = open(options.output_fname, 'w')
    else:
        f_out = sys.stdout
    
    if options.csv:
        output = csv.writer(f_out)
        output.writerow(['plate', 'reading_label', 'row', 'col',
                         'time_in_sec', 'measurement'])
    else:
        output = f_out
    
    for row in db.Execute(query):
        plate, reading_label, row, col, time_in_sec, measurement = row
        if options.csv:
            output.writerow([plate, reading_label, row, col,
                             time_in_sec, measurement])
        else:
            t = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time_in_sec))
            output.write("(%d,%d) %s, %s : %.4f" % (row, col, reading_label, t, measurement))
    
    del db
    
if __name__ == '__main__':
    main()