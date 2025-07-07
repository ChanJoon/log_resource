#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2025 Chanjoon Park
# Email: chanjoon.park@kaist.ac.kr
# Date: 2025-07-08
# Original Author: zinuok (https://github.com/zinuok)
# Added more features such as selecting processes to monitor, logging averages, and more.

# ------------------------------------------------------------------------------------------------------ #
# written by zinuok (https://github.com/zinuok)
# calculate CPU, memory usage of processes in proc_list. If you also want to log the GPU usage, 
# use jetson_stats/examples/resource_logger.py
# ref: https://thispointer.com/python-get-list-of-all-running-processes-and-sort-by-highest-memory-usage/
# ------------------------------------------------------------------------------------------------------ #

import psutil, subprocess, re, getpass
import csv, argparse
from time import sleep, time
from datetime import datetime

# Function to get the list of running processes
def get_user_processes():
    """현재 로그인한 사용자가 띄운 프로세스 이름 목록"""
    username = getpass.getuser()
    names = []
    for p in psutil.process_iter(['name', 'username']):
        if p.info['username'] == username:
            names.append(p.info['name'])
    return names

def get_ros1_processes():
    try:
        node_names = subprocess.check_output(['rosnode', 'list'], text=True).splitlines()
    except Exception:
        return []

    pnames = []
    for node in node_names:
        try:
            info = subprocess.check_output(['rosnode', 'info', node], text=True)
            m = re.search(r'Pid:\s*(\d+)', info)
            if m:
                pid = int(m.group(1))
                pnames.append(psutil.Process(pid).name())
        except Exception:
            pass  # rosnode info 실패, 프로세스 종료 등
    return pnames

def get_ros2_processes():
    try:
        node_names = subprocess.check_output(['ros2', 'node', 'list'], text=True).splitlines()
    except Exception:
        return []

    node_names = [n.lstrip('/') for n in node_names]
    pnames = []
    for p in psutil.process_iter(['name', 'cmdline']):
        try:
            cmd = ' '.join(p.info['cmdline'])
            for n in node_names:
                if n and (n == p.info['name'] or n in cmd):
                    pnames.append(p.info['name'])
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    print(f"ROS2 processes: {pnames}")
    return pnames

def get_ros_processes():
    return get_ros1_processes() + get_ros2_processes()

def get_docker_processes():
    docker_names = []
    for p in psutil.process_iter(['pid', 'name']):
        try:
            with open(f"/proc/{p.pid}/cgroup", "r") as cg:
                if 'docker' in cg.read():
                    docker_names.append(p.info['name'])
        except Exception:
            pass
    return list(set(docker_names))

def get_running_processes():
    proc_names = get_user_processes() + get_ros_processes() + get_docker_processes()
    return list(set(proc_names))

# Function to allow user to select processes to monitor
def select_processes_to_monitor():
    ros_procs = sorted(set(get_ros_processes()))
    docker_procs = sorted(set(get_docker_processes()))
    user_procs = sorted(set(get_user_processes()) - set(ros_procs) - set(docker_procs))

    combined_list = []
    print("\n" + "=" * 50)
    print(" " * 15 + "ROS PROCESSES" + " " * 15)
    print("=" * 50)
    for p in ros_procs:
        print(f"{len(combined_list)}: {p}")
        combined_list.append(p)

    print("\n" + "=" * 50)
    print(" " * 14 + "DOCKER PROCESSES" + " " * 14)
    print("=" * 50)
    for p in docker_procs:
        print(f"{len(combined_list)}: {p}")
        combined_list.append(p)

    print("\n" + "=" * 50)
    print(" " * 15 + "USER PROCESSES" + " " * 15)
    print("=" * 50)
    for p in user_procs:
        print(f"{len(combined_list)}: {p}")
        combined_list.append(p)

    selected_indices = input("Enter the indices of the processes you want to monitor (comma separated): ")
    selected_indices = [int(i.strip()) for i in selected_indices.split(',') if i.strip().isdigit() and int(i.strip()) < len(combined_list)]
    return [combined_list[i] for i in selected_indices]

# Update main function to use selected processes
proc_list = select_processes_to_monitor()  # Get user-selected processes

# variables
interval = 0.1           # time interval for each logging

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--save', action="store", dest="file", default="log.csv")
    args = parser.parse_args()
    
    f = open(args.file, 'w')
    wr = csv.writer(f)
    wr.writerow(['Timestamp', 'CPU %', 'Mem %', 'Avg CPU %', 'Avg Mem %'])
    start_time = time()
    last_time = start_time
    total_cpu_integral = 0.0  # percentage * seconds
    total_mem_integral = 0.0

    try:
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
                        print(f"Process: {info['name']}, CPU: {info['cpu_percent']}%, Mem: {info['memory_percent']}%")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

            # compute time-weighted averages
            now_time = time()
            delta_t = now_time - last_time
            total_cpu_integral += total_cpu * delta_t
            total_mem_integral += total_mem * delta_t
            elapsed = now_time - start_time
            avg_cpu = total_cpu_integral / elapsed if elapsed > 0 else 0.0
            avg_mem = total_mem_integral / elapsed if elapsed > 0 else 0.0
            last_time = now_time

            # log with timestamp and averages (with milliseconds)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            wr.writerow([timestamp, total_cpu, total_mem, avg_cpu, avg_mem])
            print(f"[{timestamp}] CPU: {total_cpu:.2f}%, Mem: {total_mem:.2f}%, Avg CPU: {avg_cpu:.2f}%, Avg Mem: {avg_mem:.2f}%")

    except KeyboardInterrupt:
        print("Ctrl+C interrupt detected. Calculating averages and closing file...")

    finally:
        elapsed_total = time() - start_time
        if elapsed_total > 0:
            avg_cpu = total_cpu_integral / elapsed_total
            avg_mem = total_mem_integral / elapsed_total
            
            wr.writerow(["FINAL", "", "", f"{avg_cpu:.2f}", f"{avg_mem:.2f}"])
            print("---------- [ RESULT ] ----------")
            print(f"Average CPU: {avg_cpu:.2f}%, Average Mem: {avg_mem:.2f}%")
            print("-------------------------------\n")
        else:
            print("No data collected to calculate averages.")

        f.close()

if __name__ == '__main__':
   main()
