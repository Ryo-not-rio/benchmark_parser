import json
import re
import statistics

# List of files to be used. Must be placed in same directory as this python script.
linux_data = [
    "linux_data/config-ccm-psk-dtls1_2.txt", 
    "linux_data/config-ccm-psk-tls1_2.txt", 
    "linux_data/config-no-entropy.txt",
    "linux_data/config-suite-b.txt", 
    "linux_data/config-symmetric-only.txt", 
    "linux_data/config-thread.txt"
]

windows_data = [
    "windows_data/config-ccm-psk-dtls1_2.txt", 
    "windows_data/config-ccm-psk-tls1_2.txt", 
    "windows_data/config-no-entropy.txt",
    "windows_data/config-suite-b.txt", 
    "windows_data/config-symmetric-only.txt", 
    "windows_data/config-thread.txt"
]

def extract_info_from_line(line):
    """ Extract numbers from a line of results. Uses regular 
    expressions to retrieve a list consisting of the name of 
    the algorithm followed by each of its recorded metrics. """

    striped_line = "".join(line.split())
    cleaned_result = re.split(r'\s+|[,;.:]\s*', striped_line)
    cleaned_result[1:] = [int(re.sub('[^0-9]','', x)) for x in cleaned_result[1:]]

    return cleaned_result

def extract_data(files):
    """ Extract raw data from files. Sequentially processess one 
    line of each file at a time, adding a source to the algorithm 
    entry when needed. An element in results may look like: 
        'SHA-256': {
            'sources': {
                'config-ccm-psk-dtls1_2.txt': [116855, 17], 
                'config-ccm-psk-tls1_2.txt': [172499, 0], 
                'config-no-entropy.txt': [158101, 15], 
                'config-suite-b.txt': [183145, 13], 
                'config-symmetric-only.txt': [102813, 0], 
                'config-thread.txt': [180238, 14]
            }
        }
    
    Where each element of 'sources' is a key with the filename 
    from which the metrics come from, and the value is a list of metrics recorded.
    """

    results = {}

    for file_name in files:
        with open(file_name) as f:
            for line in f.readlines():
                elements = extract_info_from_line(line)

                if elements[0] not in results:
                    results[elements[0]] = {}

                if "sources" not in results[elements[0]]:
                    results[elements[0]]['sources'] = {}
                    
                results[elements[0]]['sources'][file_name] = elements[1:]

    return results

def analyse_results(results):
    """ Takes in the output of 'extract_data', and 
    calculates median, max value, and min value for each column in the source. For example:
    
        'SHA-256': {
            'sources': {
                'config-ccm-psk-dtls1_2.txt': [101934, 0], 
                'config-ccm-psk-tls1_2.txt': [98789, 0], 
                'config-no-entropy.txt': [98929, 29], 
                'config-suite-b.txt': [94852, 30], 
                'config-symmetric-only.txt': [103846, 0], 
                'config-thread.txt': [103669, 28]
            }
        }

    Here, a median value will be calculated for 
    [101934, 98789, 98929, 94852, 103846, 103669] and 
    [0, 0, 29, 30, 0, 28], and the results will be elements in a new list
    that is added as:
        'SHA-256': {
            'medians': [100431.5, 14.0]
            'sources': ...
        }

    This process is repeated for min and max values.
    """

    for key, algorithm in results.items():
        medians = []
        maxes = []
        mins = []

        for i in range(len(list(algorithm['sources'].values())[0])):
            data = [algorithm['sources'][x][i] for x in algorithm['sources']]

            medians.append(statistics.median(data))
            maxes.append(max(data))
            mins.append(min(data))

        results[key]['medians'] = medians
        results[key]['maxes'] = maxes
        results[key]['mins'] = mins

    return results


def filter_results_with_less_than_n_entries(n, results):
    """ Removes all results that have less than n sources. """
    return {k: v for k, v in results.items() if len(v['sources']) >= n}

def save_as_json(name, results):
    """ Saves the results as a .json file. """
    with open(name, 'w') as outfile:
        json.dump(results, outfile)


filter_entries_at_least = 4

# Handling Linux data:
results_linux = extract_data(linux_data)
results_linux = filter_results_with_less_than_n_entries(filter_entries_at_least, results_linux)
results_linux = analyse_results(results_linux)

print(f'LINUX: Filtering entries with at least {filter_entries_at_least} entries resulting in {len(results_linux)} algorithms.')

print("Saving results as json...")
save_as_json(f'results_linux_{filter_entries_at_least}_or_more.json', results_linux)
print("Done.")

# Handling Windows data:
results_windows = extract_data(windows_data)
results_windows = filter_results_with_less_than_n_entries(filter_entries_at_least, results_windows)
results_windows = analyse_results(results_windows)

print(f'WINDOWS: Filtering entries with at least {filter_entries_at_least} entries resulting in {len(results_windows)} algorithms.')

print("Saving results as json...")
save_as_json(f'results_windows_{filter_entries_at_least}_or_more.json', results_windows)
print("Done.")

