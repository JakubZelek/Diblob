from diblob import DigraphManager
from copy import deepcopy
from diblob.tools import cut_outgoing_edges
from diblob.algorithms import TarjanSSC, PrimePathsGenerator, GenerateDijkstraMatrix
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

    def get_test_cases(
        self, max_number_of_cycles_in_single_test_case, double_cycle=False
    ):

        digraph_manager = self.digraph_manager
        digraph_manager_to_compress = deepcopy(digraph_manager)
        trj = TarjanSSC(digraph_manager)
        dijkstra_matrix = GenerateDijkstraMatrix.run(digraph_manager)

        sc_components = trj.run()

        blob_id = 1
        cycle_iterator = 0
        path = ["S"]

        for scc in sc_components:
            if len(scc) > 1:
                str_blob_id = f"SubBlob{blob_id}"
                digraph_manager_to_compress.gather(str_blob_id, scc)
                ssc_dict = cut_outgoing_edges(digraph_manager_to_compress, str_blob_id)
                ssc_digraph_manager = DigraphManager(ssc_dict)

                ppg = PrimePathsGenerator(ssc_digraph_manager)
                reversed_translation_dict = ppg.reversed_translation_dict
                for cycle in ppg.get_cycles():

                    cycle_iterator += 1
                    potential_extension = dijkstra_matrix[
                        (path[-1], reversed_translation_dict[cycle[0]])
                    ]

                    if potential_extension:

                        trans_cycle = [reversed_translation_dict[c] for c in cycle]
                        path += potential_extension[1:-1] + trans_cycle

                        if double_cycle:
                            path += trans_cycle[1:]

                    elif path[-1] == reversed_translation_dict[cycle[0]]:

                        trans_cycle = [reversed_translation_dict[c] for c in cycle]
                        path += potential_extension[1:-1] + trans_cycle[1:]

                        if double_cycle:
                            path += trans_cycle[1:]

                    if cycle_iterator == max_number_of_cycles_in_single_test_case:

                        path += dijkstra_matrix[(path[-1], "T")][1:]
                        yield path
                        cycle_iterator = 0
                        path = ["S"]

        if path != ["S"]:
            path += dijkstra_matrix[(path[-1], "T")][1:]
            yield path
