from dataclasses import dataclass
import time

@dataclass
class Path:
    path: list
    read_by_vertex: set
    extended: bool
    is_cycle: bool

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
        return self.path.index(value)
    
    def replace(self, index, path: Path):
        return Path 


def algorithm_1(G: dict, s: str):
    paths_ended_in_v = {
        key: [Path(path=[key], read_by_vertex=set(), extended=False, is_cycle=False)]
        for key in G.keys()
    }
    update_flags = {key: False for key in G.keys()}
    reversed_G = {key: [] for key in G.keys()}

    for key, value in G.items():
        for v in value:
            reversed_G[v].append(key)

    queue = [s]

    while queue:
        vi = queue.pop(0)
        update_flags[vi] = False

        if vi == s:
            queue.extend(G[vi])

        for vj in reversed_G[vi]:
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
                        for succ in G[vj]
                    ):
                        paths_ended_in_v[vj] = [
                            p
                            for p in paths_ended_in_v[vj]
                            if not p.extended
                            and all(not (p < p_) for p_ in paths_ended_in_v[vj])
                        ]
        if update_flags[vi]:
            queue.extend(G[vi])

    for v in G.keys():
        paths_ended_in_v[v] = [
            p
            for p in paths_ended_in_v[v]
            if not p.extended
            and all(not (p < p_) for p_ in paths_ended_in_v[v] if p != p_)
        ]

    return paths_ended_in_v


def get_scc_internal_prime_paths(scc: dict):
    scc_prime_paths = set()
    for v in scc.keys():
        paths_ended_in_v = algorithm_1(scc, v)
        for values in paths_ended_in_v.values():
            scc_prime_paths |= set(values)
    return scc_prime_paths


def algorithm_2(scc_internal_prime_paths: set[Path], v_en: str, v_ex: str):
    entry_exit_paths = set()
    if v_en == v_ex:
        return v_en
    
    for path in scc_internal_prime_paths:
        if v_en in path and v_ex in path:
            v_en_index = path.index(v_en)
            v_ex_index = path.index(v_ex)
            
            entry_exit_paths.add(path[v_en_index:v_ex_index + 1])
    
    copy_of_entry_exit_paths = set(entry_exit_paths)

    for p in copy_of_entry_exit_paths:
        for k in copy_of_entry_exit_paths:
            if p != k and k < p:
                if k in entry_exit_paths:
                    entry_exit_paths.remove(k)
    return entry_exit_paths


def algorithm_3(scc_internal_prime_paths: set[Path], v_ex: str):
    exit_paths = set()
    for path in scc_internal_prime_paths:
        if v_ex in path and not (path.is_cycle and path[0] == v_ex):
            v_ex_index = path.index(v_ex)
            exit_paths.add(path[:v_ex_index + 1])
    
    copy_of_exit_paths = set(exit_paths)

    for p in copy_of_exit_paths:
        for k in copy_of_exit_paths:
            if p != k and k < p:
                if k in exit_paths:
                    exit_paths.remove(k)
    return exit_paths

def algorithm_4(scc_internal_prime_paths: set[Path], v_en: str):
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


def algorithm_5(scc_entry_exit_paths: set[Path]):

def generate_diamond(k: int, start_label="B0") -> dict:
   
    graph = {}
    current_start = start_label
    counter = 1  

    for level in range(k):

        left = f"B{counter}"
        counter += 1
        right = f"B{counter}"
        counter += 1
        next_vertex = f"B{counter}"
        counter += 1

        graph[current_start] = [left, right]
        graph[left] = [next_vertex]
        graph[right] = [next_vertex]

        current_start = next_vertex
    graph[current_start] = []

    return graph




# for i in range(1, 40):
#     s = time.time()
#     d = generate_diamond(i)
#     algorithm_1(d, "B0")
#     t = time.time()
#     print(i, 2**i, t-s)


# from diblob.algorithms import PrimePathGenerator
# from diblob import DigraphManager



# for i in range(1, 40):
#     s = time.time()
#     d = generate_diamond(i)
#     graph = DigraphManager({"G0": d})
#     ppg = PrimePathGenerator(graph)

#     for c in ppg.get_cycles():
#         pass

#     for a in ppg.get_prime_paths_without_cycles():
#         pass
#     t = time.time()
#     print(i, 2**i, t-s)


scc = {"1": ["3"],
       "2": ["1"],
       "3": ["2", "4"],
       "4": ["6"],
       "6": ["5", "1"],
       "5": ["4"]}

internal_prime_paths = get_scc_internal_prime_paths(scc)

print(algorithm_2(internal_prime_paths, v_en="2", v_ex="5"))
print(algorithm_3(internal_prime_paths, v_ex="5"))
print(algorithm_4(internal_prime_paths, v_en="5"))