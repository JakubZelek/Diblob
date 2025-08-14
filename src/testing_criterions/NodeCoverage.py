from diblob.algorithms import DFS_with_path, DijkstraAlgorithm
from copy import deepcopy
from testing_criterions.decorators import (
    validate_source,
    validate_sink,
    validate_reachability,
    validate_diblob,
)


class NodeCoverage:
    """
    Node coverage criterion.
    """

    @validate_reachability()
    @validate_source()
    @validate_sink()
    @validate_diblob()
    def __init__(self, digraph_manager) -> None:
        self.digraph_manager = digraph_manager

    def get_test_cases(self):
        """
        Returns test cases generated for node coverage.
        """
        starting_point = "S"
        end_point = "T"

        digraph_manager = deepcopy(self.digraph_manager)
        dfs = DFS_with_path(digraph_manager)
        test_cases = dfs.run(starting_point)

        digraph_manager.reverse_edges(
            *[edge[0] for edge in digraph_manager.edges.values()]
        )

        dijkstra = DijkstraAlgorithm(digraph_manager)
        min_distance_dict = dijkstra.run(end_point)

        for test_case in test_cases:
            node_id = test_case[-1]
            if node_id != end_point:
                test_case += [
                    elem[0] for elem in min_distance_dict[node_id]["min_path"]
                ][::-1]
            yield test_case
