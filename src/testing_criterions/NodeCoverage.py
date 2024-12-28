from diblob import DigraphManager
from diblob.algorithms import DFS_with_path, DijkstraAlgorithm


class NodeCoverage:
    def __init__(self, digraph_manager) -> None:
        self.digraph_manager = digraph_manager

    def get_test_cases(self, starting_point, end_point, winnow_out = True):
        digraph_manager = self.digraph_manager
        dfs = DFS_with_path(digraph_manager)
        test_cases = dfs.run(starting_point)

        digraph_manager.reverse_edges(*[edge[0] for edge in digraph_manager.edges.values()])

        dijkstra = DijkstraAlgorithm(digraph_manager)
        min_distance_dict = dijkstra.run(end_point)

        for test_case in test_cases:
            node_id = test_case[-1]
            if node_id != end_point:
                test_case += [elem[0] for elem in min_distance_dict[node_id]['min_path']][::-1]
            
        if winnow_out:
            for idx, test_case in enumerate(test_cases):
                cover = {element for tc in test_cases for element in tc if tc != test_case}
                if set(test_case).issubset(cover):
                    test_cases.pop(idx)
        return test_cases


digraph_manager = DigraphManager({"B0": {}})
digraph_manager.add_nodes('S', 'T', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10')
digraph_manager.connect_nodes(('S', '1'), ('1', '2'), ('1', '3'), ('1', '4'), ('2', '5'), ('3', '5'), ('4', '5'),
                              ('5', '6'), ('6', '7'), ('7', '5'), ('6', '8'), ('8', '9'), ('9', '6'), ('9', '7'), ('7', '10'),
                              ('10', '9'), ('8', 'T'), ('9', 'T'), ('10', 'T'))

node_coverage = NodeCoverage(digraph_manager)
test_cases = node_coverage.get_test_cases('S', 'T')
print(test_cases)