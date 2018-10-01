import datetime
import psutil
import sys

# Process Monitor
# Usage: monitor_specific.py <pid> <output_file>

def get_usage(proc):
    """ Get process usage.
    Returns a list of strings:
    0: Time stamp
    1: Percent CPU usage, measured over 2.5 second interval.
    2: Percent memory, measured as rss
    3: Actual memory used, Resident Set Size (i.e. total memory used by process, inc. shared)
    4: Actual memory used, Unique Set Size (i.e. amount of memory that would be freed if process was terminated)
    5: Number of Threads
    6: Process Status
    """
    ts = '{}'.format(datetime.datetime.now())
    pc = proc.cpu_percent(interval=2.5)
    pm = proc.memory_percent()
    am = proc.memory_full_info()
    nt = proc.num_threads()
    st = proc.status()
    return [ts, str(pc), str(pm), str(am.rss), str(am.uss), str(nt), str(st)]


def main(pid, output_file):
    p = psutil.Process(pid)
    print('{} - INFO - Monitoring process {} ({}, {})'.format(datetime.datetime.now(), pid, p.name(), p.username()))
    print('{} - INFO - Writing stats to {}'.format(datetime.datetime.now(), output_file))
    print('{} - INFO - Use Ctrl-C to stop'.format(datetime.datetime.now()))
    
    with open(output_file, 'w') as o:
        o.write('# Process monitor for pid {}\n')
        o.write('# Process name: {}\n')
        o.write('# Process owner: {}\n')
        o.write('timestamp, percent_cpu, percent_mem, actual_mem_rss, actual_mem_uss, num_threads, status\n')
        try:
            while True:
                o.write('{}\n'.format('\t'.join(get_usage(p))))
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    if len(sys.argv) == 3:
        main(int(sys.argv[1]), sys.argv[2])
    else:
        print('Usage: monitor_specific.py <pid> <output_file>')