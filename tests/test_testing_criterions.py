"""
Tests for testing criterions
"""

from diblob.digraph_manager import DigraphManager
from testing_criterions.NodeCoverage import NodeCoverage
from testing_criterions.EdgeCoverage import EdgeCoverage
from testing_criterions.SimpleCycleCoverage import SimpleCycleCoverage
from testing_criterions.SimplePathsCoverage import SimplePathsCoverage
from testing_criterions.PrimePathCoverage import PrimePathCoverage

PRIME_PATH_GRAPH = {
    "5": ["4"],
    "3": ["4"],
    "2": ["T"],
    "S": ["1"],
    "1": ["2", "3"],
    "4": ["5", "1"],
    "T": [],
}

SIMPLE_GRAPH = {
    "S": ["1"],
    "1": ["2", "3", "4"],
    "T": [],
    "6": ["1"],
    "4": ["5"],
    "3": ["5"],
    "5": ["6", "T"],
    "2": ["5"],
}

ONLINE_SHOP_GRAPH = {
    "Order": ["Login"],
    "ProductDetails": ["Catalog", "Order", "T"],
    "CreditCard": ["ValidatePayment"],
    "SearchProduct": ["ProductDetails"],
    "ValidatePayment": ["T", "InvalidPayment"],
    "ShopCard": ["ValidatePayment"],
    "ViewProduct": ["ProductDetails"],
    "Blik": ["ValidatePayment"],
    "OpenShop": ["Login", "SearchProduct", "Catalog"],
    "AddToCard": ["CheckOut"],
    "InvalidPayment": ["Order"],
    "S": ["OpenShop"],
    "Catalog": ["ViewProduct"],
    "T": [],
    "Payment": ["OnlineTransfer", "CreditCard", "Blik", "ShopCard"],
    "Login": ["AddToCard", "Catalog"],
    "OnlineTransfer": ["ValidatePayment"],
    "CheckOut": ["Payment"],
}


def nodes_covered(test_cases, digraph):
    """
    return True if all nodes are covered in the graph.
    """
    nodes = set()
    for test_case in test_cases:
        nodes |= set(test_case)

    dig_nodes = set(digraph.nodes)
    return nodes == dig_nodes


def edges_covered(test_cases, digraph):
    """
    return True if all nodes are covered in the graph.
    """
    edges = set()
    for test_case in test_cases:
        for node_x, node_y in zip(test_case, test_case[1:]):
            edges.add((node_x, node_y))

    dig_edges = set(digraph.edges)
    return edges - dig_edges, dig_edges - edges


def test_node_coverage():
    """
    Tests Node Coverage.
    """
    digraph_manager = DigraphManager({"B0": ONLINE_SHOP_GRAPH})
    node_coverage = NodeCoverage(digraph_manager)

    test_cases = [test_case for test_case in node_coverage.get_test_cases()]
    assert test_cases == [
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "OnlineTransfer",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "OnlineTransfer",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "CreditCard",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "ShopCard",
            "ValidatePayment",
            "T",
        ],
        ["S", "OpenShop", "Login", "Catalog", "ViewProduct", "ProductDetails", "T"],
        ["S", "OpenShop", "SearchProduct", "ProductDetails", "T"],
    ]

    assert nodes_covered(test_cases, digraph_manager)

    digraph_manager = DigraphManager({"B0": SIMPLE_GRAPH})
    node_coverage = NodeCoverage(digraph_manager)

    test_cases = [test_case for test_case in node_coverage.get_test_cases()]

    assert test_cases == [
        ["S", "1", "2", "5", "6", "1", "2", "5", "T"],
        ["S", "1", "2", "5", "T"],
        ["S", "1", "3", "5", "T"],
        ["S", "1", "4", "5", "T"],
    ]

    assert nodes_covered(test_cases, digraph_manager)


def test_edge_coverage():
    """
    Tests Edge Coverage.
    """

    digraph_manager = DigraphManager({"B0": ONLINE_SHOP_GRAPH})
    edge_coverage = EdgeCoverage(digraph_manager)

    test_cases = edge_coverage.get_test_cases_minimal_total_cost(
        cost_function={("Payment", "Blik"): 100}, default_cost=1
    )
    dif_1, dif_2 = edges_covered(test_cases, digraph_manager)

    assert not dif_1
    assert not dif_2
    test_cases = edge_coverage.get_test_cases_minimal_number_of_test_cases(
        cost_function={("Payment", "Blik"): 100}, default_cost=1
    )
    edges_covered(test_cases, digraph_manager)
    dif_1, dif_2 = edges_covered(test_cases, digraph_manager)

    assert not dif_1
    assert not dif_2

    test_cases = edge_coverage.get_test_cases_set_number_of_test_cases(
        k=4, cost_function={("Payment", "Blik"): 100}, default_cost=1
    )
    edges_covered(test_cases, digraph_manager)
    dif_1, dif_2 = edges_covered(test_cases, digraph_manager)

    assert not dif_1
    assert not dif_2

    digraph_manager = DigraphManager({"B0": SIMPLE_GRAPH})
    edge_coverage = EdgeCoverage(digraph_manager)

    test_cases = edge_coverage.get_test_cases_minimal_number_of_test_cases(
        cost_function={("5", "6"): 10, ("6", "1"): 10}, default_cost=1
    )
    assert len(test_cases) == 1

    test_cases = edge_coverage.get_test_cases_minimal_total_cost(
        cost_function={("5", "6"): 10, ("6", "1"): 10}, default_cost=1
    )
    assert len(test_cases) == 2

    test_cases = edge_coverage.get_test_cases_set_number_of_test_cases(
        cost_function={("5", "6"): 10, ("6", "1"): 10}, default_cost=2, k=3
    )
    assert len(test_cases) == 3


def test_cycle_coverage():
    """
    Tests Cycle Coverage.
    """
    digraph_manager = DigraphManager({"B0": ONLINE_SHOP_GRAPH})
    simple_cycle = SimpleCycleCoverage(digraph_manager)

    test_cases = [test_case for test_case in simple_cycle.get_test_cases(1)]
    assert test_cases == [
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "OnlineTransfer",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "CreditCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "ShopCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "Order",
            "Login",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "T",
        ],
    ]

    test_cases = [test_case for test_case in simple_cycle.get_test_cases(5)]
    assert test_cases == [
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "OnlineTransfer",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "CreditCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "ShopCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "Order",
            "Login",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "T",
        ],
    ]

    digraph_manager = DigraphManager({"B0": SIMPLE_GRAPH})
    simple_cycle = SimpleCycleCoverage(digraph_manager)

    test_cases = [test_case for test_case in simple_cycle.get_test_cases(1)]

    assert test_cases == [
        ["S", "1", "2", "5", "6", "1", "2", "5", "T"],
        ["S", "1", "3", "5", "6", "1", "2", "5", "T"],
        ["S", "1", "4", "5", "6", "1", "2", "5", "T"],
    ]

    test_cases = [test_case for test_case in simple_cycle.get_test_cases(5)]
    assert test_cases == [
        [
            "S",
            "1",
            "2",
            "5",
            "6",
            "1",
            "3",
            "5",
            "6",
            "1",
            "4",
            "5",
            "6",
            "1",
            "2",
            "5",
            "T",
        ]
    ]


def test_simple_path_coverage():
    """
    Tests Simple Path Coverage.
    """
    digraph_manager = DigraphManager({"B0": ONLINE_SHOP_GRAPH})
    simple_path = SimplePathsCoverage(digraph_manager)

    test_cases = [test_case for test_case in simple_path.get_test_cases(5)]
    assert test_cases == [
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "CreditCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "OnlineTransfer",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "CreditCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "CreditCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "ShopCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "OnlineTransfer",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "ShopCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "CreditCard",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "ShopCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "OnlineTransfer",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "CreditCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "ShopCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "OnlineTransfer",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "CreditCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "ShopCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "CreditCard",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "OnlineTransfer",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "ShopCard",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "CreditCard",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "CreditCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "ShopCard",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "ShopCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "T",
        ],
        ["S", "OpenShop", "Login", "Catalog", "ViewProduct", "ProductDetails", "T"],
        [
            "S",
            "OpenShop",
            "SearchProduct",
            "ProductDetails",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "OnlineTransfer",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "SearchProduct",
            "ProductDetails",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "SearchProduct",
            "ProductDetails",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "CreditCard",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "SearchProduct",
            "ProductDetails",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "SearchProduct",
            "ProductDetails",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "CreditCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "SearchProduct",
            "ProductDetails",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "ShopCard",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "SearchProduct",
            "ProductDetails",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "ShopCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "T",
        ],
        ["S", "OpenShop", "SearchProduct", "ProductDetails", "T"],
        [
            "S",
            "OpenShop",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "OnlineTransfer",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "CreditCard",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "OnlineTransfer",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "ShopCard",
            "ValidatePayment",
            "T",
        ],
        [
            "S",
            "OpenShop",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "Catalog",
            "ViewProduct",
            "ProductDetails",
            "T",
        ],
        ["S", "OpenShop", "Catalog", "ViewProduct", "ProductDetails", "T"],
        [
            "S",
            "OpenShop",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "OnlineTransfer",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "CreditCard",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "OnlineTransfer",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "Blik",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "OnlineTransfer",
            "ValidatePayment",
            "InvalidPayment",
            "Order",
            "Login",
            "AddToCard",
            "CheckOut",
            "Payment",
            "ShopCard",
            "ValidatePayment",
            "T",
        ],
    ]

    edges_covered(test_cases, digraph_manager)
    dif_1, dif_2 = edges_covered(test_cases, digraph_manager)
    assert not dif_1
    assert not dif_2

    digraph_manager = DigraphManager({"B0": SIMPLE_GRAPH})
    simple_path = SimplePathsCoverage(digraph_manager)

    test_cases = [test_case for test_case in simple_path.get_test_cases(1)]
    assert test_cases == [
        ["S", "1", "2", "5", "6", "1", "2", "5", "T"],
        ["S", "1", "2", "5", "T"],
        ["S", "1", "3", "5", "6", "1", "2", "5", "T"],
        ["S", "1", "3", "5", "T"],
        ["S", "1", "4", "5", "6", "1", "2", "5", "T"],
        ["S", "1", "4", "5", "T"],
        ["S", "1", "2", "5", "6", "1", "2", "5", "T"],
        ["S", "1", "2", "5", "6", "1", "3", "5", "T"],
        ["S", "1", "2", "5", "6", "1", "4", "5", "T"],
        ["S", "1", "4", "5", "6", "1", "2", "5", "T"],
        ["S", "1", "4", "5", "6", "1", "3", "5", "T"],
        ["S", "1", "3", "5", "6", "1", "2", "5", "T"],
        ["S", "1", "3", "5", "6", "1", "4", "5", "T"],
        ["S", "1", "2", "5", "6", "1", "3", "5", "T"],
        ["S", "1", "2", "5", "6", "1", "4", "5", "T"],
    ]
    dif_1, dif_2 = edges_covered(test_cases, digraph_manager)

    assert not dif_1
    assert not dif_2

    test_cases = [test_case for test_case in simple_path.get_test_cases(5)]
    assert test_cases == [
        ["S", "1", "2", "5", "T"],
        ["S", "1", "2", "5", "6", "1", "2", "5", "T"],
        ["S", "1", "3", "5", "T"],
        ["S", "1", "4", "5", "T"],
        ["S", "1", "4", "5", "6", "1", "2", "5", "T"],
        ["S", "1", "2", "5", "6", "1", "4", "5", "T"],
        [
            "S",
            "1",
            "4",
            "5",
            "6",
            "1",
            "3",
            "5",
            "6",
            "1",
            "2",
            "5",
            "6",
            "1",
            "3",
            "5",
            "6",
            "1",
            "4",
            "5",
            "6",
            "1",
            "2",
            "5",
            "6",
            "1",
            "3",
            "5",
            "6",
            "1",
            "2",
            "5",
            "6",
            "1",
            "4",
            "5",
            "T",
        ],
    ]
    dif_1, dif_2 = edges_covered(test_cases, digraph_manager)

    assert not dif_1
    assert not dif_2


def test_prime_path_coverage():
    digraph_manager = DigraphManager({"B0": PRIME_PATH_GRAPH})
    prime_path = PrimePathCoverage(digraph_manager)

    test_cases = [test_case for test_case in prime_path.get_test_cases(1)]
    assert test_cases == [
        ["S", "1", "3", "4", "1", "3", "4", "1", "2", "T"],
        ["S", "1", "3", "4", "5", "4", "5", "4", "1", "2", "T"],
        ["S", "1", "3", "4", "5", "4", "1", "2", "T"],
        ["S", "1", "3", "4", "5", "4", "1", "3", "4", "1", "2", "T"],
        ["S", "1", "3", "4", "1", "2", "T"],
        ["S", "1", "2", "T"],
        ["S", "1", "3", "4", "5", "4", "1", "2", "T"],
    ]

    test_cases = [test_case for test_case in prime_path.get_test_cases(5)]
    assert test_cases == [
        [
            "S",
            "1",
            "3",
            "4",
            "1",
            "3",
            "4",
            "1",
            "3",
            "4",
            "5",
            "4",
            "5",
            "4",
            "1",
            "2",
            "T",
        ],
        ["S", "1", "3", "4", "5", "4", "1", "2", "T"],
        ["S", "1", "2", "T"],
        ["S", "1", "3", "4", "1", "2", "T"],
    ]
