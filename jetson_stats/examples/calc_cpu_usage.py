#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import csv, argparse
import numpy as np



def data_stat(data, name='default'):
    # calculate statistics
    mean = np.mean(data)
    std = np.std(data)
    max_val = np.max(data)
    min_val = np.min(data)
    
    print('-'*20)
    print(f"Statistics for {name}")
    print(f"Mean: {mean}")
    print(f"Std: {std}")
    print(f"Max: {max_val}")
    print(f"Min: {min_val}")
    print('-'*20)


if __name__ == "__main__":
    # parse output file name
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_csv', type=str, default="")

    args = parser.parse_args()
    
    # read csv file as numpy (skip header)
    data = np.genfromtxt(args.input_csv, delimiter=',', skip_header=1)
    
    # cpu
    data_cpu = data[:, 0]
    
    # memory 
    data_mem = data[:, 1]

    # print statistics    
    data_stat(data_cpu, 'cpu')
    data_stat(data_mem, 'mem')
    
