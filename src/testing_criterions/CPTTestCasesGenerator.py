from copy import deepcopy
from testing_criterions import CPTDigraphManager
from testing_criterions.exceptions import (
    InvalidSinkSourceException,
    LackOfEdgeElementException,
)


class TestCasesGenerator:
    """
    Generates test cases for criterions which can be served by CPT algorithm.
    """

    def __init__(
        self, digraph_manager, source="S", sink="T", cost_function=None, default_cost=1
    ) -> None:

        if cost_function is None:
            cost_function = {}

        if source in digraph_manager or sink in digraph_manager:
            raise InvalidSinkSourceException(
                "Sink and sources should be unique over digraph namespace!"
            )

        self.source = source
        self.sink = sink
        self.digraph_manager = digraph_manager

        dict_json_representation = dict(digraph_manager(digraph_manager.root_diblob_id))
        self.cpt = CPTDigraphManager(
            dict_json_representation,
            cost_function={
                edge_id: cost_function.get(edge_id, default_cost)
                for edge_id in digraph_manager.edges
            },
        )

        self.minimal_elements, self.maximal_elements = self.cpt.get_edge_elements()
        if not self.minimal_elements or not self.maximal_elements:
            raise LackOfEdgeElementException(
                "Should be at least one minimal/maximal element in the diblob!"
            )

    def __get_additional_nodes_and_edges(self, k):
        sink = self.sink
        source = self.source

        nodes_to_add = [sink + source + str(number) for number in range(k)] + [
            sink,
            source,
        ]

        minimal_edges = [(self.source, node_id) for node_id in self.minimal_elements]
        maximal_edges = [(node_id, self.sink) for node_id in self.maximal_elements]

        sink_source_edges = [
            (sink, sink + source + str(number)) for number in range(k)
        ] + [(sink + source + str(number), source) for number in range(k)]

        return nodes_to_add, minimal_edges, maximal_edges, sink_source_edges

    def __get_cost(self, edge_list, cost):
        return {edge_id: cost for edge_id in edge_list}

    def __set_params(
        self, k, minimal_edges_cost=1, maximal_edges_cost=1, sink_source_cost=1
    ):
        """ "Case 1: Minimal total number of test cases."""
        cpt = deepcopy(self.cpt)
        nodes_to_add, minimal_edges, maximal_edges, sink_source_edges = (
            self.__get_additional_nodes_and_edges(k)
        )
        edges = minimal_edges + maximal_edges + sink_source_edges

        cpt.add_nodes(*nodes_to_add)
        cpt.connect_nodes(*edges)

        cpt.update_cost_function(
            self.__get_cost(minimal_edges, cost=minimal_edges_cost)
        )
        cpt.update_cost_function(
            self.__get_cost(maximal_edges, cost=maximal_edges_cost)
        )
        cpt.update_cost_function(
            self.__get_cost(sink_source_edges, cost=sink_source_cost)
        )

        return cpt

    def __extract_test_cases(self, test_cases):
        test_case_list = []
        test_case = []
        skip_flag = False

        for elem in test_cases:
            if not skip_flag and elem[1] != self.sink:
                test_case.append(elem[1])
            if elem[1] == self.sink:
                test_case_list.append(test_case)
                test_case = []
                skip_flag = True
            if elem[1] == self.source:
                skip_flag = False

        return test_case_list

    def generate_test_cases(
        self, k, maximal_edges_cost=1, minimal_edges_cost=1, sink_source_cost=1
    ):
        """generates test cases based on delivered setting.

        Args:
            k (int): the number of test cases will be generated. Sometimes minimal
            number of test cases is less than delivered k.
            Then the minimal number of test cases is computed.
            maximal_edges_cost (int, optional): cost of the edges with the form (_, sink).
            minimal_edges_cost (int, optional): cost of the edges with the form (source, _).
            sink_source_cost (int, optional): cost of the edges with the form (sink, _), (_, source).

        Returns:
            list(list): generated test cases.
        """
        cpt = self.__set_params(
            k, minimal_edges_cost, maximal_edges_cost, sink_source_cost
        )
        test_cases, _ = cpt.compute_cpt(start_node=self.source)
        return self.__extract_test_cases(test_cases)
