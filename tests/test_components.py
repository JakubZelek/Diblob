# pylint: disable=protected-access
"""
Diblob component tests (components controlled by DigraphManager).
"""

import pytest

from diblob.components import Node, Edge, Diblob
from diblob.exceptions import InvalidPathException


def test_node():
    """
    Node test.
    """

    node = Node(node_id='node_id',
                diblob_id='diblob_id',
                incoming_nodes=['1', '2', '3', '3'],
                outgoing_nodes=['1', '1', '2', '3', '4', '5', '6'])

    assert node.get_incoming_edges() == {('1', 'node_id'), ('2', 'node_id'), ('3', 'node_id')}
    assert node.get_outgoing_edges() == {('node_id', '1'), ('node_id', '2'), ('node_id', '3'),
                                         ('node_id', '4'), ('node_id', '5'), ('node_id', '6')}

    assert node.incoming_dim() == 4
    assert node.outgoing_dim() == 7

    node._add_incoming('new_id')
    node._rm_incoming('1')

    node._add_outgoing('new_id')
    node._rm_outgoing('1')

    assert node.incoming_nodes == ['2', '3', '3', 'new_id']
    assert node.outgoing_nodes == ['1', '2', '3', '4', '5', '6', 'new_id']


def test_edge():
    """
    Edge test.
    """

    with pytest.raises(InvalidPathException):
        Edge([])

    with pytest.raises(InvalidPathException):
        Edge(['1'])

    edge = Edge(['1', '2', '3'])

    assert edge.get_tail_and_head() == ('1', '3')

    edge._reverse()

    assert edge.get_tail_and_head() == ('3', '1')
    assert edge.get_id() == ('3', '1')

    edge._reverse()
    assert edge.get_id() == ('1', '3')


def test_diblob():
    """
    Diblob test.
    """

    diblob = Diblob(diblob_id='diblob_id',
                nodes={'1', '2', '3'},
                children={'B1', 'B2', 'B3'},
                parent_id='parent_diblob_id')

    diblob._add_children('B4', 'B5')
    diblob._add_nodes('4', '5', '6', '7')

    assert diblob.children == {'B1', 'B2', 'B3', 'B4', 'B5'}
    assert diblob.nodes == {'1', '2', '3', '4', '5', '6', '7'}
