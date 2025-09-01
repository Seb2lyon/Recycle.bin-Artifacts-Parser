# Recycle.bin-Artifacts-Parser
Post-mortem Windows forensics script - Analysis of the Recycle.bin artifacts ($I files)

Usage examples :
python Recycle.bin_parser.py -i $I123456                   Display the content of a single $I file
python Recycle.bin_parser.py -i Folder                     Display the content of all $I files inside a Folder
python Recycle.bin_parser.py -i Folder -o output.csv       Save the results in a CSV file (no Console output)
python Recycle.bin_parser.py -i Folder -o output.csv -v    Save the results in a CSV file with Console output

Version 2025.09 - Developed by Seb2lyon
