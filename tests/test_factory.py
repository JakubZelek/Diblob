"""
Diblob factory tests.
"""


from diblob.digraph_manager import DigraphManager
from diblob.factory import DiblobFactory


def test_edge_graph():
    """
    test for edge digraph creation.
    """
    digraph_manager = DigraphManager({"B0": {"A": ["B", "F"],
                                             "B": ["C", "D", "E"],
                                             "C": ["D"],
                                             "D": ["E", "F", "G"],
                                             "E": ["F", "A"],
                                             "F": ["G", "B"],
                                             "G": ["A", "D"]}})

    digraph_manager = DiblobFactory.generate_edge_digraph(digraph_manager)
    digraph_manager.sorted()

    assert digraph_manager('B0') == {'B0': {'B|D': ['D|E', 'D|F', 'D|G'],
                                            'B|E': ['E|A', 'E|F'], 
                                            'F|B': ['B|C', 'B|D', 'B|E'], 
                                            'G|D': ['D|E', 'D|F', 'D|G'], 
                                            'D|E': ['E|A', 'E|F'], 
                                            'A|F': ['F|B', 'F|G'], 
                                            'C|D': ['D|E', 'D|F', 'D|G'], 
                                            'D|G': ['G|A', 'G|D'], 
                                            'F|G': ['G|A', 'G|D'], 
                                            'G|A': ['A|B', 'A|F'], 
                                            'D|F': ['F|B', 'F|G'], 
                                            'E|A': ['A|B', 'A|F'], 
                                            'B|C': ['C|D'], 
                                            'A|B': ['B|C', 'B|D', 'B|E'], 
                                            'E|F': ['F|B', 'F|G']}}


    digraph_manager = DiblobFactory.generate_edge_digraph(digraph_manager, reduce_value=1)
    digraph_manager.sorted()

    assert digraph_manager('B0') == {'B0': {'F|G|A': ['G|A|B', 'G|A|F'], 
                                            'G|D|F': ['D|F|B', 'D|F|G'], 
                                            'B|E|A': ['E|A|B', 'E|A|F'], 
                                            'C|D|G': ['D|G|A', 'D|G|D'], 
                                            'G|A|F': ['A|F|B', 'A|F|G'], 
                                            'A|F|B': ['F|B|C', 'F|B|D', 'F|B|E'], 
                                            'F|B|E': ['B|E|A', 'B|E|F'], 
                                            'B|D|G': ['D|G|A', 'D|G|D'], 
                                            'C|D|F': ['D|F|B', 'D|F|G'], 
                                            'D|E|F': ['E|F|B', 'E|F|G'], 
                                            'D|G|D': ['G|D|E', 'G|D|F', 'G|D|G'], 
                                            'F|B|D': ['B|D|E', 'B|D|F', 'B|D|G'], 
                                            'A|B|D': ['B|D|E', 'B|D|F', 'B|D|G'], 
                                            'E|A|B': ['A|B|C', 'A|B|D', 'A|B|E'], 
                                            'C|D|E': ['D|E|A', 'D|E|F'], 
                                            'A|B|C': ['B|C|D'], 
                                            'D|F|G': ['F|G|A', 'F|G|D'], 
                                            'D|G|A': ['G|A|B', 'G|A|F'], 
                                            'G|A|B': ['A|B|C', 'A|B|D', 'A|B|E'], 
                                            'E|F|G': ['F|G|A', 'F|G|D'], 
                                            'G|D|E': ['D|E|A', 'D|E|F'], 
                                            'B|E|F': ['E|F|B', 'E|F|G'], 
                                            'F|B|C': ['B|C|D'], 
                                            'F|G|D': ['G|D|E', 'G|D|F', 'G|D|G'],
                                            'B|C|D': ['C|D|E', 'C|D|F', 'C|D|G'], 
                                            'A|B|E': ['B|E|A', 'B|E|F'], 
                                            'A|F|G': ['F|G|A', 'F|G|D'], 
                                            'E|A|F': ['A|F|B', 'A|F|G'], 
                                            'D|E|A': ['E|A|B', 'E|A|F'], 
                                            'D|F|B': ['F|B|C', 'F|B|D', 'F|B|E'], 
                                            'G|D|G': ['D|G|A', 'D|G|D'], 
                                            'B|D|F': ['D|F|B', 'D|F|G'], 
                                            'B|D|E': ['D|E|A', 'D|E|F'], 
                                            'E|F|B': ['F|B|C', 'F|B|D', 'F|B|E']}}

    digraph_manager = DigraphManager({"B0": {"A": ["B"],
                                             "B": ["C"],
                                             "C": ["D"],
                                             "D": ["E"],
                                             "E": ["A"]}})

    digraph_manager = DiblobFactory.generate_edge_digraph(digraph_manager)
    assert digraph_manager('B0') == {'B0': {'C|D': ['D|E'],
                                            'D|E': ['E|A'], 
                                            'E|A': ['A|B'], 
                                            'A|B': ['B|C'], 
                                            'B|C': ['C|D']}}

    digraph_manager = DiblobFactory.generate_edge_digraph(digraph_manager, 1)
    assert digraph_manager('B0') == {'B0': {'A|B|C': ['B|C|D'],
                                            'B|C|D': ['C|D|E'], 
                                            'D|E|A': ['E|A|B'], 
                                            'E|A|B': ['A|B|C'], 
                                            'C|D|E': ['D|E|A']}}

    digraph_manager = DiblobFactory.generate_edge_digraph(digraph_manager, 2)
    assert digraph_manager('B0') == {'B0': {'B|C|D|E': ['C|D|E|A'],
                                            'A|B|C|D': ['B|C|D|E'], 
                                            'C|D|E|A': ['D|E|A|B'], 
                                            'E|A|B|C': ['A|B|C|D'], 
                                            'D|E|A|B': ['E|A|B|C']}}

    digraph_manager = DiblobFactory.generate_edge_digraph(digraph_manager, 3)
    assert digraph_manager('B0') == {'B0': {'B|C|D|E|A': ['C|D|E|A|B'],
                                            'C|D|E|A|B': ['D|E|A|B|C'], 
                                            'E|A|B|C|D': ['A|B|C|D|E'], 
                                            'D|E|A|B|C': ['E|A|B|C|D'], 
                                            'A|B|C|D|E': ['B|C|D|E|A']}}

    digraph_manager = DiblobFactory.generate_edge_digraph(digraph_manager, 4)
    assert digraph_manager('B0') == {'B0': {'C|D|E|A|B|C': ['D|E|A|B|C|D'],
                                            'A|B|C|D|E|A': ['B|C|D|E|A|B'], 
                                            'E|A|B|C|D|E': ['A|B|C|D|E|A'], 
                                            'D|E|A|B|C|D': ['E|A|B|C|D|E'], 
                                            'B|C|D|E|A|B': ['C|D|E|A|B|C']}}


    digraph_manager = DigraphManager({"B0": {"A": ["B"],
                                             "B": ["C"],
                                             "C": ["D"],
                                             "D": ["E"],
                                             "E": []}})

    digraph_manager = DiblobFactory.generate_edge_digraph(digraph_manager)
    digraph_manager = DiblobFactory.generate_edge_digraph(digraph_manager,1)
    digraph_manager = DiblobFactory.generate_edge_digraph(digraph_manager,2)
    digraph_manager = DiblobFactory.generate_edge_digraph(digraph_manager,3)

    assert digraph_manager('B0') == {'B0': {'A|B|C|D|E': []}}
    digraph_manager = DiblobFactory.generate_edge_digraph(digraph_manager,4)

    assert digraph_manager('B0') == {'B0': {'A|B|C|D|E': []}}


def test_bipartite_digraph():
    """
    test for bipartite digraph creation.
    """
    digraph_manager = DigraphManager({"B0": {"A": ["B", "F"],
                                             "B": ["C", "D", "E"],
                                             "C": ["D"],
                                             "D": ["E", "F", "G"],
                                             "E": ["F", "A"],
                                             "F": ["G", "B"],
                                             "G": ["A", "D"] }})

    digraph_manager = DiblobFactory.generate_bipartite_digraph(digraph_manager)
    assert digraph_manager('B0') == {'B0': {'B`': ['C``', 'D``', 'E``'], 
                                            'G``': [], 
                                            'D`': ['E``', 'F``', 'G``'], 
                                            'F`': ['B``', 'G``'], 
                                            'C`': ['D``'], 
                                            'F``': [], 
                                            'C``': [], 
                                            'G`': ['A``', 'D``'], 
                                            'D``': [], 
                                            'E``': [], 
                                            'B``': [], 
                                            'E`': ['A``', 'F``'], 
                                            'A``': [], 
                                            'A`': ['B``', 'F``']}}

def test_flow_digraph():
    """
    test for flow digraph creation.
    """
    digraph_manager = DigraphManager({"B0": {"A": ["D"],
                                             "B": ["D"],
                                             "C": ["D"],
                                             "D": ["E", "F"],
                                             "E": ["G", "H"],
                                             "F": ["H", "I"],
                                             "G": ["J"],
                                             "H": ["J"],
                                             "I": ["J"],
                                             "J": []}})

    flow_digraph_manager = DiblobFactory.generate_flow_digraph(digraph_manager)
    flow_digraph_manager.sorted()

    assert flow_digraph_manager('B0') == {'B0': {'B``': ['D`'],
                                                 'A``': ['D`'], 
                                                 'C`': ['C``'], 
                                                 'G`': ['G``'], 
                                                 'I`': ['I``'], 
                                                 'C``': ['D`'], 
                                                 'F``': ['H`', 'I`'], 
                                                 'F`': ['F``'], 
                                                 'J`': ['J``'], 
                                                 'H``': ['J`'], 
                                                 'D``': ['E`', 'F`'], 
                                                 'E``': ['G`', 'H`'], 
                                                 'A`': ['A``'], 
                                                 'D`': ['D``'], 
                                                 'G``': ['J`'], 
                                                 'I``': ['J`'], 
                                                 'H`': ['H``'], 
                                                 'B`': ['B``'], 
                                                 'J``': [], 
                                                 'E`': ['E``']}}
