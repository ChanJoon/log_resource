# log_resource

***
This is python script logs CPU, Memory, and GPU usage for NVIDIA Jetson board. <br>
There are two files for logging the usages
+ **cpu_mem_logger.py:** total **CPU, Memory** usage for specified processes are logged
+ **jetson_stats/examples/resource_logger.py:** total **CPU, Memory, GPU** usage for specified processes are logged 

For second script, I modified and add a script 'resource_logger.py' from the original package from [jetson_stats]("https://github.com/rbonghi/jetson_stats")
***

## Install
```
$ pip install psutil
$ sudo -H pip install -U jetson-stats
$ git clone https://github.com/zinuok/log_resource.git
```

## Run
+ **'vo algorithm name' list:** vins-mono, vins-fusion, rovio, msckf-vio, orb2-ros
```
$ cd ~/jetson_stats/examples
$ python resource_logger.py --name [vo algorithm name] --save [output csv file name]
```

