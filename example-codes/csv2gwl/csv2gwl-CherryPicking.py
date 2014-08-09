import string
import os
import csv
import sys
import re

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

def convertCSV(csv_file,gwl_file,dnaType):

	w = csv.reader(open(csv_file, "rU"))

	# aspirate count

	aspirate_plate_number = 0
	prev_experiment_number = ""
	dispense_count = 0
	destination_plate_number = 0

	for row in w:

		destination = row[0]

		# since it is really not known how long the experiment names (really just numbers) are going to be, we can't count on the source well to always be in the same position
		# this is why a regular expression will be used. the well format will always be in a [A-Z][0-9][0-9] format. re.search returns an object where .group(0) shows all the text that conforms to the regular expression
		try:
			match = re.search("([A-Z]|[a-z])[0-9][0-9]",row[1])
			source = match.group(0)
		except AttributeError:
			continue

		# search for the A00 patterna and grab everthing before it.
		try:
			experiment = re.search("\w+(?=[A-Z][0-9][0-9])",row[1])
			experiment = experiment.group(0)
		except AttributeError:
			continue

		
		# increment the plate number if the experiment number changes
		if experiment != prev_experiment_number:
			prev_experiment_number = experiment
			aspirate_plate_number += 1


		# increment destination plate every 96 dispenses
		if dispense_count % 96 == 0:
			destination_plate_number += 1

		dispense_count	+= 1


		convertToGWL(source,destination,gwl_file,aspirate_plate_number,destination_plate_number,dnaType)

	return aspirate_plate_number,destination_plate_number

def convertToGWL(source,destination,gwl_file,aspirate_plate_number,destination_plate_number,dnaType):



	plateLabelAspirate = dnaType +" "
	plateLabelAspirate += str(aspirate_plate_number)
	plateTypeAspirate = "50ul - 96 PCR Plate" 
	volumeAspirate = 20
	
	plateLabelDispense = dnaType + " " + "Final" + " "
	plateLabelDispense += str(destination_plate_number)
	plateTypeDispense = "50ul - 96 Nunc V-Bottom" 
	volumeDispense = 20


	# this is a dictionary that allows any A01 formatted well to be converted into a linear, 96 well scheme that the EVOware expects.
	# the formula is: [Some Letter][Some number between 1 and 12] --> (8 x (Some Number - 1)) + (Value of the letter ie A = 1, B = 2 ...)
	microplate2Evoware = {"A":1,"a":1,"B":2,"b":2,"C":3,"c":3,"D":4,"d":4,"E":5,"e":5,"F":6,"f":6,"G":7,"g":7,"H":8,"h":8}

	evowareSource      = ( 8 * ( int(source[1:]) - 1) + microplate2Evoware[source[0]])
	evowareDestination = ( 8 * ( int(destination[1:]) - 1) + microplate2Evoware[destination[0]])


	aspirate = "".join(["A;",plateLabelAspirate,";;",plateTypeAspirate,";",str(evowareSource),";;",str(volumeAspirate),";;;\n"])
	dispense = "".join(["D;",plateLabelDispense,";;",plateTypeDispense,";",str(evowareDestination),";;",str(volumeDispense),";;;\nW;\n"])

	gwl_file.write(aspirate)
	gwl_file.write(dispense)

def finished(argv,aspirate_plate_number_TDNA,destination_plate_number_TDNA):
	print
	print "All done :-]"
	print 
	print "You have " + str(aspirate_plate_number_TDNA) + " source plates"
	print
	print "You have " + str(destination_plate_number_TDNA) + " destination plates"
	print

	if len(argv) == 1:
		print "Did you know you can just give the script the file or path to the file?"
		print "Try this next time:"
		print "python csv2gwl.py <file name or path to file>"
		print

def main(argv):

	csv_file = checkFile(argv)

	directory, newFileNameWithExtension = os.path.split(argv[1])
	newFileName, extension              = os.path.splitext(newFileNameWithExtension)

	TDNA = newFileName + "-TDNA-Worklist.gwl"
	WT   = newFileName + "-WT-Worklist.gwl"

	gwl_TDNA_file = open(TDNA,"w")
	gwl_WT_file = open(WT,"w")

	aspirate_plate_number_TDNA,destination_plate_number_TDNA = convertCSV(csv_file,gwl_TDNA_file,"TDNA")
	aspirate_plate_number_WT, destination_plate_number_WT = convertCSV(csv_file,gwl_WT_file,"WT")

	gwl_TDNA_file.close()
	gwl_WT_file.close()

	finished(argv,aspirate_plate_number_TDNA,destination_plate_number_TDNA)

if __name__ == "__main__":
	main(sys.argv)



