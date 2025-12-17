from copy import deepcopy
from diblob.algorithms import PrimePathGenerator, ShortestPathBetween2Nodes
from testing_criterions.decorators import (
    validate_source,
    validate_sink,
    validate_reachability,
    validate_diblob,
)


class SimpleCycleCoverage:
    @validate_reachability()
    @validate_source()
    @validate_sink()
    @validate_diblob()

    def __init__(self, digraph_manager) -> None:
        self.digraph_manager = digraph_manager

    def get_shortest_path(self, shortest_path_dict: dict, node_id_x: str, node_id_y: str):
        if (node_id_x, node_id_y) in shortest_path_dict:
            return shortest_path_dict[(node_id_x, node_id_y)]
        shortest_path = ShortestPathBetween2Nodes.run(self.digraph_manager, node_id_x, node_id_y)
        shortest_path_dict[(node_id_x, node_id_y)] = shortest_path
        return shortest_path

    def get_test_cases(
        self, k: int, double_cycle: bool=False
    ):
        ppg = PrimePathGenerator(deepcopy(self.digraph_manager))
        shortest_path_dict = {}
        test_case = []

        cycle_counter = 0
        for cycle in ppg.get_cycles():
            cycle = [node_id for node_id in cycle]
            cycle_counter += 1
            if double_cycle:
                cycle = cycle + cycle[1:]
    
            if cycle_counter == 1:
                shortest_path_from_s = self.get_shortest_path(shortest_path_dict, "S", cycle[0])
                test_case += shortest_path_from_s + cycle[1:]
                if k == 1:
                    shortest_path_to_t = self.get_shortest_path(shortest_path_dict, test_case[-1], "T")
                    test_case += shortest_path_to_t[1:]
                    yield test_case
                    cycle_counter, test_case = 0, []

            else:
                shortest_path = self.get_shortest_path(shortest_path_dict, test_case[-1], cycle[0])

                if shortest_path is None:
                    shortest_path_to_t = self.get_shortest_path(shortest_path_dict, test_case[-1], "T")
                    test_case += shortest_path_to_t[1:]
                    yield test_case
                    shortest_path_from_s = self.get_shortest_path(shortest_path_dict, "S", cycle[0])
                    cycle_counter, test_case = 1, shortest_path_from_s + cycle[1:]
                
                elif cycle_counter == k:
                    shortest_path_to_t = self.get_shortest_path(shortest_path_dict, cycle[-1], "T")
                    test_case += shortest_path[1:] + cycle[1:] + shortest_path_to_t[1:]
                    yield test_case
                    cycle_counter, test_case = 0, []
                else:
                    test_case += shortest_path[1:] + cycle[1:]


        if cycle_counter != 0:
            test_case += self.get_shortest_path(shortest_path_dict, test_case[-1], "T")[1:]
            yield test_case
