"""
Implementation of the algorithm available in the following papier:
https://ieeexplore.ieee.org/document/8836452?denied=

[1] E. Fazli and M. Afsharchi, "A Time and Space-Efficient Compositional Method for Prime and Test Paths Generation," in IEEE Access, vol. 7, pp. 134399-134410, 2019, doi: 10.1109/ACCESS.2019.2941429. keywords: {Complexity theory;Approximation algorithms;Merging;Software testing;Software algorithms;Flow graphs;Software testing;structural testing;prime path coverage},
"""

from dataclasses import dataclass
from diblob.algorithms import TarjanSCC
from diblob.digraph_manager import DigraphManager
from collections import deque


@dataclass
class Path:
    path: list
    read_by_vertex: set = None
    extended: bool = None
    is_cycle: bool = None
    scc_dict: dict = None

    def __add__(self, other):
        return Path(self.path + other, set(), False, False)

    def __getitem__(self, index):
        result = self.path[index]
        if isinstance(index, slice):
            return Path(result, set(), self.extended, self.is_cycle)
        return result

    def __len__(self):
        return len(self.path)

    def __contains__(self, item):
        return item in self.path

    def __lt__(self, other):
        return "-".join(self.path) in "-".join(other.path)

    def __repr__(self):
        return str(self.path)

    def __hash__(self):
        return hash(tuple(self.path))

    def __eq__(self, other):
        return "-".join(self.path) == "-".join(other.path)

    def index(self, value):
        """
        Returns index of the element.
        """
        return self.path.index(value)

    def get_scc_indexes(self):
        """
        Returns dictionary with strongly connected components and their indexes.
        """
        return {
            scc_id: idx
            for idx, scc_id in enumerate(self.path)
            if scc_id.startswith("SCC_")
        }

    def replace_node_with_path(self, other, index):
        """
        Replace node with path based on specific index.
        """
        path = list(self.path)
        path[index : index + 1] = other.path
        return Path(path, set(), False, False)

    def get_scc_crossed_by_path(self, scc_dict: dict):
        """
        Yield scc's (with the size > 1) that are crossed by path.
        """
        for scc in scc_dict.values():
            if set(self.path) & scc.nodes:
                yield scc


class SCC:
    """
    Strongly connected component class
    """

    def __init__(self, scc_graph: dict, graph: dict):
        self.scc_graph = scc_graph
        self.internal_paths = self.get_internal_prime_paths()

        self.scc_entry_nodes = {
            scc_node_id
            for scc_node_id in scc_graph
            if any(
                scc_node_id in graph[node_id]
                for node_id in graph
                if node_id not in scc_graph
            )
        }
        self.scc_exit_nodes = {
            scc_node_id
            for scc_node_id in scc_graph
            if any(
                node_id in graph[scc_node_id]
                for node_id in graph
                if node_id not in scc_graph
            )
        }
        self.nodes = scc_graph.keys()

        self.entry_exit_paths = self.compute_entry_exit_paths()
        self.entry_paths = self.extract_entry_paths()
        self.exit_paths = self.extract_exit_paths()

    def compute_entry_exit_paths(self):
        """
        Returns paths that.
        """
        scc_entry_exit_list = []
        for scc_entry in self.scc_entry_nodes:
            for scc_exit in self.scc_exit_nodes:
                scc_entry_exit_list.extend(
                    list(
                        scc_entry_exit_paths_extraction(
                            self.internal_paths, scc_entry, scc_exit
                        )
                    )
                )
        return scc_entry_exit_list

    def extract_entry_paths(self):
        """
        Returns entry paths that of SCC.
        """
        scc_entry_set = set()
        for scc_entry in self.scc_entry_nodes:
            scc_entry_set |= scc_entry_paths_extraction(self.internal_paths, scc_entry)
        return scc_entry_set

    def extract_exit_paths(self):
        """
        Returns exit paths that of SCC.
        """
        scc_exit_set = set()
        for scc_exit in self.scc_exit_nodes:
            scc_exit_set |= scc_exit_paths_extraction(self.internal_paths, scc_exit)
        return scc_exit_set

    def get_internal_prime_paths(self):
        """
        Returns internal prime paths of SCC.
        """
        scc_prime_paths = set()
        for v in self.scc_graph.keys():
            paths_ended_in_v = vertex_based_prime_paths_generation(self.scc_graph, v)
            for values in paths_ended_in_v.values():
                scc_prime_paths |= set(values)
        return scc_prime_paths

    def __repr__(self):
        return str(self.scc_graph)


def get_ccfg_graph_and_scc_dict(graph: dict):
    """
    Returns CCFG graph and SCC dictionary (scc_name: SCC).
    """
    digraph = DigraphManager({"Graph": graph})
    tarjan = TarjanSCC(digraph)

    scc_number = 0
    scc_dict = {}
    for scc in tarjan.run():
        if len(scc) > 1:
            scc_id = f"SCC_{scc_number}"

            scc_dict[scc_id] = SCC(
                scc_graph={
                    scc_node_id: [
                        scc_node_outgoing_id
                        for scc_node_outgoing_id in graph[scc_node_id]
                        if scc_node_outgoing_id in scc
                    ]
                    for scc_node_id in scc
                },
                graph=graph,
            )

            digraph.gather(scc_id, scc)
            digraph.compress_diblob(scc_id)

            scc_number += 1

    return dict(digraph("Graph"))["Graph"], scc_dict


def vertex_based_prime_paths_generation(graph: dict, s: str):
    """
    Algorithm 1 from [1]
    """
    paths_ended_in_v = {
        key: [Path(path=[key], read_by_vertex=set(), extended=False, is_cycle=False)]
        for key in graph.keys()
    }
    update_flags = {key: False for key in graph.keys()}
    reversed_graph = {key: [] for key in graph.keys()}

    for key, value in graph.items():
        for v in value:
            reversed_graph[v].append(key)

    queue = [s]

    while queue:
        vi = queue.pop(0)
        update_flags[vi] = False

        if vi == s:
            queue.extend(graph[vi])

        for vj in reversed_graph[vi]:
            for q in paths_ended_in_v[vj]:
                if q[0] != q[-1] or len(q) == 1:
                    if vi not in q.read_by_vertex:
                        q.read_by_vertex.add(vi)
                        if vi not in q or vi == q[0]:
                            r = q + [vi]
                            q.extended = True
                            if vi == q[0]:
                                r.is_cycle = True
                            paths_ended_in_v[vi].append(r)
                            update_flags[vi] = True

                    if all(
                        all(succ in q.read_by_vertex for q in paths_ended_in_v[vj])
                        for succ in graph[vj]
                    ):
                        paths_ended_in_v[vj] = [
                            p
                            for p in paths_ended_in_v[vj]
                            if not p.extended
                            and all(not (p < p_) for p_ in paths_ended_in_v[vj])
                        ]
        if update_flags[vi]:
            queue.extend(graph[vi])


    for v in graph.keys():
        paths_ended_in_v[v] = [
            p
            for p in paths_ended_in_v[v]
            if not p.extended
            and all(not (p < p_) for p_ in paths_ended_in_v[v] if p != p_)
        ]
    return paths_ended_in_v


def scc_entry_exit_paths_extraction(
    scc_internal_prime_paths: set[Path], v_en: str, v_ex: str
):
    """
    Algorithm 2 from [1]
    """
    entry_exit_paths = set()
    if v_en == v_ex:
        return [Path([v_en])]

    for path in scc_internal_prime_paths:
        if v_en in path and v_ex in path:
            v_en_index = path.index(v_en)
            v_ex_index = path.index(v_ex)

            entry_exit_paths.add(path[v_en_index : v_ex_index + 1])

    copy_of_entry_exit_paths = set(entry_exit_paths)

    for p in copy_of_entry_exit_paths:
        for k in copy_of_entry_exit_paths:
            if p != k and k < p:
                if k in entry_exit_paths:
                    entry_exit_paths.remove(k)
    return entry_exit_paths


def scc_exit_paths_extraction(scc_internal_prime_paths: set[Path], v_ex: str):
    """
    Algorithm 3 from [1]
    """
    exit_paths = set()
    for path in scc_internal_prime_paths:
        if v_ex in path and not (path.is_cycle and path[0] == v_ex):
            v_ex_index = path.index(v_ex)
            exit_paths.add(path[: v_ex_index + 1])

    copy_of_exit_paths = set(exit_paths)

    for p in copy_of_exit_paths:
        for k in copy_of_exit_paths:
            if p != k and k < p:
                if k in exit_paths:
                    exit_paths.remove(k)
    return exit_paths


def scc_entry_paths_extraction(scc_internal_prime_paths: set[Path], v_en: str):
    """
    Algorithm 4 from [1]
    """
    entry_paths = set()
    for path in scc_internal_prime_paths:
        if v_en in path and not (path.is_cycle and path[0] == v_en):
            v_en_index = path.index(v_en)
            entry_paths.add(path[v_en_index:])

    copy_of_exit_paths = set(entry_paths)

    for p in copy_of_exit_paths:
        for k in copy_of_exit_paths:
            if p != k and k < p:
                if k in entry_paths:
                    entry_paths.remove(k)
    return entry_paths


def check_incoming(incoming: str, q: Path, scc_dict: dict[str, SCC], graph: dict):
    """
    Helper for incoming node for q.
    """
    match incoming:
        case _ if incoming.startswith("SCC"):
            return any(
                q[0] in graph[node_id] for node_id in scc_dict[incoming].scc_exit_nodes
            )
        case _:
            return q[0] in graph[incoming]


def check_outgoing(outgoing: str, q: Path, scc_dict: dict[str, SCC], graph: dict):
    """
    Helper for outgoing node for q.
    """
    match outgoing:
        case _ if outgoing.startswith("SCC"):
            return any(
                node_id in graph[q[-1]]
                for node_id in scc_dict[outgoing].scc_entry_nodes
            )
        case _:
            return outgoing in graph[q[-1]]


def can_tour(p: Path, q: Path, index: int, scc_dict: dict[str, SCC], graph: dict):
    """
    Helper for validation (q can tour p)
    """
    if index > 0 and index < len(p) - 1:
        incoming = p[index - 1]
        outgoing = p[index + 1]

        return check_incoming(incoming, q, scc_dict, graph) and check_outgoing(
            outgoing, q, scc_dict, graph
        )

    if index == 0:
        outgoing = p[index + 1]
        return check_outgoing(outgoing, q, scc_dict, graph)

    incoming = p[index - 1]
    return check_incoming(incoming, q, scc_dict, graph)


def cfg_complete_prime_paths_generation(
    prime_paths_of_ccfg: list[Path], scc_dict: dict[str, SCC], graph: dict
):
    """
    Algorithm 5 from [1]
    """
    queue = deque(prime_paths_of_ccfg)
    result = set()

    while queue:
        p = queue.popleft()
        expanded = False
        for scc_id, idx in p.get_scc_indexes().items():
            
            for q in scc_dict[scc_id].entry_exit_paths:
                if can_tour(p, q, idx, scc_dict, graph):
                    r = p.replace_node_with_path(q, idx)
                    queue.append(r)
                    expanded = True

        if not expanded and not (p[0].startswith("SCC") or p[-1].startswith("SCC")):
            result.add(p)

    return result


def scc_exit_prime_paths_generation(
    complete_prime_paths: set[Path], scc_dict: dict[str, SCC]
):
    """
    Algorithm 6 from [1]
    """
    result = set()

    for p in complete_prime_paths:
        for scc in p.get_scc_crossed_by_path(scc_dict):
            for q in scc.exit_paths:
                v_ex = q[-1]
                if v_ex in p:
                    index = p.index(v_ex)
                 
                    if p[index + 1] not in scc.nodes:
                        r = Path(q.path[:-1] + p.path[index:])
                        result.add(r)
    return result


def scc_entry_prime_paths_generation(
    complete_prime_paths: set[Path],
    scc_exit_prime_paths: set[Path],
    scc_dict: dict[str, SCC],
):
    """
    Algorithm 7 from [1]
    """
    result = set()

    for p in complete_prime_paths | scc_exit_prime_paths:
        for scc in p.get_scc_crossed_by_path(scc_dict):
            for q in scc.entry_paths:
                v_en = q[0]
                if v_en in p:
                    index = p.path.index(v_en)
                    if p[index-1] not in scc.nodes:
                        r = Path(p.path[:index] + q.path)
                        result.add(r)
    return result


def get_internal_prime_paths(scc_dict: dict[str, SCC]):
    """
    Returns cycles and prime paths that starts and ends in scc.
    """
    result = set()

    for scc in scc_dict.values():
        boundary = scc.scc_entry_nodes | scc.scc_exit_nodes
        for p in scc.internal_paths:
            start, end = p[0], p[-1]

            if p.is_cycle or (start not in boundary and end not in boundary):
                result.add(p)

    return result


def generate_prime_paths(graph: dict):
    """
    Yields all prime paths from the graph
    """
    
    all_paths = set()
    temp_graph = dict(graph)

    start_nodes = [node_id for node_id in graph.keys() if all(node_id not in outgoing for outgoing in graph.values())]

    starting_node = start_nodes[0]
    art_start = False

    #Modify graph to Single entry, if necessary
    if len(start_nodes) > 1:
        temp_graph["ARTIFICIAL_START"] = [node_id for node_id in graph.keys() if all(node_id not in outgoing for outgoing in graph.values())]
        starting_node = "ARTIFICIAL_START"
        art_start = True

    

    ccfg, scc_dict = get_ccfg_graph_and_scc_dict(temp_graph)

    prime_paths_of_ccfg = vertex_based_prime_paths_generation(ccfg, starting_node)

    non_empty_prime_paths = []

    for paths in prime_paths_of_ccfg.values():
        if paths:

            non_empty_prime_paths.extend(paths)

    complete_prime_paths = cfg_complete_prime_paths_generation(
        non_empty_prime_paths, scc_dict, graph
    )

    all_paths |= complete_prime_paths
    scc_exit_prime_paths = scc_exit_prime_paths_generation(
        complete_prime_paths, scc_dict
    )
    
    all_paths |= scc_exit_prime_paths

    scc_entry_prime_paths = scc_entry_prime_paths_generation(
        complete_prime_paths, scc_exit_prime_paths, scc_dict
    )
    all_paths |= scc_entry_prime_paths
    internal_prime_paths = get_internal_prime_paths(scc_dict)

    all_paths |= internal_prime_paths

    if art_start:
        for path in all_paths:
            yield path[1:]
    else:
        for path in all_paths:
            yield path



