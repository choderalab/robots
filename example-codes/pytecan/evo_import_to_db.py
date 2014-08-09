from argparse import ArgumentParser
import toolbox.tecan as tecan
import sys, os
from toolbox.database import MySQLDatabase, SqliteDatabase
import time
from pytecan.evo_is_active import read_exp_id_csv

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

def MakeOpts():
    """Returns an OptionParser object with all the default options."""
    parser = ArgumentParser()

    parser.add_argument("-o", "--host", dest="host", default="hldbv02",
                        help="The hostname for the MySQL database")
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help='debug mode, store results in dummy DB')
    
    xml_group = parser.add_mutually_exclusive_group(required=True)
    xml_group.add_argument("-x", "--xml_filename", default=None,
                           help="The filename for a single XML result file")
    xml_group.add_argument("-a", "--xml_dir", default=None,
                           help="The directory from which to import the latest XML results file")
    
    parser.add_argument("-p", "--plate", default=None, type=int, required=True,
                        help="The plate number (usually between 1-10) in the robot script")
    parser.add_argument('exp_id_csv', nargs=1,
                        help='the name of the CVS file where the exp_ids are')

    return parser

def GetTimeString():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

def GetLatestFile(path):
    filelist = [os.path.join(path, x) for x in os.listdir(path)]
    filelist = filter(lambda x: not os.path.isdir(x), filelist)
    return max(filelist, key=lambda x: os.stat(x).st_mtime)

def GetExperimentID(options, db, header_dom, script_dom):
    if options.exp_id is not None:
        return options.exp_id

    serial_number = tecan.GetSerialNumber(header_dom)
    if options.iteration == 0:
        exp_id = GetTimeString()
        db.Insert('tecan_experiments', [exp_id, serial_number, "Automatically generated"])
        db.Insert('tecan_scripts', [exp_id, script_dom.toxml()])
        print "Generating Experiment ID: " + exp_id
        return exp_id

    exp_id = tecan.GetCurrentExperimentID(db, serial_number)
    if exp_id is None:
        raise Exception("There are no experiments in the database yet")
    return exp_id

def error(s):
    print s
    sys.exit(-1)
    
def main():
    options = MakeOpts().parse_args()

    if options.debug:
        db = CreateDummyDB()
    else:
        db = MySQLDatabase(host=options.host, user='ronm', port=3306,
                           passwd='a1a1a1', db='tecan')
    
    if options.xml_dir:
        if not os.path.exists(options.xml_dir):
            error("Directory not found: " + options.xml_dir)
        xml_fname = GetLatestFile(options.xml_dir)
    else:
        xml_fname = options.xml_filename

    if not os.path.exists(xml_fname):
        error("File not found: " + xml_fname)
    
    print "Importing from file: " + xml_fname
    header_dom, script_dom, plate_values = tecan.ParseReaderFile(xml_fname)

    exp_id_dict, plate_id = read_exp_id_csv(options.exp_id_csv[0])
    
    if options.plate not in exp_id_dict:
        error('The measured plate (%d) does not have an exp_id in the CSV file' % options.plate)

    exp_id = exp_id_dict[options.plate]
    MES = {plate_id: plate_values}
    tecan.WriteToDatabase(MES, db, exp_id)
    db.Commit()
    print "Done!"
    sys.exit(0)
   
if __name__ == '__main__':
    main()
