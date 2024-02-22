import random
from abc import ABC, abstractmethod


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
            - node_id (str): id ot the node where computation is started.
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


    def run(self, node_id: str, cost_function: dict = None):
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
