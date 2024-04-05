"""
Enables random digraphs creation.
"""
from __future__ import annotations

import random
import itertools

from diblob.digraph_manager import DigraphManager
from diblob.exceptions import (InvalidAdditionException,
                               RandomCycleException,
                               RandomDAGException,
                               RootDiblobException,
                               InvalidGeneratorParameterException)

SEED = 0
RANDOM_DIBLOB_ID = "RAND"
random.seed(SEED)


class RandomBase:
    """
    Random graph base.
    - Enables digraphs addition based on magic method __add__.
    - Enables digraphs injection based on magic method __ior__.
    """

    def __init__(self, digraph: "RandomBase" | DigraphManager) -> None:
        self.digraph_manager = digraph if isinstance(digraph, DigraphManager)\
                                       else digraph.digraph_manager


    def __add__(self, other):

        if len(self.digraph_manager.diblobs) > 1 or len(other.digraph_manager.diblobs) > 1:
            raise InvalidAdditionException("Only digraphs with the one diblob can be added!")

        self_root_id = self.digraph_manager.root_diblob_id
        other_root_id = other.digraph_manager.root_diblob_id
        dict_x = dict(self.digraph_manager(self_root_id))[self_root_id]
        dict_y = dict(other.digraph_manager(other_root_id))[other_root_id]

        root_id = self.digraph_manager.root_diblob_id
        digraph_manager =  DigraphManager({root_id: {key: list(set(dict_x.get(key, []) +
                                            dict_y.get(key, [])))
                                            for key in set(dict_x) | set(dict_y)}})
        return RandomBase(digraph_manager)

    def __str__(self) -> str:
        return str(self.digraph_manager)

    def remove_isolated_nodes(self):
        """
        Removes isolated nodes.
        """
        occupied_nodes = set(edge[0] for edge in self.digraph_manager.edges.keys()) |\
                         set(edge[1] for edge in self.digraph_manager.edges.keys())

        nodes_to_remove = [self.digraph_manager[node_id] for node_id in
                           self.digraph_manager.nodes.keys() - occupied_nodes]

        self.digraph_manager.remove_nodes(*nodes_to_remove)


class RandomCycle(RandomBase):
    """
    Generates random cycle with delivered size which is embedded in node_space.
    """

    def __init__(self, node_space: list[str], cycle_size: int,
                 random_diblob_id: str = RANDOM_DIBLOB_ID):

        if len(node_space) < cycle_size:
            raise RandomCycleException("node_space must to be greater than cycle_size!")

        tail_node_id = random.choice(node_space)
        start_node_id = tail_node_id

        cycle_dict = {}
        node_space = list(node_space)

        for _ in range(cycle_size - 1):

            node_space.remove(tail_node_id)
            head_node_id = random.choice(node_space)
            cycle_dict[tail_node_id] = [head_node_id]
            tail_node_id = head_node_id

        cycle_dict[tail_node_id] = [start_node_id]
        cycle_dict.update({key: [] for key in (set(node_space) - set(cycle_dict.keys()))})
        super().__init__(DigraphManager({random_diblob_id: cycle_dict}))


class RandomSCC(RandomBase):
    """
    Generates random strongly connected components using RandomCycle. 
    Components are generated in node_space, so the can be disjoint.
    """

    def __init__(self, node_space: list[str], cycle_sizes: list[int],
                 random_diblob_id: str = RANDOM_DIBLOB_ID):

        if any(len(node_space) < c_size for c_size in cycle_sizes):
            raise RandomCycleException("node_space must to be greater than cycle_size!")

        if not cycle_sizes:
            raise RandomCycleException("cycle_sizes cannot be empty!")

        random_cycle = RandomCycle(node_space, cycle_sizes[0], random_diblob_id)
        for c_size in cycle_sizes[1:]:
            random_cycle = random_cycle + RandomCycle(node_space, c_size, random_diblob_id)

        super().__init__(random_cycle)


class RandomDAG(RandomBase):
    """
    Generates random directed acyclic graph. DAG is embedded in node_space.
    """

    def __init__(self, node_space: list[str], number_of_edges: int,
                 random_diblob_id: str = RANDOM_DIBLOB_ID):

        node_space_size = len(node_space)
        max_number_of_edges_in_dag = node_space_size * (node_space_size - 1) // 2

        if number_of_edges > max_number_of_edges_in_dag:
            raise RandomDAGException(f"node_space size should be \
                                     greater than {max_number_of_edges_in_dag}!")

        digraph_manager = DigraphManager({random_diblob_id: {}})
        digraph_manager.add_nodes(*node_space)

        node_space_order = list(node_space)
        random.shuffle(node_space_order)

        node_indexes = [(tail_idx, head_idx) for tail_idx in range(node_space_size)
                        for head_idx in range(tail_idx, node_space_size) if tail_idx < head_idx]
        print(len(node_indexes), number_of_edges)
        node_indexes = random.sample(node_indexes, k=number_of_edges)

        digraph_manager.connect_nodes(*[(node_space_order[tail_idx], node_space_order[head_idx])
                                      for tail_idx, head_idx in node_indexes])

        super().__init__(digraph_manager)


class RandomDigraph(RandomBase):
    """
    Generates random digraph by delivered list of digraphs injection.
    - uses dag as the base of the graph.
    - replace random nodes by elements of the list with digraphs.
    """

    def __init__(self,
                 dag_digraph: RandomDigraph,
                 inj_digraphs: list[RandomBase],
                 injection_drop_probability: float = 0.2):


        dag = dag_digraph.digraph_manager
        if len(dag.diblobs) > 1:
            raise RootDiblobException('DAG in generator should be and digraphs\
                                       with just one diblob (root)!')

        node_ids = list(dag.nodes)

        if len(inj_digraphs) > len(node_ids):
            raise InvalidGeneratorParameterException('DAG should has more nodes than the\
                                                     number of delivered digraphs!')

        node_ids = random.sample(node_ids, len(inj_digraphs))

        for node_id, inj_digraph in zip(node_ids, inj_digraphs):

            dag_node = dag_digraph.digraph_manager[node_id]
            node_space = inj_digraph.digraph_manager.nodes

            edges_to_drop = list(itertools.product(dag_node.incoming_nodes, node_space)) +\
                            list(itertools.product(node_space, dag_node.outgoing_nodes))

            dag_digraph.digraph_manager.inject(inj_digraph.digraph_manager, node_id)
            dag_digraph.digraph_manager.flatten(inj_digraph.digraph_manager.root_diblob_id)


            dag_digraph.digraph_manager.remove_edges(*[dag_digraph.digraph_manager[drop_id][0]
                                                       for drop_id in edges_to_drop
                                            if random.random() < injection_drop_probability])

        super().__init__(dag_digraph)
