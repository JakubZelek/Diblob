"""
Tests for testing criterions
"""

from diblob.digraph_manager import DigraphManager
from testing_criterions.NodeCoverage import NodeCoverage


SIMPLE_GRAPH = {
    "S": ["1"],
    "1": ["2", "3", "4"],
    "T": [],
    "6": ["1"],
    "4": ["5"],
    "3": ["5"],
    "5": ["6", "T"],
    "2": ["5"]
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
    "CheckOut": ["Payment"]
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

def test_node_coverage():
    """
    Tests Node Coverage.
    """
    digraph_manager = DigraphManager({"B0": ONLINE_SHOP_GRAPH})
    node_coverage = NodeCoverage(digraph_manager)

    test_cases = node_coverage.get_test_cases()
 
    assert test_cases == [['S', 'OpenShop', 'Login', 'AddToCard', 'CheckOut', 'Payment', 'OnlineTransfer', 'ValidatePayment',
                           'InvalidPayment', 'Order', 'Login', 'Catalog', 'ViewProduct', 'ProductDetails', 'T'],
                          ['S', 'OpenShop', 'Login', 'AddToCard', 'CheckOut', 'Payment', 'CreditCard', 'ValidatePayment', 'T'],
                          ['S', 'OpenShop', 'Login', 'AddToCard', 'CheckOut', 'Payment', 'Blik', 'ValidatePayment', 'T'],
                          ['S', 'OpenShop', 'Login', 'AddToCard', 'CheckOut', 'Payment', 'ShopCard', 'ValidatePayment', 'T'],
                          ['S', 'OpenShop', 'SearchProduct', 'ProductDetails', 'T']]

    assert nodes_covered(test_cases, digraph_manager)

    digraph_manager = DigraphManager({"B0": SIMPLE_GRAPH})
    node_coverage = NodeCoverage(digraph_manager)
    
    test_cases = node_coverage.get_test_cases()

    assert test_cases == [['S', '1', '2', '5', '6', '1', '2', '5', 'T'], 
                         ['S', '1', '3', '5', 'T'], 
                         ['S', '1', '4', '5', 'T']]
    assert nodes_covered(test_cases, digraph_manager)

test_node_coverage()
