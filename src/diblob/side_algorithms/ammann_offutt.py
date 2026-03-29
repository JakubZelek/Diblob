"""
Implementation for the prime paths generation from:
https://github.com/heshenghuan/Prime-Path-Coverage
"""


def isPrimePath(path, graph):
    """Whether a path is a prime path."""
    if len(path) >= 2 and path[0] == path[-1]:
        return True
    elif reachHead(path, graph) and reachEnd(path, graph):
        return True
    else:
        return False


def reachHead(path, graph):
    """
    Whether the path can be extended at head, and the extended path is still
    a simple path.
    """
    former_nodes = filter(lambda n: path[0] in graph[
                          'edges'][n], graph['nodes'])
    for n in former_nodes:
        if n not in path or n == path[-1]:
            return False
    return True


def reachEnd(path, graph):
    """
    Whether the path can be extended at tail, and the extended path is still
    a simple path.
    """
    later_nodes = graph['edges'][path[-1]]
    for n in later_nodes:
        if n not in path or n == path[0]:
            return False
    return True


def extendable(path, graph):
    """Whether a path is extendable."""
    if isPrimePath(path, graph) or reachEnd(path, graph):
        return False
    else:
        return True


def findSimplePath(graph, exPaths, paths=[]):
    """Find the simple paths of a graph."""
    paths.extend(filter(lambda p: isPrimePath(p, graph), exPaths))
    exPaths = filter(lambda p: extendable(p, graph), exPaths)
    newExPaths = []
    for p in exPaths:
        for nx in graph['edges'][p[-1]]:
            if nx not in p or nx == p[0]:
                newExPaths.append(p + (nx, ))
    if len(newExPaths) > 0:
        findSimplePath(graph, newExPaths, paths)


def ammann_offutt_prime_paths(graph):
    """Find the prime paths of a graph."""
    exPaths = [(n, ) for n in graph['nodes']]
    simplePaths = []
    # recursively finding the simple paths of the graph
    findSimplePath(graph, exPaths, simplePaths)
    primePaths = sorted(simplePaths, key=lambda a: (len(a), a))

    return primePaths

def rotate_cycle(cycle):
    """
    Given a cycle like [A, B, C, D, A],
    return all its rotations:
    [A, B, C, D, A], [B, C, D, A, B], ...
    """
    base = cycle[:-1]
    rotations = []
    n = len(base)
    for i in range(n):
        rotated = base[i:] + base[:i] + [base[i]]
        rotations.append(rotated)
    return rotations
 