
import os
import json
import statistics
from tools import measure_memory_and_time
from diblob.algorithms import PrimePathGenerator, TarjanSCC
from diblob.digraph_manager import DigraphManager
from diblob.side_algorithms import generate_prime_paths, ammann_offutt_prime_paths, get_prime_paths

with open("Diblob/final_cfgs.json") as f:
    data = json.load(f)

with open("Diblob/final_maps.json") as f:
    map_of_ids = json.load(f)

MIN_NUM_OF_NODES = 51
MAX_NUM_OF_NODES = 100
TIMEOUT = 600*3
FLOOR_TIMEOUT = 600

def jonson_based_approach(graph: dict):
    counter = 0
    for _ in PrimePathGenerator(DigraphManager({"G0": graph})).get_prime_paths():
        counter += 1
    return counter
    
def scc_based_approach(graph: dict, start_nodes: list[str]):
    counter = 0
    for _ in generate_prime_paths(graph, start_nodes):
        counter += 1
    return counter

def amman_offutt_original(graph: dict):
    counter = 0
    for _ in get_prime_paths({"nodes": graph.keys(), "edges": graph}):
        counter += 1
    return counter

def amman_offutt_speedup(graph: dict):
    counter = 0
    for _ in ammann_offutt_prime_paths({"nodes": graph.keys(), "edges": graph}):
        counter += 1
    return counter


def find_nodes_with_zero_indegree(graph):
    all_nodes = set(graph.keys())               
    targets = set(node for targets in graph.values() for node in targets)  
    zero_indegree = all_nodes - targets 
    return list(zero_indegree)

if __name__ == "__main__":
        for graph in data:
            try:
                if not (MIN_NUM_OF_NODES <= graph["num_nodes"] <= MAX_NUM_OF_NODES):
                    continue

                digraph = json.loads(graph["graph"])
                sccs = TarjanSCC(DigraphManager({"G0": digraph})).run()

                experiment_info = {}
                experiment_info["num_edges"] = graph["num_edges"]
                experiment_info["num_nodes"] = graph["num_nodes"]
                experiment_info["num_scc"] = len(sccs)
                experiment_info["avg_scc_size"] = sum(len(x) for x in sccs)/len(sccs)
                experiment_info["max_scc_size"] = max(len(x) for x in sccs)
                experiment_info["median_scc_size"] = statistics.median([len(x) for x in sccs])
                experiment_info["is_dag"] = graph["is_dag"]
                experiment_info["filename"] = graph["filename"]
                experiment_info["repo_name"] = map_of_ids[graph["repo_name"]]
                experiment_info["function_name"] = graph["name"]

                print(f"########## PROCESSED GRAPH WITH {experiment_info['num_nodes']} NODES ############ ")

                num_of_prime_paths, memory_peak, time = measure_memory_and_time(jonson_based_approach, timeout=TIMEOUT, graph=digraph)

                if num_of_prime_paths >= 5000:

                    experiment_info["jonson_based_approach"] = {"num_prime_paths": num_of_prime_paths, "memory_peak": memory_peak, "time": time}
                    print(f"jonson_based_approach: TIME: {time}, MEMORY: {memory_peak}, RESULT: {num_of_prime_paths}")
                    
                    # if time < 0.1:
                    #     continue

                    timeout = max(TIMEOUT, 16*time)

                    num_of_prime_paths, memory_peak, time = measure_memory_and_time(amman_offutt_speedup, timeout=timeout, graph=digraph)
                    experiment_info["amman_offutt_speedup"] = {"num_prime_paths": num_of_prime_paths, "memory_peak": memory_peak, "time": time}
                    print(f"amman_offutt_speedup: TIME: {time}, MEMORY: {memory_peak}, RESULT: {num_of_prime_paths}")

                    start_nodes = find_nodes_with_zero_indegree(digraph)
                    num_of_prime_paths, memory_peak, time = measure_memory_and_time(scc_based_approach, timeout=timeout, graph=digraph, start_nodes=start_nodes)
                    experiment_info["scc_based_approach"] = {"num_prime_paths": num_of_prime_paths, "memory_peak": memory_peak, "time": time}
                    print(f"scc_based_approach: TIME: {time}, MEMORY: {memory_peak}, RESULT: {num_of_prime_paths}")

                    num_of_prime_paths, memory_peak, time = measure_memory_and_time(amman_offutt_original, timeout=timeout, graph=digraph)
                    experiment_info["amman_offutt_original"] = {"num_prime_paths": num_of_prime_paths, "memory_peak": memory_peak, "time": time}
                    print(f"amman_offutt_original: TIME: {time}, MEMORY: {memory_peak}, RESULT: {num_of_prime_paths}")


                    print("####################################################")
                    print()

                    
                    with open("Diblob/notebooks/experiments/prime_paths_papier/resultsv/51_100.jsonl", "a") as f:
                        f.write(json.dumps(experiment_info) + "\n")

            except:
                    continue
            