import argparse
import os
import sys
import datetime
import csv


def main(input_path, output_path, verbose):

	# PROCESSING INPUT FILE / DIRECTORY

	# Create a list of $I files to parse
	files_to_parse = []

	path = os.path.abspath(input_path)
	
	# If the input is a single file
	if os.path.isfile(path):
		print("[+] Check the input file '{}', to confirm it is a $I file".format(input_path))

		# Check if the file is a $I file
		if is_siFile(path):
			print("[+] The input file '{}' is a $I file".format(input_path))

			# If it is a $I file, add it's path to the list of $I files to parse
			files_to_parse.append(path)
		else:

			# If it is not a $I file, exit the script 
			print("[-] The input file '{}' is not a $I file".format(input_path))
			sys.exit(2)

	# If the input is a directory
	elif os.path.isdir(path):
		print("[+] Start to scan the input directory '{}', to find $I files".format(input_path))

		# Walk along all the directory to get all the files
		for root, directory, files in os.walk(path):

			# For each files...
			for file in files:
				file_path = os.path.join(root, file)

				# Check if the file is a $I file
				if is_siFile(file_path):

					# If it is a $I file, add it's path to the list of $I files to parse
					files_to_parse.append(file_path)

	# End of processing input file or directory
	# Print the number of confirmed $I files to parse
	files_nb = len(files_to_parse)

	if files_nb == 0:
		print("[-] There is no $I file available in the input directory '{}'".format(input_path))
		sys.exit(3)

	else:
		print("[+] $I files to parse : {}".format(files_nb))


	# PROCESSING PARSING FILES

	# Create a list of dictionaries (1 dictionary per file)
	# Key = File path / Values = "$I File", "Original Size", "Deleted Timestamp", "Original Name"
	parsed_files = []

	for file in files_to_parse:
		parsed_file = parsing_file(file)
		parsed_files.append(parsed_file)


	# PROCESSING OUTPUT

	# Manage the Console and CSV output, regarding the activated options
	if output_path is None:
		console_output(parsed_files)
	elif verbose is True:
		console_output(parsed_files)
		csv_output(parsed_files, output_path)
	else:
		csv_output(parsed_files, output_path)

	print("[+] Process ended succesfully")


def is_siFile (filePath):

	file_name = os.path.split(filePath)[1]
	file_name_without_ext = file_name.split(".")
	
	# Check if the name start with "$I" and is 8 caracter's long (without extention)
	if file_name[:2] == "$I" and len(file_name_without_ext[0]) == 8:

		# Open the file in binary mode
		with open(filePath, "rb") as file:
			binary_file = file.read()

		# Convert the file content in an array
		hex_file = bytearray(binary_file)

		# Get the header (8 first Bytes)
		header = hex_file[:8]

		# Convert the header in little endian
		header.reverse()

		# Check if the header is a $I file's header
		if header.hex() == "0000000000000002":
			return True
		else:
			return False
	
	else:
		return False


def parsing_file(filePath):

	parsed_file = {}

	parsed_file["$I File"] = os.path.split(filePath)[1]

	# Open the file in binary mode
	with open(filePath, "rb") as file:
		binary_file = file.read()

	# Convert the file content in an array
	hex_file = bytearray(binary_file)

	# Get the File Size (Offset 8 - Size 8 Bytes) in little endian
	hex_file_size = hex_file[8:16]
	hex_file_size.reverse()

	parsed_file["Original Size"] = int(hex_file_size.hex(), 16)

	# Get the Deleted Timstamp (Offset 16 - Size 8 Bytes) in little endian
	hex_deleted_timestamp = hex_file[16:24]
	hex_deleted_timestamp.reverse()

	int_deleted_timestamp = int(hex_deleted_timestamp.hex(), 16)

	parsed_file["Deleted Timestamp"] = convertTimestamp(int_deleted_timestamp)

	# Get the File Name Length (Offset 24 - Size 4 Bytes) in little endian
	hex_file_name_length = hex_file[24:28]
	hex_file_name_length.reverse()

	int_file_name_length = int(hex_file_name_length.hex(), 16)

	# Get the hex File Name (length = File Name Length x 2)
	hex_file_name = bytearray(hex_file[28:28 + (int_file_name_length * 2)])

	# Skip every 2 Bytes (= 00) and convert the hex File Name in ASCII 
	file_name_char_list = []

	for count, char in enumerate(hex_file_name):
		if count % 2 == 0:
			file_name_char_list.append(chr(char))

	parsed_file["Original Name"] = "".join(file_name_char_list)

	return parsed_file


def convertTimestamp(int_timestamp):
	unix_timestamp = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc).timestamp()
	win_timestamp = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc).timestamp()

	win_to_unix = unix_timestamp - win_timestamp

	hum_date = datetime.datetime.fromtimestamp((int_timestamp * 0.0000001) - win_to_unix)

	return hum_date.strftime("%d/%m/%Y %H:%M:%S")


def console_output(filesDict):
	print("[+] Result of the parsing : \n-------------------------------------------")
	for count, file in enumerate(filesDict):
		print("$I File #{}".format(count+1))
		print("$I File Name : \t\t{}".format(file["$I File"]))
		print("Original File Name : \t{}".format(file["Original Name"]))
		print("Original File Size : \t{} Bytes".format(file["Original Size"]))
		print("Deleted Timestamp : \t{}".format(file["Deleted Timestamp"]))
		print("-------------------------------------------")

def csv_output(filesDict, csv_output):
	header = ["$I File", "Original Name", "Original Size", "Deleted Timestamp"]
	with open(csv_output, "w", newline="") as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=header, escapechar="\n")

		writer.writeheader()
		writer.writerows(filesDict)

	print("[+] Results are recorded in {} file".format(csv_output))



if __name__ == "__main__":

	epilog = '''
Usage examples :
python Recycle.bin_parser.py -i $I123456                   Display the content of a single $I file
python Recycle.bin_parser.py -i Folder                     Display the content of all $I files inside a Folder
python Recycle.bin_parser.py -i Folder -o output.csv       Save the results in a CSV file (no Console output)
python Recycle.bin_parser.py -i Folder -o output.csv -v    Save the results in a CSV file with Console output

Version 2025.09 - Developed by Seb2lyon'''

	description = '''
Description :
Post-mortem Windows forensics script
Analysis of the Recycle.bin artifacts ($I files)'''

	parser = argparse.ArgumentParser(prog="Recycle.bin Artifacts Parser", formatter_class=argparse.RawTextHelpFormatter, description=description, epilog=epilog)

	parser.add_argument("-i", "--input", help="single $I file or folder containing $I files", required=True)
	parser.add_argument("-o", "--output", help="CSV file to save the results in")
	parser.add_argument("-v", "--verbose", help="Activate the verbose mode", action="store_true")

	args = parser.parse_args()

	# Check the input and output
	in_dir_path = os.path.abspath(args.input)
	
	# Check if the input file or folder exists
	if os.path.exists(in_dir_path):

		# Check if the output path exists
		if args.output is not None:
			out_dir_path = os.path.abspath(args.output)
			out_dir_name = os.path.dirname(out_dir_path)

			# If the output path does not exists, create it
			if not os.path.exists(out_dir_name) or not os.path.isdir(out_dir_name):
				os.makedirs(out_dir_name)

		# If the input file or folder exists AND the output path exists, continue with the main function
		main(args.input, args.output, args.verbose)
				

	# If the input file or folder does not exists, exit the script
	else:
		print("[-] The input file or folder does not exists")
		sys.exit(1)
