import os
import sys
import matplotlib.pyplot as plt

def find_results(input_dir):
    results = []

    for folder in [input_dir]:
        for subdir, dirs, files in os.walk(folder):
            if 'results.txt' in files:
                mapped = process_file(f'{subdir}/results.txt')
                results.append(mapped)
    
    return results

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

    plt.plot(gen, elite, color='blue')
    plt.plot(gen, best, color='red')
    plt.plot(gen, peak, color='green')
    plt.plot(gen, median, color='orange')
    
    plt.xlabel('Generations')
    plt.ylabel('Fitness')
    plt.legend(['Elite', 'Best', 'Peak', 'Median'], loc='lower right')

    plt.savefig(f'{output_dir}/{test_name.lower()}_all.png')
    plt.clf()


def plot_single_mean(mean, output_dir, test_name, mean_name, color='blue'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.plot(mean, color=color)

    plt.xlabel('Generations')
    plt.ylabel('Fitness')
    plt.legend([mean_name], loc='lower right')

    plt.savefig(f'{output_dir}/{test_name.lower()}_{mean_name.lower()}.png')
    plt.clf()


def plot_single_mean_versus(mean_a, mean_b, output_dir, mean_id_a, mean_id_b, mean_name):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.plot(mean_a)
    plt.plot(mean_b)

    plt.xlabel('Generations')
    plt.ylabel('Fitness')
    plt.legend([mean_id_a, mean_id_b], loc='lower right')

    plt.savefig(f'{output_dir}/versus_{mean_name.lower()}.png')
    plt.clf()


def _process_results(input_dir):
    results = find_results(input_dir)
    info_by_gen = get_info_by_gen(results)
    all_means = get_all_means(info_by_gen)
    return all_means

def _plot_each_single_mean(means, output_dir, test_name):
    plot_single_mean(means[1], output_dir, test_name, 'Elite', color='blue')
    plot_single_mean(means[2], output_dir, test_name, 'Best', color='red')
    plot_single_mean(means[3], output_dir, test_name, 'Peak', color='green')
    plot_single_mean(means[4], output_dir, test_name, 'Median', color='orange')

args = sys.argv[1:]

input_original_dir = args[0]
input_modified_dir = args[1]
output_dir = args[2]
test_name = args[3]

all_modified_means = _process_results(input_modified_dir)

plot_means(all_modified_means, output_dir, test_name)
_plot_each_single_mean(all_modified_means, output_dir, test_name)

# This is intended to use when I have the original WANN results vs the modified version
plot_single_mean_versus(all_modified_means[1], all_modified_means[2], output_dir, 'Modified Elite', 'Original Elite', 'Elite')