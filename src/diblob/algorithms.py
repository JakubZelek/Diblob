import random
from collections import deque
from abc import ABC, abstractmethod
from copy import deepcopy

START = "S"
END = "T"

def edges_to_path(edges):
    if not edges:
        return edges
    path = [edges[0][0]]
    for _, v in edges:
        path.append(v)
    return path

class DFSTemplate(ABC):
    """
    Abstract class for DFS. Used for DFS algorithms modifications.
    """
    def __init__(self, digraph_manager):
        self.visit_time = 0
        self.visited_nodes = []
        self.visitation_dict = {}
        self.digraph_manager = digraph_manager
        self.nodes_to_visit = list(digraph_manager.nodes)


    def exec(self, node_id: str):
        """
        Executes DFS starting with node_id.
        Args:
            - node_id (str): id of the node where computation is started.
        """
        self.nodes_to_visit.remove(node_id)

        random.shuffle(self.nodes_to_visit)
        self.nodes_to_visit = [node_id] + self.nodes_to_visit

        while self.nodes_to_visit:
            self.run(node_id)

            if self.nodes_to_visit:
                node_id = self.nodes_to_visit[0]

    @abstractmethod
    def run(self, node_id: str):
        """
        Abstract runner, used by exec method
        """


class DFS(DFSTemplate):
    """
    Basic DFS.
    """
    def run(self, node_id: str):
        """
        Basic DFS runner.
        """
        self.visited_nodes.append(node_id)
        self.nodes_to_visit.remove(node_id)
        self.visitation_dict[node_id] = {"visitation_time": self.visit_time}

        for outgoing_node_id in self.digraph_manager[node_id].outgoing_nodes:
            if outgoing_node_id not in self.visited_nodes:
                self.run(outgoing_node_id)

        self.visit_time += 1
        self.visitation_dict[node_id] |=  {"return_time": self.visit_time}


class DFS_with_path(DFSTemplate):

    def run(self, node_id):
        test_cases = []   
        current_path = []
        self.run_iter(node_id, current_path, test_cases)

        return test_cases


    def run_iter(self, node_id: str, current_path, test_cases):

        self.visited_nodes.append(node_id)
        self.nodes_to_visit.remove(node_id)
        current_path.append(node_id)

        flag = True
        for outgoing_node_id in self.digraph_manager[node_id].outgoing_nodes:
            if outgoing_node_id not in self.visited_nodes:
                self.run_iter(outgoing_node_id, current_path, test_cases)
                flag = False

        if flag:
            test_cases.append(list(current_path))
        current_path.pop()

class DFSA(DFS):
    """
    DFS modification enables compute time of nodes visitation.
    """
    def __init__(self, digraph_manager):
        super().__init__(digraph_manager)
        self.node_idx = len(self.digraph_manager.nodes)
        self.nodes_order_dict = {}


    @staticmethod
    def ordering_decorator(dfs_proc_func):
        """
        Decorator for runner enables visitation time computation.
        """
        def wrapper(self, node_id):
            result = dfs_proc_func(self, node_id)
            self.node_idx -= 1
            self.nodes_order_dict[self.node_idx] = node_id
            return result
        return wrapper


    @ordering_decorator
    def run(self, node_id):
        super().run(node_id)


class DijkstraAlgorithm:
    """
    Dijkstra Algorithm
    """
    def __init__(self, digraph_manager):
        self.digraph_manager = digraph_manager


    def run(self, node_id: str, cost_function = None):
        """
        Dijkstra algorithm runner. 
        Args:
            - node_id (str): starting node id.
            - cost_function (dict): enable edge weighting.
        """
        if cost_function is None:
            cost_function = {edge_id : 1 for edge_id in self.digraph_manager.edges}

        nodes = sorted(list(self.digraph_manager.nodes))

        min_distance_dict = {dest_node_id: {"distance": float('inf') if dest_node_id != node_id\
                                                                     else 0,
                                            "min_path": []} for dest_node_id in nodes}

        while nodes:

            min_node_id = min(nodes, key=lambda dest_node_id:
                              min_distance_dict[dest_node_id]["distance"])

            v = min_distance_dict[min_node_id]
            min_distance = v["distance"]
            nodes.remove(min_node_id)

            for neigh_id in set(self.digraph_manager[min_node_id].outgoing_nodes) & set(nodes):

                u = min_distance_dict[neigh_id]
                edge_id = (min_node_id, neigh_id)
                potential_new_min_distance = min_distance + cost_function[edge_id]

                if u["distance"] > potential_new_min_distance:
                    u["distance"] = potential_new_min_distance
                    u["min_path"] = v["min_path"] + [edge_id]

        return min_distance_dict


class TarjanSSC:
    """
    Extracts SSC's from the graph.
    """
    def __init__(self, digraph_manager):
        self.digraph_manager = digraph_manager
    
    def run(self):
        stack = []
        defined = set()  # Tracks nodes that have been fully processed
        on_stack = set()
        low_links = {}
        indices = {}
        index = 0
        result = []

        def strong_connect(node_id):
            nonlocal index
            # Mark the node as visited
            indices[node_id] = low_links[node_id] = index
            index += 1
            stack.append(node_id)
            on_stack.add(node_id)
            defined.add(node_id)  # Mark the node as fully defined/processed

            # Traverse outgoing nodes
            for out_node_id in self.digraph_manager[node_id].outgoing_nodes:
                if out_node_id not in defined:  # Node not yet visited
                    strong_connect(out_node_id)
                    low_links[node_id] = min(low_links[node_id], low_links[out_node_id])
                elif out_node_id in on_stack:  # Node is part of the current SCC
                    low_links[node_id] = min(low_links[node_id], indices[out_node_id])

            # Check if this node is the root of an SCC
            if low_links[node_id] == indices[node_id]:
                scc = set()
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.add(w)
                    if w == node_id:
                        break
                result.append(scc)

        # Start the Tarjan's algorithm
        for node_id in self.digraph_manager.nodes:
            if node_id not in defined:
                strong_connect(node_id)

        return result


def normalize_cycle(cycle):
    cycle = cycle[:-1]
    min_index = cycle.index(min(cycle))
    return cycle[min_index:] + cycle[:min_index]

class JonsonForSimpleSSC:
    def __init__(self, digraph_manager):
        self.digraph_manager = digraph_manager

    def run(self, node_id):
        cycles = set()
        nodes = list(self.digraph_manager.nodes)
        nodes.remove(node_id)
        nodes = [node_id] + nodes
        blocked = {node_id: False for node_id in nodes}
        block_map = {node_id: set() for node_id in nodes}
        stack = []

        def circuit(node_id, start):

            stack.append(node_id)
            blocked[node_id] = True
            found_cycle = False

            for outgoing_node_id in self.digraph_manager[node_id].outgoing_nodes:
                if outgoing_node_id == start:

                    cycle = normalize_cycle(stack + [start])
                    cycles.add(tuple(cycle))
                    found_cycle = True
                elif not blocked[outgoing_node_id]:

                    if circuit(outgoing_node_id, start):
                        found_cycle = True

            if found_cycle:
                unblock(node_id)
            else:
                for outgoing_node_id in self.digraph_manager[node_id].outgoing_nodes:
                    block_map[outgoing_node_id].add(node_id)

            stack.pop()
            return found_cycle

        def unblock(node):
            """
            Unblocks a node and its dependent nodes recursively.
            :param node: Node to unblock
            """
            blocked[node] = False
            for dependent in block_map[node]:
                if blocked[dependent]:
                    unblock(dependent)
            block_map[node].clear()

        processed = set()

        for start in self.digraph_manager.nodes:
            if start in processed:
                continue

            circuit(start, start)
            processed.add(start)
        return [list(cycle) for cycle in cycles]


class HopcroftKarp:
    
    @staticmethod
    def run(digraph_manager):
        pair_u = {node_id: None for node_id in digraph_manager.nodes}
        pair_v = {outgoing_node_id: None for node_id in digraph_manager.nodes
                  for outgoing_node_id in digraph_manager[node_id].outgoing_nodes}
        dist = {}
        matching = 0
        while HopcroftKarp.bfs_part(digraph_manager, pair_u, pair_v, dist):
            for node_id in digraph_manager.nodes:
                if pair_u[node_id] is None:
                    if HopcroftKarp.dfs_part(digraph_manager, node_id, pair_u, pair_v, dist):
                        matching += 1
    
        return matching, pair_u, pair_v
    
    @staticmethod
    def bfs_part(digraph_manager, pair_u, pair_v, dist):
        queue = deque()
        for node_id in digraph_manager.nodes:
            if pair_u[node_id] is None:
                dist[node_id] = 0
                queue.append(node_id)
            else:
                dist[node_id] = float('inf')
        dist[None] = float('inf')
        
        while queue:
            node_id = queue.popleft()
            if dist[node_id] < dist[None]:
                for outgoing_node_id in digraph_manager[node_id].outgoing_nodes:
                    if dist[pair_v[outgoing_node_id]] == float('inf'):
                        dist[pair_v[outgoing_node_id]] = dist[node_id] + 1
                        queue.append(pair_v[outgoing_node_id])
        return dist[None] != float('inf')

    @staticmethod
    def dfs_part(digraph_manager, node_id, pair_u, pair_v, dist):
        if node_id is not None:
            for outgoing_node_id in digraph_manager[node_id].outgoing_nodes:
                if dist[pair_v[outgoing_node_id]] == dist[node_id] + 1:
                    if HopcroftKarp.dfs_part(digraph_manager, pair_v[outgoing_node_id], pair_u, pair_v, dist):
                        pair_v[outgoing_node_id] = node_id
                        pair_u[node_id] = outgoing_node_id
                        return True
            dist[node_id] = float('inf')
            return False
        return True
    
    @staticmethod
    def construct_path_cover(digraph_manager):
        
        _, pair_u, _ = HopcroftKarp.run(digraph_manager)
        visited = set()
        paths = []

        unmatched_starts = {v for v in pair_u.keys() if v not in pair_u.values()}

        for start in unmatched_starts:
            if start in visited:
                continue

            path = []
            current = start
            while current is not None and current not in visited:
                path.append(current)
                visited.add(current)
                current = pair_u[current]

            paths.append(path)

        return paths


class ShortestPathBetween2Nodes:

    @staticmethod
    def run(digraph_manager, start, target):
        queue = deque([(start, [start])])
        visited = set()

        while queue:
            current, path = queue.popleft()
            if current == target:
                return path 
            if current not in visited:
                visited.add(current)
                for neighbor in digraph_manager[current].outgoing_nodes:
                    queue.append((neighbor, path + [neighbor]))
        return None

class GenerateDijkstraMatrix:

    @staticmethod
    def run(digraph_manager):
        dijkstra_matrix = {}
        dijkstra = DijkstraAlgorithm(digraph_manager)
        for node_id in digraph_manager.nodes:
            dijkstra_dict = dijkstra.run(node_id)
            for key in dijkstra_dict:
                dijkstra_matrix[(node_id, key)] = edges_to_path(dijkstra_dict[key]['min_path'])

        return dijkstra_matrix
    

class PrimePathsGenerator:
    def __init__(self, digraph_manager):

        self.graph_dict, self.reversed_translation_dict = self.digraph_manager_to_graph_dict(digraph_manager)
        
        self.blocked_set = set()
        self.stack = []
        self.blocked_dict = {}


    def get_extended_graph(self, node_id):
        extended_graph = deepcopy(self.graph_dict)
        extended_graph[1] = [node_id]

        for n_id in list(extended_graph):
            if n_id != node_id and node_id not in extended_graph[n_id]:
                extended_graph[n_id].append(1)
        return extended_graph


    def get_reversed_graph(self):
        reversed_graph = {node_id: [] for node_id in self.graph_dict}

        for node_id, outgoing_nodes in self.graph_dict.items():
            for outgoing_node_id in outgoing_nodes:
                reversed_graph[outgoing_node_id].append(node_id)

        return reversed_graph
    

    def dfs_part(self, node_id, graph, reversed_graph):
        found_cycle = False

        self.stack.append(node_id)
        self.blocked_set.add(node_id)
        
        for outgoing_node_id in graph[node_id]:
            if outgoing_node_id == 1:
               
                outgoing_nodes = graph[node_id]
                incoming_nodes_to_start = reversed_graph[graph[1][0]]

                cannot_be_extend_forward = not (set(outgoing_nodes) - set(self.stack))
                cannot_be_extend_backward = not (set(incoming_nodes_to_start) - set(self.stack))
                
                if cannot_be_extend_forward and cannot_be_extend_backward:

                    yield list(self.stack[1:])
                    found_cycle = True

            elif outgoing_node_id != 1 and self.stack[0] == outgoing_node_id:

                yield list(self.stack + [outgoing_node_id])
                found_cycle = True

            elif outgoing_node_id not in self.blocked_set:
                for result in self.dfs_part(outgoing_node_id, graph, reversed_graph):
                    yield result
                    found_cycle = True

        if found_cycle:
            self.unblock(node_id)
        else:
            for outgoing_node_id in graph[node_id]:
                if node_id not in self.blocked_dict[outgoing_node_id]:
                    self.blocked_dict[outgoing_node_id].append(node_id)

        self.stack.pop()
        return


    def unblock(self, node_id):
        self.blocked_set.remove(node_id)

        for blocked_outgoing_id in self.blocked_dict[node_id]:
            self.blocked_dict[node_id].remove(blocked_outgoing_id)
            if blocked_outgoing_id in self.blocked_set:
                self.unblock(blocked_outgoing_id)


    def get_prime_paths_without_cycles(self):
        for node_id in self.graph_dict:
            extended_graph = self.get_extended_graph(node_id)
            reversed_extended_graph = self.get_reversed_graph()
            self.blocked_dict = {n_id: [] for n_id in extended_graph}
            self.blocked_set = set()
            yield from self.dfs_part(1, extended_graph, reversed_extended_graph)

    def get_cycles(self):
        s = 2
        while s < len(self.graph_dict) + 1:
            graph = {node_id: [w for w in self.graph_dict[node_id] if w >= s] 
                     for node_id in self.graph_dict if node_id >= s}
            if len(graph) != 0:
                s = min(graph.keys())
                self.blocked_dict = {n_id: [] for n_id in graph}
                self.blocked_set = set()

                yield from self.dfs_part(s, graph, None)
                s += 1

    @staticmethod
    def digraph_manager_to_graph_dict(digraph_manager):
        keys = sorted(digraph_manager.nodes)
        translation_dict = {key: index + 2 for index, key in enumerate(keys)}
        
        reversed_translation_dict = {value:key for key, value in translation_dict.items()}
        result_dictionary = {}

        for node_id in digraph_manager.nodes:
            result_dictionary[translation_dict[node_id]] = [
                translation_dict[outgoing_node_id]
                for outgoing_node_id in digraph_manager[node_id].outgoing_nodes]
            
        return result_dictionary, reversed_translation_dict
