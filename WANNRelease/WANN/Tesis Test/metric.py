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

    max_elite = -1
    max_peak = -1
    
    for i,gen_data in enumerate(info_by_gen):
        e,b,p,m = 0,0,0,0
        for run in gen_data:
            if max_elite < run['elite']:
                max_elite = run['elite']
            if max_peak < run['peak']:
                max_peak = run['peak']
            e += run['elite']
            b += run['best']
            p += run['peak']
            m += run['median']

        gen.append(i)
        elite.append(e/len(gen_data))
        best.append(b/len(gen_data))
        peak.append(p/len(gen_data))
        median.append(m/len(gen_data))
    
    print(max_elite, max_peak)
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


def get_fitness_comparison(original_mean, modified_mean, output_dir, mean_name):
    max_fitness_original,max_fitness_modified = max(original_mean), max(modified_mean)
    last_fitness_original,last_fitness_modified = original_mean[-1], modified_mean[-1]

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    f = open(f'{output_dir}/comparison_{mean_name.lower()}.txt', 'w')
    f.write(f'Original Max\t\t {max_fitness_original}\n')
    f.write(f'Modified Max\t\t {max_fitness_modified}\n')
    f.write('\n\n')
    f.write(f'Original Last\t\t {last_fitness_original}\n')
    f.write(f'Modified Last\t\t {last_fitness_modified}\n')
    f.close()

def get_speed_comparison(original_mean, modified_mean, output_dir, mean_name):
    benchmarks = [200, 400, 600, 800]

    original_speed = {}
    modified_speed = {}

    for gen,fitness in enumerate(original_mean):
        for mark in benchmarks:
            if mark not in original_speed and fitness >= mark:
                original_speed[mark] = gen + 1
    
    for gen,fitness in enumerate(modified_mean):
        for mark in benchmarks:
            if mark not in modified_speed and fitness >= mark:
                modified_speed[mark] = gen + 1

    f = open(f'{output_dir}/speed_comparison_{mean_name.lower()}.txt', 'w')
    for mark in benchmarks:
        if mark in original_speed and mark in modified_speed:
            f.write(f'Original first gen reaching {mark} fitness\t\t: {original_speed[mark]}\n')
            f.write(f'Modified first gen reaching {mark} fitness\t\t: {modified_speed[mark]}\n')
            f.write('\n\n')

    f.close()

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
original_name = 'original'

all_original_means = _process_results(input_original_dir)
all_modified_means = _process_results(input_modified_dir)

plot_means(all_original_means, output_dir, original_name)
_plot_each_single_mean(all_original_means, output_dir, original_name)

plot_means(all_modified_means, output_dir, test_name)
_plot_each_single_mean(all_modified_means, output_dir, test_name)

# This is intended to use when I have the original WANN results vs the modified version
plot_single_mean_versus(all_original_means[1], all_modified_means[1], output_dir, 'Original Elite', 'Modified Elite', 'Elite')
plot_single_mean_versus(all_original_means[2], all_modified_means[2], output_dir, 'Original Best', 'Modified Best', 'Best')
plot_single_mean_versus(all_original_means[3], all_modified_means[3], output_dir, 'Original Peak', 'Modified Peak', 'Peak')
plot_single_mean_versus(all_original_means[4], all_modified_means[4], output_dir, 'Original Median', 'Modified Median', 'Median')

get_fitness_comparison(all_original_means[1], all_modified_means[1], output_dir, 'Elite')
get_fitness_comparison(all_original_means[2], all_modified_means[2], output_dir, 'Best')
get_fitness_comparison(all_original_means[3], all_modified_means[3], output_dir, 'Peak')
get_fitness_comparison(all_original_means[4], all_modified_means[4], output_dir, 'Median')

get_speed_comparison(all_original_means[1], all_modified_means[1], output_dir, 'Elite')
get_speed_comparison(all_original_means[2], all_modified_means[2], output_dir, 'Best')
get_speed_comparison(all_original_means[3], all_modified_means[3], output_dir, 'Peak')
get_speed_comparison(all_original_means[4], all_modified_means[4], output_dir, 'Median')