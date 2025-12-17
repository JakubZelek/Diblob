import random
from collections import deque
from abc import ABC, abstractmethod
from copy import deepcopy
from diblob.digraph_manager import DigraphManager
from diblob.factory import DiblobFactory
from diblob.exceptions import CollisionException, InvalidNodeIdException


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
        self.visitation_dict[node_id] |= {"return_time": self.visit_time}


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

    def run(self, node_id: str, cost_function=None):
        """
        Dijkstra algorithm runner.
        Args:
            - node_id (str): starting node id.
            - cost_function (dict): enable edge weighting.
        """
        if cost_function is None:
            cost_function = {edge_id: 1 for edge_id in self.digraph_manager.edges}

        nodes = sorted(list(self.digraph_manager.nodes))

        min_distance_dict = {
            dest_node_id: {
                "distance": float("inf") if dest_node_id != node_id else 0,
                "min_path": [],
            }
            for dest_node_id in nodes
        }

        while nodes:
            min_node_id = min(
                nodes,
                key=lambda dest_node_id: min_distance_dict[dest_node_id]["distance"],
            )

            v = min_distance_dict[min_node_id]
            min_distance = v["distance"]
            nodes.remove(min_node_id)

            for neigh_id in set(self.digraph_manager[min_node_id].outgoing_nodes) & set(
                nodes
            ):
                u = min_distance_dict[neigh_id]
                edge_id = (min_node_id, neigh_id)
                potential_new_min_distance = min_distance + cost_function[edge_id]

                if u["distance"] > potential_new_min_distance:
                    u["distance"] = potential_new_min_distance
                    u["min_path"] = v["min_path"] + [edge_id]

        return min_distance_dict


class TarjanSCC:
    """
    Extracts SSC's from the graph.
    """

    def __init__(self, digraph_manager):
        self.digraph_manager = digraph_manager

    def run(self):
        stack = []
        defined = set()
        on_stack = set()
        low_links = {}
        indices = {}
        index = 0
        result = []

        def strong_connect(node_id):
            nonlocal index

            indices[node_id] = low_links[node_id] = index
            index += 1
            stack.append(node_id)
            on_stack.add(node_id)
            defined.add(node_id)

            for out_node_id in self.digraph_manager[node_id].outgoing_nodes:
                if out_node_id not in defined:
                    strong_connect(out_node_id)
                    low_links[node_id] = min(low_links[node_id], low_links[out_node_id])
                elif out_node_id in on_stack:
                    low_links[node_id] = min(low_links[node_id], indices[out_node_id])

            if low_links[node_id] == indices[node_id]:
                scc = set()
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.add(w)
                    if w == node_id:
                        break
                result.append(scc)

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
        pair_v = {
            outgoing_node_id: None
            for node_id in digraph_manager.nodes
            for outgoing_node_id in digraph_manager[node_id].outgoing_nodes
        }
        dist = {}
        matching = 0
        while HopcroftKarp.bfs_part(digraph_manager, pair_u, pair_v, dist):
            for node_id in digraph_manager.nodes:
                if pair_u[node_id] is None:
                    if HopcroftKarp.dfs_part(
                        digraph_manager, node_id, pair_u, pair_v, dist
                    ):
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
                dist[node_id] = float("inf")
        dist[None] = float("inf")

        while queue:
            node_id = queue.popleft()
            if dist[node_id] < dist[None]:
                for outgoing_node_id in digraph_manager[node_id].outgoing_nodes:
                    if dist[pair_v[outgoing_node_id]] == float("inf"):
                        dist[pair_v[outgoing_node_id]] = dist[node_id] + 1
                        queue.append(pair_v[outgoing_node_id])
        return dist[None] != float("inf")

    @staticmethod
    def dfs_part(digraph_manager, node_id, pair_u, pair_v, dist):
        if node_id is not None:
            for outgoing_node_id in digraph_manager[node_id].outgoing_nodes:
                if dist[pair_v[outgoing_node_id]] == dist[node_id] + 1:
                    if HopcroftKarp.dfs_part(
                        digraph_manager, pair_v[outgoing_node_id], pair_u, pair_v, dist
                    ):
                        pair_v[outgoing_node_id] = node_id
                        pair_u[node_id] = outgoing_node_id
                        return True
            dist[node_id] = float("inf")
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
                dijkstra_matrix[(node_id, key)] = edges_to_path(
                    dijkstra_dict[key]["min_path"]
                )

        return dijkstra_matrix

class PrimePathCore:
    """
    Core for Simple Cycle Generator and Max Simple Path generator.
    """

    def __init__(self, digraph_manager: DigraphManager):
        self.digraph_manager = digraph_manager

        diblob_id = self.digraph_manager.root_diblob_id
        self.graph_dict = dict(self.digraph_manager(diblob_id)[diblob_id])
        self.reversed_graph = self.reverse_graph(self.graph_dict)

        self.tarjant_dict = {}
        for scc in TarjanSCC(digraph_manager).run():
            for node_id in scc:
                self.tarjant_dict[node_id] = scc

    def dfs_jonson(self, node_id: str, induced_graph: dict, stack: list,
                    blocked_set: set, blocked_dict: dict):
        """
        DFS part from Jonson's algorithm
        """
        found_cycle = False
        stack.append(node_id)
        blocked_set.add(node_id)

        for outgoing_node_id in induced_graph[node_id]:
            if stack[0] == outgoing_node_id:
                yield (*stack, outgoing_node_id)
                found_cycle = True

            elif outgoing_node_id not in blocked_set:
                for result in self.dfs_jonson(outgoing_node_id,
                                              induced_graph,
                                              stack,
                                              blocked_set,
                                              blocked_dict):
                    yield result
                    found_cycle = True

        if found_cycle:
            self.unblock(blocked_set, blocked_dict, node_id)
        else:
            for outgoing_node_id in induced_graph[node_id]:
                if node_id not in blocked_dict[outgoing_node_id]:
                    blocked_dict[outgoing_node_id].add(node_id)

        stack.pop()
        return

    def unblock(self, blocked_set: set, blocked_dict: dict, node_id: str):
        """
        Unblock mechanism from Jonson's algorithm for simple cycles.
        """
        blocked_set.remove(node_id)

        while blocked_dict[node_id]:
            blocked_outgoing_id = blocked_dict[node_id].pop()
            if blocked_outgoing_id in blocked_set:
                self.unblock(blocked_set, blocked_dict, blocked_outgoing_id)

    @staticmethod
    def reverse_graph(graph_dict: dict):
        """
        Returns reversed graph for given dict.
        example: {'A': ['B'], 'B': []} -> {'B': ['A'], 'A': []}
        """
        reversed_graph = {node_id: [] for node_id in graph_dict}

        for node_id, outgoing_nodes in graph_dict.items():
            for neigh in outgoing_nodes:
                reversed_graph[neigh].append(node_id)

        return reversed_graph

class MaxSimplePathGenerator(PrimePathCore):
    """
    MaX Simple Path Generator - based on the node_id
    """
    def __init__(self, digraph_manager: DigraphManager):
        super().__init__(digraph_manager)

        self.sources = {node_id for node_id in digraph_manager.nodes
                        if len(digraph_manager[node_id].incoming_nodes) == 0}
        self.sinks = {node_id for node_id in digraph_manager.nodes
                      if len(digraph_manager[node_id].outgoing_nodes) == 0}


    def get_extended_graph(self, node_id: str, artificial_node: str = "ArtificialNode"):
        """
        Returns extended digraph for given node_id, None if
        node_id cannot be a Maximal Simple Path starting node.
        """

        if artificial_node in self.digraph_manager:
            raise CollisionException(f"Please choose other node_id, {artificial_node} is occupied")
        if node_id not in self.digraph_manager:
            raise InvalidNodeIdException(f"{node_id} doesn't exists in \
                    digraph_manager, available nodes: {self.digraph_manager.nodes}")

        incoming_nodes = self.digraph_manager[node_id].incoming_nodes
        set_in_outgoing = set()

        for incoming_node_id in self.digraph_manager[node_id].incoming_nodes:
            if self.tarjant_dict[incoming_node_id] - self.tarjant_dict[node_id]:
                return False #Always extendable -> Different SCCs
            set_in_outgoing |= set(self.digraph_manager[incoming_node_id].outgoing_nodes)

        if len(set_in_outgoing) <= len(incoming_nodes) and len(incoming_nodes) > 0:
            return False

        nodes_to_add = {(artificial_node, node_id)}

        for digraph_manager_node_id in self.digraph_manager.nodes:

            if digraph_manager_node_id == node_id:
                continue

            if node_id in self.digraph_manager.nodes[digraph_manager_node_id].outgoing_nodes:
                continue #There is a possible cycle

            skip_loop = False
            outgoings = self.digraph_manager[digraph_manager_node_id].outgoing_nodes
            set_out_incomings = set()

            for outgoing_node_id in outgoings:
                if self.tarjant_dict[outgoing_node_id] != self.tarjant_dict[digraph_manager_node_id]:
                    skip_loop = True
                    break

                set_out_incomings |= set(self.digraph_manager[outgoing_node_id].incoming_nodes)

            if skip_loop or len(set_out_incomings) <= len(outgoings) and len(outgoings) > 0:
                continue

            nodes_to_add.add((digraph_manager_node_id, artificial_node))

        self.digraph_manager.add_nodes(artificial_node)
        self.digraph_manager.connect_nodes(*nodes_to_add)

        return True

    def get_maximal_simple_path_for_node_id(self,
                                            node_id: str,
                                            artificial_node: str = "ArtificialNode"):
        """
        Yields maximal simple paths that starts from node_id
        """
        graph_dict = self.graph_dict
        reversed_graph = self.reversed_graph
        extended_graph = self.get_extended_graph(node_id, artificial_node)
        digraph_manager = self.digraph_manager

        if extended_graph:

            for scc in TarjanSCC(digraph_manager).run():

                if node_id in scc:

                    induced_graph = DiblobFactory.get_induced_digraph(digraph_manager, scc)
                    induced_graph = dict(induced_graph("Ind")["Ind"])

                    blocked_dict = {n_id: set() for n_id in induced_graph}
                    blocked_set = set()
                    stack = []

                    for potential_simple_path in self.dfs_jonson(artificial_node,
                                                                 induced_graph,
                                                                 stack,
                                                                 blocked_set,
                                                                 blocked_dict):

                        potential_simple_path = potential_simple_path[1:-1]
                        tail, head = potential_simple_path[0], potential_simple_path[-1]

                        tail_ok = all(_node in potential_simple_path
                                      for _node in reversed_graph[tail])
                        head_ok = all(_node in potential_simple_path
                                      for _node in graph_dict[head])

                        if tail_ok and head_ok:
                            yield potential_simple_path

                    self.digraph_manager.remove_nodes(self.digraph_manager[artificial_node])
                    return


class SimpleCycleGenerator(PrimePathCore):
    """
    Simple Cycles Generator
    """

    def __init__(self, digraph_manager: DigraphManager):
        super().__init__(digraph_manager)

    def get_simple_cycles(self):
        """
        Yields simple cycles
        """

        nodes = list(self.digraph_manager.nodes)
        digraph_manager = self.digraph_manager
        tarjan_dict = self.tarjant_dict

        for node_index, node_id in enumerate(nodes):
            induced_nodes = set(nodes[node_index:]) & tarjan_dict[node_id]
            induced_graph = DiblobFactory.get_induced_digraph(digraph_manager, induced_nodes)
            induced_graph = dict(induced_graph("Ind")["Ind"])

            stack = []
            blocked_dict = {n_id: set() for n_id in induced_graph}
            blocked_set = set()

            yield from self.dfs_jonson(node_id,
                                        induced_graph,
                                        stack,
                                        blocked_set,
                                        blocked_dict)

class PrimePathGenerator:
    """
    Prime Paths generator (backward compatibility)
    """
    def __init__(self, digraph_manager):
        self.digraph_manager = digraph_manager
        self.max_simple_paths_generator = MaxSimplePathGenerator(digraph_manager)
        self.simple_cycles_generator = SimpleCycleGenerator(digraph_manager)

    def get_prime_paths_without_cycles(self):
        for node_id in self.digraph_manager.nodes:
            for max_simple_cycle in self.max_simple_paths_generator.get_maximal_simple_path_for_node_id(node_id):
                yield max_simple_cycle

    def get_cycles(self):
        for simple_cycle in self.simple_cycles_generator.get_simple_cycles():
            yield simple_cycle