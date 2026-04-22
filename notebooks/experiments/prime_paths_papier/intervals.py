
import os
import json
import statistics
import time
from tools import measure_memory_and_time
from diblob.algorithms import PrimePathGenerator, TarjanSCC
from diblob.digraph_manager import DigraphManager
from diblob.side_algorithms import generate_prime_paths, ammann_offutt_prime_paths, get_prime_paths
import tracemalloc
with open("Diblob/final_cfgs.json") as f:
    data = json.load(f)

with open("Diblob/final_maps.json") as f:
    map_of_ids = json.load(f)

MIN_NUM_OF_NODES = 1001
MAX_NUM_OF_NODES = 50000
TIMEOUT = 3600*24
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

THRESHOLD = 500_000_00
MES_THRESHOLD = 1_000_00

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
                experiment_info["exp_result_time"] = []
                # experiment_info["exp_result_memory"] = []

                print(f"########## PROCESSED GRAPH WITH {experiment_info['num_nodes']} NODES ############ ")

                s = time.perf_counter()
                gen = PrimePathGenerator(DigraphManager({"G0": digraph})).get_prime_paths()
                experiment_info["init_time"] = time.perf_counter() - s
                print("INIT TIME:", experiment_info["init_time"])
                s = time.perf_counter()
                s1 = s
                counter = 0 
                # tracemalloc.start()
                for _ in gen:
                    counter += 1
                    if counter % MES_THRESHOLD == 0:
                        checkpoint = time.perf_counter()
                        time_mes = checkpoint - s1
                        # current, peak = tracemalloc.get_traced_memory()
                        # peak = peak / 10**6
                        print(f"REACH CHECKPOINT:, {counter}, TIME: {time_mes}")

                        experiment_info["exp_result_time"].append(time_mes)
                        # experiment_info["exp_result_memory"].append(peak)
                        s1 = checkpoint
                        
                    
                    if counter % THRESHOLD == 0:
                        break 
    
                checkpoint = time.perf_counter()
                print("FINISHED EXPERIMENT: ", checkpoint - s1)
                experiment_info["exp_finish"] = {"counter": counter, "time": s - checkpoint}
                    
                with open("Diblob/notebooks/experiments/prime_paths_papier/resultsv/1001_2000.jsonl", "a") as f:
                    f.write(json.dumps(experiment_info) + "\n")

         
            except:
                continue