"""
Exploratory tests for diblob. Tests combine functionality available in entire package.
"""

from diblob.digraph_manager import DigraphManager
from diblob.factory import DiblobFactory
from diblob.tools import display_digraph


def test_exploratory_dag_decomposition():
    """
    Steps:
        - create empty digraph.
        - add nodes A, B, C, D, E, F
        - create DAG adding edges
        - decompose graph to paths using edge graph (function composition)
    """

    digraph_manager = DigraphManager({"B0": {}})
    digraph_manager.add_nodes('A', 'B', 'C', 'D', 'E', 'F')
    digraph_manager.connect_nodes(('A', 'B'), ('A', 'C'), ('B', 'E'), ('C', 'D'),
                                  ('C', 'F'), ('D', 'E'),('D', 'F'))


    assert digraph_manager('B0') == {'B0': {'F': [],
                                            'E': [], 
                                            'D': ['E', 'F'], 
                                            'C': ['D', 'F'], 
                                            'A': ['B', 'C'], 
                                            'B': ['E']}}

    for reduce_value in range(3): # the longest path
        digraph_manager = DiblobFactory.generate_edge_digraph(digraph_manager, reduce_value)

    assert digraph_manager('B0') == {'B0': {'A|B|E': [],
                                            'A|C|F': [], 
                                            'A|C|D|E': [], 
                                            'A|C|D|F': []}}

def test_exploratory_diblobs():
    """
    Steps:
        - create empty digraph.
        - add nodes A, B, C, D, E, F, G
        - add some edges 
        - create diblobs B1 = {A, B}, B2 = {C, D}, B3 = {B1, B2, E}
        - create new two empty digraphs.
        - add nodes X, Y, Z to the first one 
        - add nodes P, Q, R to the second one
        - inject digraphs to the firstly created digraph
        - create new empty digraph
        - add nodes I, J, K
        - inject firstly created digraph to the new one
    """

    digraph_manager = DigraphManager({"B0": {}})
    digraph_manager.add_nodes('A', 'B', 'C', 'D', 'E', 'F', 'G')

    digraph_manager.connect_nodes(('A', 'B'), ('A', 'C'), ('B', 'E'), ('C', 'D'),
                                  ('C', 'F'), ('D', 'E'),('D', 'F'),
                                  ('E', 'G'), ('G', 'A'), ('G', 'C'))

    digraph_manager.gather('B1', {'A', 'B'})
    digraph_manager.gather('B2', {'C', 'D'})
    digraph_manager.gather('B3', {'B1', 'B2', 'E'})
    assert digraph_manager('B0') == {'B0': {'B3': {'B2': {'D': [{'B3': ['E']}, {'B0': ['F']}],
                                                          'C': ['D', {'B0': ['F']}]}, 
                                                   'E': [{'B0': ['G']}], 
                                                   'B1': {'B': [{'B3': ['E']}], 
                                                          'A': ['B', {'B2': ['C']}]}}, 
                                            'G': [{'B1': ['A']}, {'B2': ['C']}], 
                                            'F': []}}

    digraph_manager_xyz = DigraphManager({"C0": {}})
    digraph_manager_xyz.add_nodes('X', 'Y', 'Z')
    digraph_manager_xyz.connect_nodes(('X', 'Y'))

    digraph_manager_pqr = DigraphManager({"D0": {}})
    digraph_manager_pqr.add_nodes('P', 'Q', 'R')
    digraph_manager_pqr.connect_nodes(('P', 'Q'), ('Q', 'R'))

    digraph_manager.inject(digraph_manager_xyz, 'E')
    digraph_manager.inject(digraph_manager_pqr, 'C')

    digraph_manager.sorted()

    assert digraph_manager('B0') == {
                                    "B0": {
                                        "G": [{"B1": ["A"]}, {"D0": ["P", "Q", "R"]}],
                                        "F": [],
                                        "B3": {
                                            "C0": {
                                                "Z": [{"B0": ["G"]}],
                                                "X": ["Y", {"B0": ["G"]}],
                                                "Y": [{"B0": ["G"]}],
                                            },
                                            "B2": {
                                                "D0": {
                                                    "Q": ["R", {"B2": ["D"]}, {"B0": ["F"]}],
                                                    "R": [{"B2": ["D"]}, {"B0": ["F"]}],
                                                    "P": ["Q", {"B2": ["D"]}, {"B0": ["F"]}],
                                                },
                                                "D": [{"B0": ["F"]}, {"C0": ["X", "Y", "Z"]}],
                                            },
                                            "B1": {
                                                "B": [{"C0": ["X", "Y", "Z"]}],
                                                "A": ["B", {"D0": ["P", "Q", "R"]}],
                                            },
                                        },
                                    },
                                    }

    digraph_manager_ijk = DigraphManager({"E0": {}})
    digraph_manager_ijk.add_nodes('I', 'J', 'K')
    digraph_manager_ijk.inject(digraph_manager, 'I')

    digraph_manager.sorted()

    assert digraph_manager_ijk('B0') == {
                                        "B0": {
                                            "F": [],
                                            "B3": {
                                                "B2": {
                                                    "D0": {
                                                        "Q": ["R", {"B2": ["D"]}, {"B0": ["F"]}],
                                                        "R": [{"B2": ["D"]}, {"B0": ["F"]}],
                                                        "P": ["Q", {"B2": ["D"]}, {"B0": ["F"]}],
                                                    },
                                                    "D": [{"B0": ["F"]}, {"C0": ["X", "Y", "Z"]}],
                                                },
                                                "B1": {
                                                    "B": [{"C0": ["X", "Y", "Z"]}],
                                                    "A": ["B", {"D0": ["P", "Q", "R"]}],
                                                },
                                                "C0": {
                                                    "Y": [{"B0": ["G"]}],
                                                    "X": ["Y", {"B0": ["G"]}],
                                                    "Z": [{"B0": ["G"]}],
                                                },
                                            },
                                            "G": [{"B1": ["A"]}, {"D0": ["P", "Q", "R"]}],
                                        },
                                        }
