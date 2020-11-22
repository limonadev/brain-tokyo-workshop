import os
import sys

def process_file(filename):
    f = open(filename, 'r')

    trash = ['-','|---|','Fit:','Elite','Best','Peak','Median']

    mapped = []
    
    for line in f.readlines():
        parts = line.split()
        parts = [p for p in parts if p not in trash]
        parts = [int(p) if '.' not in p else float(p) for p in parts]

        gen,elite,best,peak,median = parts

        mapped.append({'elite':elite,'best':best,'peak':peak,'median':median})

    f.close()

    return mapped


args = sys.argv[1:]

input_dirs = args[:-1]
output_dir = args[-1]

results = []

for folder in input_dirs:
    for subdir, dirs, files in os.walk(folder):
        if 'results.txt' in files:
            mapped = process_file(f'{subdir}/results.txt')

            results.append(mapped)
            
        #if filename == 'results.txt':
        #    print('nani')