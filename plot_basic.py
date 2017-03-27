#!/usr/bin/env python

# Plot System Usage
# Given a system_monitor.py output log, create a plotly graph of system usage.
# Usage: plot_sys_use.py <log.txt>

import sys
from datetime import datetime

import plotly.plotly as pyo
import plotly.offline as py
import plotly.graph_objs as go

def parse_annotations_file(timeseries, filename):
    annots = {'timestamp': [], 'type': [], 'message': []}
    with open(filename, 'r') as an_in:
        content = {}
        for line in an_in:
            line=line.strip()
            if len(line) > 0:
                if line[0] != '#':
                    line = line.split(' - ')
                    if len(line) >= 4:
                        if line[2] == 'INFO':
                            annots['timestamp'].append(datetime.strptime(line[0], '%Y-%m-%d %H:%M:%S,%f'))
                            annots['message'].append(line[3])
            else:
                pass

    i = 0
    if timeseries[0] < annots['timestamp'][-1]:
        labels = []
        for t in timeseries:
            annotation = None
            while not annotation:
                if t >= annots['timestamp'][i] and t <= annots['timestamp'][i+1]:
                    annotation = annots['message'][i]
                else:
                    i += 1
            labels.append(annotation)
        return labels
    else:
        print('WARNING: No annotations found within time frame.')
        return timeseries



def main(log):

    # Use Date Format
    date_format = '%Y-%m-%d %H:%M:%S.%f'

    # Set limits.
    limits = False
    # limits = {'start': '2017-01-12 16:08:01.420',
    #           'end': '2017-01-13 06:34:22.768'}

    # Define Timeframes for Labeling
    tf = False
    # tf = {'Sample_15_v1': ['2017-01-13 03:33:54.740', '2017-01-13 05:34:23.138'],
    #       'Sample_15_v2': ['2017-01-12 16:29:33.990', '2017-01-12 19:28:42.250'],
    #       'Sample_15_v3': ['2017-01-12 19:28:46.364', '2017-01-13 00:17:03.561'],
    #       'Sample_15_v4': ['2017-01-13 00:17:07.660', '2017-01-13 01:55:18.162'],
    #       'Sample_15_v5': ['2017-01-13 01:55:27.922', '2017-01-13 03:33:42.054']}

    # Create a text annotation track from debug log.
    annotations = False
    # annotation_filename = 'logs/Sample_2_chimerascan_run.log'

    data = {"time": [], "cpu": [], "pcpu": [], "mem": [], "disk": []}

    with open(log, 'r') as inpt:
        header = inpt.readline()
        for l in inpt.readlines():
            l = l.strip().split('\t')
            data["time"].append(datetime.strptime(l[0], date_format))
            data["cpu"].append(float(l[1]))
            data["pcpu"].append([float(x) for x in eval(l[2])])
            data["mem"].append(float(l[3]))
            data["disk"].append(float(l[4]))

    if limits:
        # datetime.strptime(limits['start'], limit_format) > datetime.strptime(limits['end'], limit_format):
        new_data = {"time": [], "cpu": [], "pcpu": [], "mem": [], "disk": [], 'rel_s': []}
        start = False
        for i in range(len(data['time'])):
            t = data['time'][i]
            if t >= datetime.strptime(limits['start'], date_format) and t <= datetime.strptime(limits['end'], date_format):
                if not start:
                    start = t
                    new_data['time'].append(t)
                    new_data['cpu'].append(data['cpu'][i])
                    new_data['mem'].append(data['mem'][i])
                    new_data['disk'].append(data['disk'][i])
                    new_data['rel_s'].append((t - start).total_seconds())
                else:
                    new_data['time'].append(t)
                    new_data['cpu'].append(data['cpu'][i])
                    new_data['mem'].append(data['mem'][i])
                    new_data['disk'].append(data['disk'][i])
                    new_data['rel_s'].append((t - start).total_seconds())
        data = new_data
    else:
        start = data['time'][0]
        data["rel_s"] = [(x - start).total_seconds() for x in data['time']]

    if annotations:
        text = parse_annotations_file(data['time'], annotation_filename)
    else:
        text = data['time']

    cpu_trace = go.Scatter(
        name="CPU",
        x=data['rel_s'],
        y=data['cpu'],
        text=text,
        line={'color': '#355C7D'}
    )
    disk_trace = go.Scatter(
        name="Disk",
        x=data['rel_s'],
        y=data['disk'],
        line={'color': '#C06C84'}
    )
    mem_trace = go.Scatter(
        name="Memory",
        x=data['rel_s'],
        y=data['mem'],
        line={'color': '#F8B195'}
    )
    data = [cpu_trace, disk_trace, mem_trace]


    if tf:
        for name, limits in tf.iteritems():
            s = (datetime.strptime(limits[0], date_format) - start).total_seconds()
            e = (datetime.strptime(limits[1], date_format) - start).total_seconds()
            t_trace = go.Scatter(
                name=name,
                x=[s, e],
                y=[100, 100],
                mode='lines+markers',
                fill='tozeroy'
                # line={'color': '#000000'}
            )
            data.append(t_trace)


    layout = {'title': "Worker Resource Utilization Profile",
              'xaxis': {'title': 'Time (s)'},
              'yaxis': {'title': 'Usage (%)'}}


    fig = {'data': data, 'layout': layout}
    pyo.plot(fig, filename="fig/full_master_profile.html", show_link=False)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("ERROR: Please specify a system_monitor.py log file.\nUsage: plot_sys_use.py <log.txt>")

    sys.exit(0)