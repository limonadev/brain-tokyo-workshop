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


def get_info_by_gen(results):
    gens = []
    for mapped in results:
        for i,gen_map in enumerate(mapped):
            if len(gens) == i:
                gens.append([])
            gens[i].append(gen_map)
    return gens


def get_all_mean(info_by_gen):
    gen,elite,best,peak,median = [],[],[],[],[]
    for i,gen_data in enumerate(info_by_gen):
        e,b,p,m = 0,0,0,0
        for run in gen_data:
            e += run['elite']

        gen.append(i)
        elite.append(e/len(gen_data))

    return gen,elite,best,peak,median


args = sys.argv[1:]

input_dirs = args[:-1]
output_dir = args[-1]

results = []

for folder in input_dirs:
    for subdir, dirs, files in os.walk(folder):
        if 'results.txt' in files:
            mapped = process_file(f'{subdir}/results.txt')
            results.append(mapped)

info_by_gen = get_info_by_gen(results)

all_mean = get_all_mean(info_by_gen)