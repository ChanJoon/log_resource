#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# ref: https://thispointer.com/python-get-list-of-all-running-processes-and-sort-by-highest-memory-usage/

from jtop import jtop, JtopException
import csv
import argparse
import psutil
from time import sleep


def main():
    while True:
        # Iterate over all running process
        for proc in psutil.process_iter():
            try:
                # Get process info.
                stats = jetson.stats
                info = proc.as_dict(attrs=['name', 'cpu_percent', 'memory_percent'])
                if info['name'] == "rqt_image_view":
                    print(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        sleep(0.1)


if __name__ == '__main__':
   main()
