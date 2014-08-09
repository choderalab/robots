from argparse import ArgumentParser
import time, sys, os
from database import MySQLDatabase, SqliteDatabase
from victor_parser import VictorParser

def MakeOpts():
    """Returns an OptionParser object with all the default options."""
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true',
                        help='debug mode, store results in dummy DB')
    parser.add_argument("-o", "--host", dest="host", default="hldbv02",
                        help="The hostname for the MySQL database")
    parser.add_argument('-e', '--exp_id', default=None,
                        help='Override the experiment ID '
                             '(default is to use the measurement date-time)')
    parser.add_argument('xls_file', help='The path to the XLS file containing Victor results')
    return parser

def CreateDummyDB():
    db = SqliteDatabase('/tmp/dummy.sqlite', 'w')
    db.CreateTable('tecan_readings',
                   'exp_id TEXT, plate TEXT, reading_label TEXT, row INT, col INT, time INT, measurement REAL',
                   drop_if_exists=False)
    db.CreateTable('tecan_labels',
                   'exp_id TEXT, plate INT, row INT, col INT, label TEXT',
                   drop_if_exists=False)
    db.CreateTable('tecan_plates',
                   'exp_id TEXT, plate INT, description TEXT, owner TEXT, project TEXT',
                   drop_if_exists=False)
    db.CreateTable('tecan_experiments',
                   'exp_id TEXT, serial_number TEXT, desciption TEXT',
                   drop_if_exists=False)
    db.CreateTable('tecan_scripts',
                   'exp_id TEXT, script BLOB',
                   drop_if_exists=False)
    return db

def main():
    """
        Imports an XLS file of Victor exported results.
        The Experiment ID is determined by the time-stamp of the first measurement.
    """
    
    options = MakeOpts().parse_args()

    if options.debug:
        db = CreateDummyDB()
    else:
        db = MySQLDatabase(host=options.host, user='ronm', port=3306,
                           passwd='a1a1a1', db='tecan')

    if not os.path.exists(options.xls_file):
        print "File not found: " + options.xls_file
        sys.exit(-1)
    
    print "Importing from file: " + options.xls_file
    fp = open(options.xls_file, 'r')
    exp_id = VictorParser.ImportFileToDB(fp, db, options.exp_id)
    if options.debug:
        print "Done, go check out the results at %s" % db.filename
    else:
        print "Done, go check out the results at http://eladpc1/RoboSite/Exp/%s/0" % exp_id
    
if __name__ == '__main__':
    main()
