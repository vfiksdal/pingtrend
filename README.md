# PingTrend
Simple GUI to ping one or more host and trend the response time. The data can be logged to disk in a simple CSV format and is plotted in realtime. Helpfull to track uptime and responsiveness of networked devices or simply your internet connectivity.

# Installation
First install a python3 distribution of your choice, winpython works well for windows users, linux/mac users can use what ships with their OS.
Then you need to install some dependencies:
>python -m pip install matplotlib ping3 netifaces

# Usage
To start the program:
>python pingtrend.py

![image](https://github.com/user-attachments/assets/edb15bd7-e74f-41f2-9b40-afe38cc75d3a)

After adding target domain names and setting the proper interval you can click start:

![image](https://github.com/user-attachments/assets/62e8cdca-a954-4279-bae2-42212b5e9dec)

