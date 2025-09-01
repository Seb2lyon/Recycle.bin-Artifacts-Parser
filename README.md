# Recycle.bin-Artifacts-Parser
## Post-mortem Windows forensics script - Analysis of the Recycle.bin artifacts ($I files)

### <ins>Usage examples:</ins>

+ Display the content of a single $I file
```python 
python Recycle.bin_Parser.py -i $I123456
```
+ Display the content of all $I files inside a Folder
```python
python Recycle.bin_Parser.py -i Folder
```
+ Save the results in a CSV file (no Console output)
```python
python Recycle.bin_Parser.py -i Folder -o output.csv
```
+ Save the results in a CSV file with Console output
```python
python Recycle.bin_Parser.py -i Folder -o output.csv -v
```
### <ins>Show Help Page</ins>
```python
python Recycle.bin_Parser.py -h
```
\
*Version 2025.09 - Developed by Seb2lyon*
