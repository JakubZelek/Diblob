# pylint: disable=redefined-outer-name
"""
Diblob digraph_manager tests. 
"""

import os
import json
import pytest
from diblob.digraph_manager import DigraphManager
from diblob.exceptions import (InvalidDigraphDictException,
                               RemoveRootDiblobException,
                               CommonResourcesInjection,
                               IllegalJoinException)

DIGRAPHS_PATH = 'tests/digraphs'

@pytest.fixture()
def digraph_dict():
    """
    Reads digraphs json representations from test/graphs dictionary.
    Representations are used in tests.
    """
    digraphs_dict = {}

    for file_name in os.listdir(DIGRAPHS_PATH):
        with open(f"{DIGRAPHS_PATH}/{file_name}", 'r', encoding='utf-8') as file:
            digraphs_dict[file_name.split('.')[0]] = json.load(file)

    yield digraphs_dict


def test_invalid_json(digraph_dict):
    """
    Tests invalid json digraphs.
    """

    with pytest.raises(InvalidDigraphDictException):
        DigraphManager(digraph_dict['g0_empty_json'])

    with pytest.raises(InvalidDigraphDictException):
        DigraphManager(digraph_dict['g10_json_without_diblob'])


def test_empty_graph(digraph_dict):
    """
    Constructs digraphs based on empty digraph. Then nodes/edges are added
    and diblob operations are performed. In the end of chain operations we 
    get empty digraph again. 

    test covers digraphs only (not pseudographs)
    """

    digraph_manager = DigraphManager(digraph_dict['g1_empty_graph'])
    assert digraph_manager('B0') == {"B0": {}}

    digraph_manager.add_nodes('A', 'B', 'C', 'D', 'E')
    assert set(digraph_manager.nodes) == {'A', 'B', 'C', 'D', 'E'}

    digraph_manager.connect_nodes(('A', 'B'), ('B', 'C'), ('A', 'D'), ('D', 'E'))
    assert set(digraph_manager.edges) == {('A', 'B'), ('B','C'), ('A', 'D'), ('D', 'E')}

    digraph_manager.gather('B1', {'A', 'B', 'C', 'D'})
    digraph_manager.gather('B2', {'A', 'B'})

    assert set(digraph_manager.diblobs) == {'B0', 'B1', 'B2'}
    assert digraph_manager('B0') == {"B0": {"B1": {"C": [],
                                                   "D": [{"B0": ["E"]}],
                                                   "B2": {"A": ["B", {"B1": ["D"]}],
                                                          "B": [{"B1": ["C"]}]}},
                                                   "E": []}}

    digraph_manager.reverse_edges(*[edge[0] for edge in digraph_manager.edges.values()])

    assert set(digraph_manager.edges) == {('B', 'A'), ('C','B'), ('D', 'A'), ('E', 'D')}
    assert digraph_manager('B0') == {"B0": {"B1": {"C": [{"B2": ["B"]}],
                                                   "D": [{"B2": ["A"]}],
                                                   "B2": {"A": [],
                                                          "B": ["A"]}},
                                                   "E": [{"B1": ["D"]}]}}

    with pytest.raises(RemoveRootDiblobException):
        digraph_manager.flatten('B0')

    digraph_manager.flatten('B1')

    assert set(digraph_manager.diblobs) == {'B0', 'B2'}

    assert digraph_manager('B0') == {"B0": {"C": [{"B2": ["B"]}],
                                                "D": [{"B2": ["A"]}],
                                                "B2": {"A": [],
                                                       "B": ["A"]},
                                                "E": ["D"]}}
    digraph_manager.flatten('B2')
    assert set(digraph_manager.diblobs) == {'B0'}
    assert digraph_manager('B0') == {"B0": {"C": ["B"],
                                                "D": ["A"],
                                                "A": [],
                                                "B": ["A"],
                                                "E": ["D"]}
                                        }
    digraph_manager.remove_edges(*[edge[0] for edge in digraph_manager.edges.values()])
    assert digraph_manager('B0') == {"B0": {"C": [],
                                          "D": [],
                                          "A": [],
                                          "B": [],
                                          "E": []}}

    digraph_manager.remove_nodes(*[node for node in digraph_manager.nodes.values()])
    assert digraph_manager('B0') == {"B0": {}}


def test_paths(digraph_dict):
    """
    test paths - paths are extended in the process and compressed by compress_edge method.
    """
    digraph_manager = DigraphManager(digraph_dict['g2_one_node'])
    assert set(digraph_manager.nodes) == {'A'}
    assert digraph_manager['A'].incoming_dim() == 0
    assert digraph_manager['A'].outgoing_dim() == 0

    digraph_manager.compress_edges()
    assert not digraph_manager.edges

    digraph_manager.add_nodes('B')
    digraph_manager.connect_nodes(('A', 'B'))

    assert digraph_manager('B0') == digraph_dict["g3_path_2"]
    digraph_manager.compress_edges()

    assert digraph_manager('B0') == digraph_dict['g3_path_2']
    assert digraph_manager[('A', 'B')][0].path == ['A', 'B']

    digraph_manager.add_nodes('C')
    digraph_manager.connect_nodes(('B', 'C'))

    assert digraph_manager('B0') == digraph_dict['g4_path_3']
    digraph_manager.compress_edges()

    assert digraph_manager('B0') == {"B0": {"A": ["C"], "C": []}}
    assert digraph_manager[('A', 'C')][0].path == ['A', 'B', 'C']

    digraph_manager = DigraphManager(digraph_dict['g4_path_3'])
    digraph_manager.add_nodes('D', 'E', 'F', 'G')
    digraph_manager.connect_nodes(('C', 'D'), ('D', 'E'), ('E', 'F'), ('F', 'G'))

    assert digraph_manager('B0') == digraph_dict['g5_path_7']
    digraph_manager.compress_edges()

    assert digraph_manager('B0') == {"B0": {"A": ["G"], "G": []}}
    assert digraph_manager[('A', 'G')][0].path == ['A', 'B', 'C', 'D', 'E', 'F', 'G']


def test_cycles(digraph_dict):
    """
    test cycles.
    """
    digraph_manager = DigraphManager(digraph_dict['g6_self_cycle'])
    digraph_manager.compress_edges()

    assert digraph_manager('B0') == digraph_dict['g6_self_cycle']
    assert digraph_manager['A'].outgoing_nodes == ['A']
    assert digraph_manager['A'].incoming_nodes == ['A']

    digraph_manager = DigraphManager(digraph_dict['g7_cycle_2'])
    digraph_manager.compress_edges()

    assert digraph_manager('B0') in ({"B0": {"A": ["A"]}}, {"B0": {"B": ["B"]}})

    if ('A', 'A') in digraph_manager.edges:
        assert digraph_manager[('A', 'A')][0].path == ['A', 'B', 'A']
    else:
        assert digraph_manager[('B', 'B')][0].path == ['B', 'A', 'B']

    digraph_manager = DigraphManager(digraph_dict['g5_path_7'])
    digraph_manager.connect_nodes(('G', 'A'))
    assert digraph_manager('B0') == digraph_dict["g9_cycle_7"]

    digraph_manager.connect_nodes(('A', 'D'))
    digraph_manager.compress_edges()

    assert len(digraph_manager.edges) == 2
    assert len(digraph_manager[('A', 'D')]) == 2
    assert digraph_manager[('D', 'A')][0].path == ['D', 'E', 'F', 'G', 'A']


def test_diblob_operations(digraph_dict):
    """
    tests diblob operations on the digraph
    """

    digraph_manager = DigraphManager(digraph_dict['g11_graph_without_diblobs'])
    digraph_manager.gather(new_diblob_id='B2', node_ids={'C', 'D', 'B'})
    digraph_manager.gather(new_diblob_id='B1', node_ids={'E', 'G', 'F'})
    digraph_manager.gather(new_diblob_id='B3', node_ids={'B1', 'B2', 'J'})

    assert digraph_manager('B0') == digraph_dict['g11_graph_with_diblobs']

    assert digraph_manager.get_diblob_descendants('B0') == {'B1', 'B2', 'B3'}
    assert digraph_manager.get_diblobs_common_ancestor('B2', 'B1') == 'B3'
    assert digraph_manager.get_diblobs_common_ancestor('B2', 'B3') == 'B3'
    assert digraph_manager.get_diblobs_common_ancestor('B0', 'B1') == 'B0'


def test_decouple(digraph_dict):
    """
    test compress, decompress, decouple option for the digraph (creates digraphs from pseudograph)
    """

    digraph_manager = DigraphManager(digraph_dict["g12_closed_dag_2_4"])
    digraph_manager.compress_edges()

    assert len(digraph_manager.edges[('A', 'F')]) == 4

    digraph_manager.decompress_edges()
    digraph_manager.sorted()

    assert digraph_manager('B0') == digraph_dict["g12_closed_dag_2_4"]

    digraph_manager.compress_edges()
    digraph_manager.decouple_edges()

    assert digraph_manager('B0') == {'B0': {'dec3(A,F)': ['F'],
                                            'F': [], 
                                            'dec1(A,F)': ['F'], 
                                            'dec2(A,F)': ['F'], 
                                            'A': ['F', 'dec1(A,F)', 'dec2(A,F)', 'dec3(A,F)']}}


def test_diblob_compression(digraph_dict):
    """
    test diblob compression to the point.
    """
    digraph_manager = DigraphManager(digraph_dict["g13_graph_to_compress"])
    digraph_manager.gather(new_diblob_id="B2", node_ids={"A", "B", "C"})
    digraph_manager.gather(new_diblob_id="B3", node_ids={"A", "B"})
    digraph_manager.compress_diblob("B2")
    digraph_manager.sorted()

    assert digraph_manager("B0") == {'B0': {'F': ['B2'],
                                            'D': ['F'], 
                                            'B2': ['D', 'D', 'E', 'F'],
                                            'E': ['F']}}
    digraph_manager.decouple_edges()

    assert digraph_manager("B0") == {'B0': {'B2': ['D', 'E', 'F', 'dec1(B2,D)'],
                                            'D': ['F'], 
                                            'dec1(B2,D)': ['D'], 
                                            'E': ['F'], 
                                            'F': ['B2']}}


def test_digraph_injection(digraph_dict):
    """
    test replacing node to diblob.
    """

    digraph_manager = DigraphManager(digraph_dict["g9_cycle_7"])
    injected_graph_manager = DigraphManager(digraph_dict["g8_cycle_3"])

    with pytest.raises(CommonResourcesInjection):
        digraph_manager.inject(injected_graph_manager, 'E')

    injection_dict = {'B0`': {'A`': ['B', 'C`'],
                              'B': ['C`'],
                              'C`': ['A`', 'B']}}

    with pytest.raises(CommonResourcesInjection):
        digraph_manager.inject(DigraphManager(injection_dict), 'E')

    injection_dict = {'B0`': {'A`': ['B`', 'C`'],
                              'B`': ['C`'],
                              'C`': ['A`', 'B`']}}

    digraph_manager.inject(DigraphManager(injection_dict), 'E')
    digraph_manager.sorted()

    assert digraph_manager('B0') == {'B0': {'C': ['D'],
                                            'F': ['G'], 
                                            'B0`': {'C`': ['A`', 'B`', {'B0': ['F']}], 
                                                    'B`': ['C`', {'B0': ['F']}],
                                                    'A`': ['B`', 'C`', {'B0': ['F']}]}, 
                                            'B': ['C'], 
                                            'A': ['B'], 
                                            'D': [{'B0`': ['A`', 'B`', 'C`']}], 
                                            'G': ['A']}}


def test_digraph_joining(digraph_dict):
    """
    test joining diblobs.
    """
    digraph_manager = DigraphManager(digraph_dict["g11_graph_with_diblobs"])
    with pytest.raises(IllegalJoinException):
        digraph_manager.join_diblobs(diblob_fst_id='B3', diblob_snd_id='B2', join_id='BJoin')

    digraph_manager.join_diblobs(diblob_fst_id='B1', diblob_snd_id='B2', join_id='BJoin')
    digraph_manager.sorted()

    assert digraph_manager('B0') == {'B0': {'I': ['A', 'H', {'BJoin': ['C', 'G']}], 
                                            'H': ['A', {'BJoin': ['B']}], 
                                            'B3': {'BJoin': {'C': ['D'], 
                                                             'D': [], 
                                                             'B': ['D', {'B0': ['A']}], 
                                                             'G': ['C', 'D', 'E', 'F'], 
                                                             'E': ['B', 'D', {'B0': ['A']}], 
                                                             'F': ['C', 'D', {'B0': ['H']}]}, 
                                                    'J': [{'BJoin': ['D']}]}, 
                                                    'A': [{'BJoin': ['B', 'C', 'D']}]}}
