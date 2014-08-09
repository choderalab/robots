import string
import os
import csv
import sys
import re


# the input file is the same type of file as the csv2gwl cherry picking file.
def checkFile(argv):
	if len(argv) == 2:

		csv_file = argv[1]

		try:
			f = open(argv[1],"r")
			f.close

			return csv_file

		except IOError:
			print
			print "Looks like that file doesn't exist!"
			print
			sys.exit(1)

	
	else:
		while True:

			csv_file = raw_input("Enter the path to your file: ")

			if os.path.isfile(csv_file) == True:
				return csv_file
			else:
				
				csv_file = os.path.realpath(csv_file.strip())

				if os.path.isfile(csv_file) == True:
					return csv_file
				else:
					print
					print "Sorry that wasn't a file! Try again :-)"

def convertCSV(csv_file,gwl_file):
	w = csv.reader(open(csv_file, "rU"))

	prevExperimentNumber = ""
	primerSets = 0
	destinationWellCount = 0
	destinationPlateCount = 0

	for row in w:

		destination = row[0]

		# search for the A00 patterna and grab everthing before it.
		# Some of Adeline's CSV's have a different format. With missing row[1]'s. This will catch that.
		try:
			experiment = re.search("\w+(?=[A-Z][0-9][0-9])",row[1])
			experiment = experiment.group(0)
		except AttributeError:
			continue

		source = re.search("[A-Z][0-9][0-9]",row[1])
		source = source.group(0)
		
		# increment the plate number if the experiment number changes
		if experiment != prevExperimentNumber:
			prevExperimentNumber = experiment
			primerSets += 1

		# increment destination plate every 96 dispenses
		if destinationWellCount % 96 == 0:
			destinationPlateCount += 1

		destinationWellCount	+= 1
		
		convertToGWL(destination,primerSets,source,destinationPlateCount,gwl_file)


	return primerSets, destinationPlateCount

def convertToGWL(destination,primerSets,source,destinationPlateCount,gwl_file):

	destination = microplate2evoware(destination)
	source      = microplate2evoware(source)

	plateTypeForwardPrimer = "50ul - 96 Nunc V-Bottom"
	plateTypeReversePrimer = "50ul - 96 Nunc V-Bottom" 
	plateTypeTDNA = "50ul - 96 DeepWell Frosted Small"
	plateTypeWT   = "50ul - 96 DeepWell Frosted Small"

	plateNameForwardPrimer = "F " + str(primerSets)
	plateNameReversePrimer = "R " + str(primerSets)

	plateNameTDNA = "TDNA " + str(destinationPlateCount)
	plateNameWT   = "WT " + str(destinationPlateCount)

	volumeDispense = "2.7"

	# forward primer
	aspirateForward     = "".join(["A;",plateNameForwardPrimer,";;",plateTypeForwardPrimer,";",str(source),";;",volumeDispense,";;;\n"])
	dispenseForwardWT   = "".join(["D;",plateNameWT,";;",plateTypeWT,";",str(destination),";;",volumeDispense,";;;\nW;\n"])
	dispenseForwardTDNA = "".join(["D;",plateNameTDNA,";;",plateTypeTDNA,";",str(destination),";;",volumeDispense,";;;\nW;\n"])

	# reverse primer
	aspirateReverse     = "".join(["A;",plateNameReversePrimer,";;",plateTypeReversePrimer,";",str(source),";;",volumeDispense,";;;\n"])
	dispenseReverseWT   = "".join(["D;",plateNameWT,";;",plateTypeWT,";",str(destination),";;",volumeDispense,";;;\nW;\n"])


	# write forward primer sequence
	gwl_file.write(aspirateForward)
	gwl_file.write(dispenseForwardWT)
	gwl_file.write(aspirateForward)
	gwl_file.write(dispenseForwardTDNA)

	# write reverse primer sequence
	gwl_file.write(aspirateReverse)
	gwl_file.write(dispenseReverseWT)

def microplate2evoware(microplate_well):
	# this is a dictionary that allows any A01 formatted well to be converted into a linear, 96 well scheme that the EVOware expects.
	# the formula is: [Some Letter][Some number between 1 and 12] --> (8 x (Some Number - 1)) + (Value of the letter ie A = 1, B = 2 ...)

	microplate2Evoware = {"A":1,"a":1,"B":2,"b":2,"C":3,"c":3,"D":4,"d":4,"E":5,"e":5,"F":6,"f":6,"G":7,"g":7,"H":8,"h":8}

	destination        = ( 8 * ( int(microplate_well[1:]) - 1) + microplate2Evoware[microplate_well[0]])

	return destination

def main(argv):
	csv_file = checkFile(argv)

	directory, newFileNameWithExtension = os.path.split(argv[1])
	gwl_file_name, extension              = os.path.splitext(newFileNameWithExtension)

	gwl_file_name += "-PCRPlateMaker.gwl"

	gwl_file = open(gwl_file_name,"w")

	primerSets,destinationPlateCount = convertCSV(csv_file,gwl_file)

	gwl_file.close()

	print
	print "All Done :-]"
	print
	print "You have " + str(primerSets) + " Forward and Reverse Primer set(s)"
	print
	print "You have " + str(destinationPlateCount) + " TDNA and WT set(s)"
	print

if __name__ == "__main__":
	main(sys.argv)