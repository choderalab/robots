import sys, csv, os
from argparse import ArgumentParser

def MakeOpts():
    """Returns an OptionParser object with all the default options."""
    parser = ArgumentParser()

    parser.add_argument('exp_id_csv', nargs=1,
                        help='the name of the CVS file where the exp_ids are')
    parser.add_argument("-p", "--plate", default=None, type=int, required=True,
                        help="The plate number (usually between 1-10) in the robot script")

    return parser

def error(s):
    print s
    sys.exit(-1)
    
def read_exp_id_csv(exp_id_csv):
    if not os.path.exists(exp_id_csv):
        error("cannot find the CVS file with the experiment names: " + exp_id_csv)

    exp_id_dict = {}
    for d in csv.DictReader(open(exp_id_csv, 'r')):
        try:
            exp_id = d['exp_id']
        except KeyError:
            error('There is no column titled "exp_id" in the CSV file')
        
        try:
            plate = int(d['plate'])
        except KeyError:
            error('There is no column titled "plate" in the CSV file')
        except ValueError:
            error('The value of "plate" is not an integer: ' + d['plate'])
        
        if plate in exp_id_dict:
            error('The plate number %d appears twice in the CSV file' % plate)
        if exp_id != "":
            exp_id_dict[plate] = exp_id
    return exp_id_dict, 0

def main():
    options = MakeOpts().parse_args()
    
    exp_id_dict, plate_id = read_exp_id_csv(options.exp_id_csv[0])
            
    if len(set(exp_id_dict.values())) < len(exp_id_dict.values()):
        error('One of the exp_ids appears twice in the CSV file')

    if options.plate in exp_id_dict:
        # in case the plate matches the input argument and the exp_id
        # is not an empty string, return 0 to indicate that this plate
        # should be measured
        print "Measure plate %d with exp_id = '%s'" % (options.plate, exp_id_dict[options.plate])
        sys.exit(0)
    else:
        # if none of the lines in the CSV file match the plate number or the
        # ones that do have empty strings as exp_id, return 1 to indicate that
        # the robot should not measure this plate
        print "Don't do anything"
        sys.exit(1)
    
if __name__ == '__main__':
    main()
    