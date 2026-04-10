"""
Implementation for the prime paths generation from:
https://github.com/heshenghuan/Prime-Path-Coverage
"""


def is_prime_path(path, graph):
    """Whether a path is a prime path."""
    return (len(path) >= 2 and path[0] == path[-1]) or (
        reach_head(path, graph) and reach_end(path, graph)
    )


def reach_head(path, graph):
    """
    Whether the path can be extended at head, and the extended path is still
    a simple path.
    """
    former_nodes = filter(
        lambda node: path[0] in graph["edges"][node],
        graph["nodes"]
    )
    for node in former_nodes:
        if node not in path or node == path[-1]:
            return False
    return True


def reach_end(path, graph):
    """
    Whether the path can be extended at tail, and the extended path is still
    a simple path.
    """
    later_nodes = graph["edges"][path[-1]]
    for node in later_nodes:
        if node not in path or node == path[0]:
            return False
    return True


def is_extendable(path, graph):
    """Whether a path is extendable."""
    return not (is_prime_path(path, graph) or reach_end(path, graph))


def find_simple_paths(graph, current_paths, simple_paths):
    """Find the simple paths of a graph."""
    simple_paths.extend(filter(lambda p: is_prime_path(p, graph), current_paths))

    current_paths = filter(lambda p: is_extendable(p, graph), current_paths)
    new_paths = []

    for path in current_paths:
        for next_node in graph["edges"][path[-1]]:
            if next_node not in path or next_node == path[0]:
                new_paths.append(path + (next_node,))

    if len(new_paths) > 0:
        find_simple_paths(graph, new_paths, simple_paths)


def ammann_offutt_prime_paths(graph):
    """Find the prime paths of a graph."""
    current_paths = [(node,) for node in graph["nodes"]]
    simple_paths = []

    # recursively finding the simple paths of the graph
    find_simple_paths(graph, current_paths, simple_paths)

    return simple_paths
