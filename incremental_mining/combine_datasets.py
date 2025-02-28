import argparse
from datetime import datetime
import pm4py
from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY
from pm4py.objects.log.exporter.xes import exporter as xes_exporter

# Function to create a trace using pm4py
def create_trace_pm4py(trace_id, events, delimiter):
    trace = Trace()
    
    for event_str in events:
        event_parts = event_str.split(delimiter)
        
        event = Event()
        event['concept:name'] = event_parts[0]  # Event type
        
        timestamp = datetime.strptime(event_parts[1], "%Y-%m-%d %H:%M:%S")
        event[DEFAULT_TIMESTAMP_KEY] = timestamp
        
        if len(event_parts) == 3:
            event['org:resource'] = event_parts[2]  # Optional resource attribute
        
        trace.append(event)
    
    trace.attributes['concept:name'] = trace_id
    return trace

# Function to process a single file and return traces
def process_file_pm4py(file_path, delimiter, event_separator):
    traces = []
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
        for line in lines:
            trace_id, events_str = line.strip().split("::")
            events = events_str.split(event_separator)
            traces.append(create_trace_pm4py(trace_id, events, delimiter))
    
    return traces

# Function to generate the XES file from multiple input files
def generate_xes_pm4py(output_file, input_files, delimiter, event_separator):
    # Create an empty pm4py event log
    log = EventLog()
    
    # Process each input file and add traces to the log
    for file_path in input_files:
        traces = process_file_pm4py(file_path, delimiter, event_separator)
        for trace in traces:
            log.append(trace)
    
    # Export the event log to a XES file using pm4py
    xes_exporter.apply(log, output_file)

# Main function to parse arguments and call the XES generation function
if __name__ == '__main__':
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Generate a XES log from input event data.')
    
    # Optional arguments
    parser.add_argument('--delimiter', type=str, default='/delab/', help='Delimiter for event attributes (default: "/delab/")')
    parser.add_argument('--separator', type=str, default=',', help='Separator between events in the same trace (default: ",")')
    
    # Positional arguments for input and output files
    parser.add_argument('input_files', type=str, nargs='+', help='List of input files to process (separated by spaces)')
    parser.add_argument('output_file', type=str, help='Output XES file')

    # Parse the arguments
    args = parser.parse_args()

    # Call the function to generate the XES file with the parsed arguments
    generate_xes_pm4py(args.output_file, args.input_files, args.delimiter, args.separator)

