#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 08:41:43 2023

@author: mavroudo
"""

# This script generates multiple datasets from a single real world dataset
# where each time only a portion of the traces are carried on to the next file
# while for the rest we assign a new trace id. Additionally, for each file
# we will use multi-threading to speed-up the process


import pm4py
from datetime import datetime, timedelta
import sys
import random
import string
import copy
from threading import Thread, Lock

from pm4py.objects.log.obj import Trace, Event


# Function to generate random case identifiers
def generate_random_case_id(length=10):
    # Generate a string with letters, digits, and symbols
    characters = string.ascii_letters + string.digits
    random_case_id = ''.join(random.choice(characters) for _ in range(length))
    return random_case_id


# Function to replicate a percentage of traces in the log
def replicate_traces(log, carry_on_traces=0.1):
    # Calculate how many traces to replicate based on the carry_on_traces
    num_traces_to_replicate = int(len(log) * carry_on_traces)
    # Randomly select the traces to replicate
    traces_to_replicate = random.sample(log, num_traces_to_replicate)
    # Duplicate the selected traces and assign new case ids to avoid duplicates
    for trace in traces_to_replicate:
        # Make a deep copy of the trace to avoid modifying the original trace
        new_trace = copy.deepcopy(trace)
        # Assign a new random case id to the replicated trace
        new_trace.attributes['concept:name'] = generate_random_case_id()
        # append to log
        log.append(new_trace)

    return log


def transform_original_log(log, diff_days, want_days, min_ts):
    for t in log:
        for e in t:
            t_prev = e["time:timestamp"]
            e["time:timestamp"] = datetime.fromtimestamp(
                (t_prev.timestamp() - min_ts.timestamp()) / diff_days * want_days + min_ts.timestamp())
    for t in log:
        t.attributes['concept:name'] = generate_random_case_id()
        for index, e in enumerate(t[:-1]):
            diff = (t[index + 1]["time:timestamp"] - t[index]["time:timestamp"])
            if 0 < diff.seconds < 60 and diff.days == 0:
                t[index + 1]["time:timestamp"] += timedelta(minutes=1)
            elif diff.seconds < 0:
                t[index + 1]["time:timestamp"] += timedelta(minutes=2)
    return len(log), [t.attributes["concept:name"] for t in log]

def remove_partial_events_from_traces(log, carry_on_traces):
    # select new traces to be removed
    traces_to_remove = int(len(log) * carry_on_traces)
    traces = set([i.attributes["concept:name"] for i in random.sample(log, traces_to_remove)])
    for_next=[]
    for t in log:
        if t.attributes["concept:name"] in traces:
            removed_events_trace = copy.deepcopy(t)
            try:
                pos = random.randint(0,len(t))
            except:
                pos = len(t)
            removed_events_trace=removed_events_trace[:pos]
            t_new = Trace()
            t_new.attributes["concept:name"] = t.attributes["concept:name"]
            for e in t[pos:]:
                new_ev = Event()
                new_ev['concept:name'] = e['concept:name']
                new_ev['time:timestamp'] = e['time:timestamp']
                t_new.append(new_ev)
            for_next.append(t_new)
            t[:]=removed_events_trace
    return for_next





def create_additional_log(log, want_days, prev_traces: list, log_index: int, output_file: str):
    # =============================================================================
    #     Calculate the new trace numbers
    # =============================================================================
    # change the names of the ids because they are new
    for t in log:
        t.attributes["concept:name"] = generate_random_case_id()
    # append the traces that have been removed from the previous log
    for t in prev_traces:
        log.append(t)

    for_next = remove_partial_events_from_traces(log,carry_on_traces)
    size=0
    l = []
    for t in log:
        transf = []
        for e in t:
            size+=1
            ts = e["time:timestamp"] + timedelta(days=log_index * want_days)
            transf.append("{}/delab/{}".format(e['concept:name'], ts.strftime("%Y-%m-%d %H:%M:%S")))
        if len(transf)>0:
            l.append("{}::{}\n".format(t.attributes["concept:name"], ",".join(transf)))
    print("Log file size:",size)
    return l, for_next



if __name__ == "__main__":
    # =============================================================================
    #     Loading parameters
    # =============================================================================
    carry_on_traces = 0.1  # 10%
    logfile = sys.argv[1]  # dataset file path
    want_days = int(sys.argv[2])  # how many days each log should expand
    num_logs = int(sys.argv[3])  # number of logs to be generated
    log = pm4py.read_xes(logfile)
    print("Original size:",sum([len(t) for t in log]))
    # =============================================================================
    #     Transforming original trace to scale into the want_days parameter
    # =============================================================================
    timestamps = [i["time:timestamp"] for j in log for i in j]
    min_ts = min(timestamps)
    max_ts = max(timestamps)
    diff_days = (max_ts - min_ts).days + 1
    transform_original_log(log, diff_days, want_days, min_ts)
    replicate_traces(log, carry_on_traces)

    # =============================================================================
    #     Main Loop for the num_logs
    # =============================================================================
    for_next = []
    for n in range(num_logs):
        print(n)
        l1,for_next = create_additional_log(log,want_days,for_next,n,"")
        log_name = logfile.split("/")[-1].split(".")[0] + "_" + str(n) + ".withTimestamp"
        with open(log_name, 'w') as fout:
            for line in l1:
                fout.write(line)


