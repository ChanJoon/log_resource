#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# ------------------------------------------------------------------------------------------------------ #
# written by zinuok (https://github.com/zinuok)
# calculate CPU, memory usage of processes in proc_list. If you also want to log the GPU usage, 
# use jetson_stats/examples/resource_logger.py
# ref: https://thispointer.com/python-get-list-of-all-running-processes-and-sort-by-highest-memory-usage/
# ------------------------------------------------------------------------------------------------------ #

import psutil
import csv, argparse
from time import sleep

# variables
proc_list = ['rqt_image_view']   # process name list
interval = 0.1           # time interval for each logging



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--save', action="store", dest="file", default="log.csv")
    args = parser.parse_args()
    
    f = open(args.file, 'w')
    wr = csv.writer(f)
    wr.writerow(['CPU %', 'Mem %'])
    while True:
        total_cpu = 0
        total_mem = 0
        # Iterate over all running process
        for proc in psutil.process_iter():
            try:
                # Get process info.
                info = proc.as_dict(attrs=['name', 'cpu_percent', 'memory_percent'])
                if info['name'] in proc_list:
                    # calculate total CPU and Memory usage
                    total_cpu += info['cpu_percent']
                    total_mem += info['memory_percent']
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            except KeyboardInterrupt:
                print("Crtl+'C' interrupt")
                close(f)
        
        # log
        #print("cpu: ", total_cpu, "mem: ", total_mem)
        wr.writerow([total_cpu, total_mem])
        sleep(interval)     
    
    close(f)




if __name__ == '__main__':
   main()
