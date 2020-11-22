import os
import sys
import matplotlib.pyplot as plt

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


def get_all_means(info_by_gen):
    gen,elite,best,peak,median = [],[],[],[],[]
    for i,gen_data in enumerate(info_by_gen):
        e,b,p,m = 0,0,0,0
        for run in gen_data:
            e += run['elite']
            b += run['best']
            p += run['peak']
            m += run['median']

        gen.append(i)
        elite.append(e/len(gen_data))
        best.append(b/len(gen_data))
        peak.append(p/len(gen_data))
        median.append(m/len(gen_data))

    return [gen,elite,best,peak,median]

def plot_means(all_means, output_dir, test_name):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    gen,elite,best,peak,median = all_means

    plt.plot(gen, elite)
    plt.plot(gen, best)
    plt.plot(gen, peak)
    plt.plot(gen, median)
    
    plt.xlabel('Generations')
    plt.ylabel('Fitness')
    plt.legend(['Elite', 'Best', 'Peak', 'Median'], loc='lower right')

    plt.savefig(f'{output_dir}/{test_name}_all.png')
    #plt.show()


args = sys.argv[1:]

input_dirs = args[:-2]
output_dir = args[-2]
test_name = args[-1]

results = []

for folder in input_dirs:
    for subdir, dirs, files in os.walk(folder):
        if 'results.txt' in files:
            mapped = process_file(f'{subdir}/results.txt')
            results.append(mapped)

info_by_gen = get_info_by_gen(results)

all_means = get_all_means(info_by_gen)

plot_means(all_means, output_dir, test_name)