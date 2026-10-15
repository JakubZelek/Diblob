from testing_criterions.CPTTestCasesGenerator import TestCasesGenerator
from testing_criterions.decorators import (
    validate_source,
    validate_sink,
    validate_reachability,
    validate_cost_function,
    validate_diblob,
)


class EdgeCoverage:
    @validate_reachability()
    @validate_source()
    @validate_sink()
    @validate_diblob()
    def __init__(self, digraph_manager) -> None:
        self.digraph_manager = digraph_manager

    @staticmethod
    def fulfill_cost_function(
        digraph_manager, cost_function, default_cost, cost_function_multiplier=1
    ):
        supplied_costs = cost_function or {}
        return {
            edge_id: supplied_costs.get(edge_id, default_cost)
            * cost_function_multiplier
            for edge_id in digraph_manager.edges
        }

    def get_cost(self, cost_function):
        criterion_edge_multiplier = 0
        for value in cost_function.values():
            if value > 1:
                criterion_edge_multiplier += value - 1
        return criterion_edge_multiplier

    @validate_cost_function()
    def get_test_cases_minimal_total_cost(
        self, cost_function=None, default_cost=1, cost_function_multiplier=1
    ):
        """Minimize the total cost of real graph-edge traversals.

        CPT-only source, sink, and reset edges have zero cost because they do
        not occur in the returned test cases.
        """

        cost_function = self.fulfill_cost_function(
            self.digraph_manager, cost_function, default_cost, cost_function_multiplier
        )
        tcs = TestCasesGenerator(
            self.digraph_manager,
            source="s_cpt",
            sink="t_cpt",
            cost_function=cost_function,
        )
        return tcs.generate_test_cases(
            k=1,
            minimal_edges_cost=0,
            maximal_edges_cost=0,
            sink_source_cost=0,
        )

    @validate_cost_function()
    def get_test_cases_minimal_number_of_test_cases(
        self, cost_function=None, default_cost=1, cost_function_multiplier=1
    ):

        cost_function = self.fulfill_cost_function(
            self.digraph_manager, cost_function, default_cost, cost_function_multiplier
        )
        criterion_edge_multiplier = self.get_cost(cost_function)

        multiplier = (
            criterion_edge_multiplier * (criterion_edge_multiplier + 3) / 2
        ) ** 3

        tcs = TestCasesGenerator(
            self.digraph_manager,
            source="s_cpt",
            sink="t_cpt",
            cost_function=cost_function,
        )
        return tcs.generate_test_cases(k=1, sink_source_cost=multiplier)

    @validate_cost_function()
    def get_test_cases_set_number_of_test_cases(
        self, cost_function=None, default_cost=1, k=1, cost_function_multiplier=1
    ):

        cost_function = self.fulfill_cost_function(
            self.digraph_manager, cost_function, default_cost, cost_function_multiplier
        )
        criterion_edge_multiplier = self.get_cost(cost_function)

        multiplier = criterion_edge_multiplier * (criterion_edge_multiplier + 3) / 2
        multiplier = (multiplier**2) * (k + multiplier)

        tcs = TestCasesGenerator(
            self.digraph_manager,
            source="s_cpt",
            sink="t_cpt",
            cost_function=cost_function,
        )
        return tcs.generate_test_cases(k=k, sink_source_cost=multiplier)
