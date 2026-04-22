
import json
from tools import measure_memory_and_time
from diblob.algorithms import PrimePathGenerator, TarjanSCC
from diblob.digraph_manager import DigraphManager
from diblob.side_algorithms import generate_prime_paths, ammann_offutt_prime_paths, get_prime_paths
from diblob.generators import generate_diamond



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

TIMEOUT = 3600
experiment_info = {}
if __name__ == "__main__":
       
    for diamond_size in range(13, 21):
        digraph = generate_diamond(k=diamond_size, start_label="B0")
        max_id = max(digraph.keys())

        digraph[max_id].extend(["B0", "T0"])
        digraph["S0"] = ["B0"]
        digraph["T0"] = []


        experiment_info["diamond_size"] = diamond_size
        num_of_prime_paths, memory_peak, time = measure_memory_and_time(jonson_based_approach, timeout=TIMEOUT, graph=digraph)
        experiment_info["jonson_based_approach"] = {"num_prime_paths": num_of_prime_paths, "memory_peak": memory_peak, "time": time}
        print(f"jonson_based_approach: TIME: {time}, MEMORY: {memory_peak}, RESULT: {num_of_prime_paths}")
        

        timeout =  3600*5

        num_of_prime_paths, memory_peak, time = measure_memory_and_time(amman_offutt_speedup, timeout=timeout, graph=digraph)
        experiment_info["amman_offutt_speedup"] = {"num_prime_paths": num_of_prime_paths, "memory_peak": memory_peak, "time": time}
        print(f"amman_offutt_speedup: TIME: {time}, MEMORY: {memory_peak}, RESULT: {num_of_prime_paths}")

        start_nodes = ["S0"]
        num_of_prime_paths, memory_peak, time = measure_memory_and_time(scc_based_approach, timeout=timeout, graph=digraph, start_nodes=start_nodes)
        experiment_info["scc_based_approach"] = {"num_prime_paths": num_of_prime_paths, "memory_peak": memory_peak, "time": time}
        print(f"scc_based_approach: TIME: {time}, MEMORY: {memory_peak}, RESULT: {num_of_prime_paths}")

        num_of_prime_paths, memory_peak, time = measure_memory_and_time(amman_offutt_original, timeout=timeout, graph=digraph)
        experiment_info["amman_offutt_original"] = {"num_prime_paths": num_of_prime_paths, "memory_peak": memory_peak, "time": time}
        print(f"amman_offutt_original: TIME: {time}, MEMORY: {memory_peak}, RESULT: {num_of_prime_paths}")

        print("####################################################")
        print()


        with open("Diblob/notebooks/experiments/prime_paths_papier/resultsv/diamond_extended.jsonl", "a") as f:
                f.write(json.dumps(experiment_info) + "\n")

