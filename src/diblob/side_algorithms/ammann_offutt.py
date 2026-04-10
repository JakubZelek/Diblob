def is_simple_path(path):
    return (len(path) <= 1 or path[0] == path[-1]) or (len(set(path)) == len(path))

def is_cycle(path):
    return len(path) > 1 and  path[0] == path[-1]

def is_forward_extendable(path, graph):
    """Check if path can be extended forward while staying simple."""
    last = path[-1]
    for neighbor in graph["edges"].get(last, []):
        if neighbor not in path or neighbor == path[0]:
            return True
    return False


def extend_path(path, graph):
    """Generate all one-step forward extensions of path."""
    last = path[-1]
    extensions = []

    for neighbor in graph["edges"][last]:
        if neighbor not in path or neighbor == path[0]:
            extensions.append(path + (neighbor,))

    return extensions


def is_subpath(sub, full):
    """Check if sub is a contiguous subpath of full."""
    return "-".join(sub) + "-" in "-".join(full) + "-"


def get_prime_paths(graph):
    """
    Implementation of Ammann-Offutt prime path algorithm.
    graph = {
        "nodes": [...],
        "edges": {node: [neighbors]}
    }
    """
    # 1: P' = V (paths of length 0 → single nodes)
    p_prime = [(v,) for v in graph["nodes"]]

    # 2: T = emptyset
    temp_paths = []

    # 3: PP(G) = emptyset
    prime_paths_set = set()

    # 4: while P' != emptyset
    while p_prime:
        # 5: remove arbitrary path
        path = p_prime.pop()

        # 6: if simple and forward extendable
        if is_simple_path(path) and is_forward_extendable(path, graph) and not is_cycle(path):
            # 7: extend and add back to P'
            p_prime.extend(extend_path(path, graph))
        else:
            temp_paths.append(path)

    # 10: while T != emptyset
    while temp_paths:
        # 11: remove the longest path
        path = max(temp_paths, key=len)
        temp_paths.remove(path)

        # 12: add to PP(G)
        prime_paths_set.add(path)

        # 13: remove all subpaths of p from T
        temp_paths = [
            p for p in temp_paths if not is_subpath(p, path)
        ]

    # 14: return PP(G)
    return list(prime_paths_set)