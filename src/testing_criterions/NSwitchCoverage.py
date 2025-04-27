from diblob import DigraphManager
from diblob.factory import DiblobFactory
from testing_criterions.EdgeCoverage import EdgeCoverage
from testing_criterions.decorators import (
    validate_source,
    validate_sink,
    validate_reachability,
    validate_cost_function,
    validate_diblob,
)
from testing_criterions.exceptions import InvalidNSwitchException


def generate_new_cost_function(digraph_manager, cost_function):

    n_switch_cost_function = {}

    for edge_id in digraph_manager.edges:

        edge_id_x, edge_id_y = edge_id

        edges_x = [
            (x, y) for x, y in zip(edge_id_x.split("|"), edge_id_x.split("|")[1:])
        ]
        edges_y = [
            (x, y) for x, y in zip(edge_id_y.split("|"), edge_id_y.split("|")[1:])
        ]

        cost = 0
        for x, y in zip(edges_x[::-1], edges_y):
            cost += cost_function[x]

            if x != y:
                cost += cost_function[y]

        suffix = (
            edges_y[len(edges_y) :]
            if len(edges_x) > len(edges_y)
            else edges_y[len(edges_x) :]
        )

        for elem in suffix:
            cost += cost_function[elem]

        n_switch_cost_function[edge_id] = cost

    return n_switch_cost_function


def map_n_switch_digraph_to_normal_one(digraph_json):
    mapping = {key: str(i) for i, key in enumerate(digraph_json)}
    reversed_mapping = {str(i): key for i, key in enumerate(digraph_json)}

    mapped_json = {
        mapping[key]: [mapping[val] for val in values]
        for key, values in digraph_json.items()
    }

    mapped_json["S"] = []
    mapped_json["T"] = []

    for key in digraph_json:
        if key.endswith("T"):
            mapped_json[mapping[key]].append("T")

        if key.startswith("S"):
            mapped_json["S"].append(mapping[key])

    return mapped_json, mapping, reversed_mapping


def map_n_switch_cost_function_to_normal_one(n_switch_cost_function, mapping):
    return {
        (mapping[edge_id[0]], mapping[edge_id[1]]): cost
        for edge_id, cost in n_switch_cost_function.items()
    }


def translate_test_cases(test_cases, reversed_mapping, n_switch):
    result_test_cases = []
    for test_case in test_cases:

        new_test_case = []
        prev_n_switch_node_id = None

        for node_id in test_case:

            if node_id in reversed_mapping:
                n_switch_id = reversed_mapping[node_id].split("|")

                if prev_n_switch_node_id is None:
                    new_test_case += n_switch_id
                else:
                    idx = 0
                    edges_x = [
                        (x, y)
                        for x, y in zip(
                            prev_n_switch_node_id, prev_n_switch_node_id[1:]
                        )
                    ]
                    edges_y = [(x, y) for x, y in zip(n_switch_id, n_switch_id[1:])]

                    while edges_x[::-1][idx] == edges_y[idx]:
                        idx += 1
                        if idx == n_switch - 1:
                            break

                    new_test_case += [idy[1] for idy in edges_y[idx:]]

                prev_n_switch_node_id = n_switch_id

        result_test_cases.append(new_test_case)
    return result_test_cases


class NSwitchCoverage:
    @validate_reachability()
    @validate_source()
    @validate_sink()
    @validate_diblob()
    def __init__(self, digraph_manager) -> None:
        self.digraph_manager = digraph_manager

    @staticmethod
    def generate_n_switch_graph(digraph_manager, n_switch):

        if n_switch < 2:
            raise InvalidNSwitchException(
                "n_switch should be at least equals to 2 or 3"
            )

        for reduce in range(n_switch - 1):
            digraph_manager = DiblobFactory.generate_edge_digraph(
                digraph_manager, reduce_value=reduce
            )
        return digraph_manager

    @staticmethod
    def return_n_switch_test_cases(test_cases):
        return [
            test_case[0].split("|") + [t.split("|")[-1] for t in test_case[1:]]
            for test_case in test_cases
        ]

    def generate_n_switch_artifacts(self, cost_function, default_cost, n_switch):
        cost_function = EdgeCoverage.fulfill_cost_function(
            self.digraph_manager, cost_function, default_cost
        )

        n_switch_graph = self.generate_n_switch_graph(self.digraph_manager, n_switch)
        n_switch_cost_function = generate_new_cost_function(
            n_switch_graph, cost_function
        )

        mapped_json, mapping, reversed_mapping = map_n_switch_digraph_to_normal_one(
            n_switch_graph("B0")["B0"]
        )
        n_switch_cost_function = map_n_switch_cost_function_to_normal_one(
            n_switch_cost_function, mapping
        )
        digraph_manager = DigraphManager({"B0": mapped_json})

        edge_coverage = EdgeCoverage(digraph_manager)
        return edge_coverage, reversed_mapping, n_switch_cost_function

    @validate_cost_function()
    def get_test_cases_minimal_total_cost(
        self, cost_function=None, default_cost=1, n_switch=2, cost_function_multiplier=1
    ):
        edge_coverage, reversed_mapping, n_switch_cost_function = (
            self.generate_n_switch_artifacts(cost_function, default_cost, n_switch)
        )

        test_cases = edge_coverage.get_test_cases_minimal_total_cost(
            cost_function=n_switch_cost_function,
            default_cost=default_cost,
            cost_function_multiplier=cost_function_multiplier,
        )
        test_cases = translate_test_cases(test_cases, reversed_mapping, n_switch)

        return test_cases

    @validate_cost_function()
    def get_test_cases_minimal_number_of_test_cases(
        self, cost_function=None, default_cost=1, n_switch=2, cost_function_multiplier=1
    ):
        edge_coverage, reversed_mapping, n_switch_cost_function = (
            self.generate_n_switch_artifacts(cost_function, default_cost, n_switch)
        )

        test_cases = edge_coverage.get_test_cases_minimal_number_of_test_cases(
            cost_function=n_switch_cost_function,
            default_cost=default_cost,
            cost_function_multiplier=cost_function_multiplier,
        )
        test_cases = translate_test_cases(test_cases, reversed_mapping, n_switch)
        return test_cases

    @validate_cost_function()
    def get_test_cases_set_number_of_test_cases(
        self,
        cost_function=None,
        default_cost=1,
        k=1,
        n_switch=2,
        cost_function_multiplier=1,
    ):
        edge_coverage, reversed_mapping, n_switch_cost_function = (
            self.generate_n_switch_artifacts(cost_function, default_cost, n_switch)
        )

        test_cases = edge_coverage.get_test_cases_set_number_of_test_cases(
            k=k,
            cost_function=n_switch_cost_function,
            default_cost=default_cost,
            cost_function_multiplier=cost_function_multiplier,
        )
        test_cases = translate_test_cases(test_cases, reversed_mapping, n_switch)
        return test_cases
