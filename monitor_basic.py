#!/usr/bin/env python

# System Monitor & Recorder
# Usage: system_monitory.py <output_file>

import psutil
import sys
import thread
from datetime import datetime


def input_thread(l):
    raw_input()
    l.append(None)


def main(output_file):
    out = open(output_file, 'a')
    key = ["Timestamp", "CPU_Percent", "Per_CPU_Percent", "Memory_Percent", "Disk_Percent"]
    out.write('\t'.join(key) + '\n')
    # Start exit monitor thread.
    l = []
    thread.start_new_thread(input_thread, (l,))
    # Monitory system & write report until break.
    print("Monitoring system and writing to %s.\nPress 'Enter' to escape." % output_file)
    while True:
        # Record statistics.
        dt = datetime.now()
        cp = psutil.cpu_percent(interval=2.5)
        pp = psutil.cpu_percent(interval=2.5, percpu=True)
        vm = psutil.virtual_memory().percent
        du = psutil.disk_usage('/').percent
        out.write('\t'.join([str(x) for x in [dt, cp, pp, vm, du]]) + '\n')
        # Exit on 'Enter'
        if l:
            break
    out.close()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("ERROR: Missing output file.\nUsage: system_monitory.py <output_file>")

    print("Done.")
    sys.exit(0)
