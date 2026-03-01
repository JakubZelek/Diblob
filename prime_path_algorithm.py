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
        return self.path[index]

    def __len__(self):
        return len(self.path)

    def __contains__(self, item):
        return item in self.path

    def __lt__(self, other):
        return "-".join(self.path) in "-".join(other.path)

    def __repr__(self):
        return str(self.path)


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




for i in range(1, 40):
    s = time.time()
    d = generate_diamond(i)
    algorithm_1(d, "B0")
    t = time.time()
    print(i, 2**i, t-s)


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
