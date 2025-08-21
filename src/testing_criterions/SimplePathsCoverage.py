from diblob.algorithms import PrimePathsGenerator, GenerateDijkstraMatrix
from testing_criterions.decorators import (
    validate_source,
    validate_sink,
    validate_reachability,
    validate_diblob,
)


class SimplePathsCoverage:
    @validate_reachability()
    @validate_source()
    @validate_sink()
    @validate_diblob()
    def __init__(self, digraph_manager) -> None:
        self.digraph_manager = digraph_manager

    def get_test_cases(self, max_number_of_simple_paths_in_single_test_case):

        digraph_manager = self.digraph_manager
        dijkstra_matrix = GenerateDijkstraMatrix.run(digraph_manager)

        simple_path_iterator = 0
        path = ["S"]
        skip_flag = False

        ppg = PrimePathsGenerator(digraph_manager)
        reversed_translation_dict = ppg.reversed_translation_dict
        for simple_path in ppg.get_prime_paths_without_cycles():
            if simple_path:
                if (
                    reversed_translation_dict[simple_path[0]] == "S"
                    and reversed_translation_dict[simple_path[-1]] == "T"
                ):
                    yield [reversed_translation_dict[x] for x in simple_path]
                    continue

                simple_path_iterator += 1
                potential_extension = dijkstra_matrix[
                    (path[-1], reversed_translation_dict[simple_path[0]])
                ]

                if potential_extension:
                    trans_cycle = [reversed_translation_dict[sp] for sp in simple_path]
                    path += potential_extension[1:-1] + trans_cycle

                elif path[-1] == reversed_translation_dict[simple_path[0]]:
                    trans_cycle = [reversed_translation_dict[sp] for sp in simple_path]
                    path += potential_extension[1:-1] + trans_cycle[1:]

                else:
                    skip_flag = True

                if (
                    skip_flag
                    or simple_path_iterator == max_number_of_simple_paths_in_single_test_case
                ):
                    path += dijkstra_matrix[(path[-1], "T")][1:]
                    if path[1] == "S":
                        yield path[1:]
                    else:
                        yield path
                    simple_path_iterator = 0
                    path = ["S"]
                    skip_flag = False

        if path != ["S"]:
            path += dijkstra_matrix[(path[-1], "T")][1:]
            if path[1] == "S":
                yield path[1:]
            else:
                yield path
