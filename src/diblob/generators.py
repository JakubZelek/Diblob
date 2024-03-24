"""
Enables random digraphs creation.
"""
import random
import itertools

from diblob.digraph_manager import DigraphManager
from diblob.exceptions import (InvalidAdditionException,
                               RandomCycleException,
                               RandomDAGException)

SEED = 0
RANDOM_DIBLOB_ID = "RAND"
random.seed(SEED)


class RandomBase:
    """
    Random graph base.
    - Enables digraphs addition based on magic method __add__.
    - Enables digraphs injection based on magic method __ior__.
    """

    def __init__(self, digraph: DigraphManager | "RandomBase") -> None:
        self.digraph_manager = digraph if isinstance(digraph, DigraphManager)\
                                       else digraph.digraph_manager


    def __add__(self, other):

        if len(self.digraph_manager.diblobs) > 1 or len(other.digraph_manager.diblobs) > 1:
            raise InvalidAdditionException("Only digraphs with the one diblob can be added!")

        dict_x = dict(self.digraph_manager(self.digraph_manager.root_diblob_id))
        dict_y = dict(other.digraph_manager(other.digraph_manager.root_diblob_id))

        digraph_manager =  DigraphManager({RANDOM_DIBLOB_ID: {key: list(set(dict_x.get(key, []) +
                                                                            dict_y.get(key, [])))
                                                          for key in set(dict_x) | set(dict_y)}})
        return RandomBase(digraph_manager)


    def __ior__(self, other):
        self.digraph_manager.inject(other.digraph_manager, other.digraph_manager.root_diblob_id)
        self.digraph_manager.flatten(other.digraph_manager.root_diblob_id)


    def __str__(self) -> str:
        self.digraph_manager.sorted()
        return str(self.digraph_manager)


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
        super().__init__(DigraphManager({random_diblob_id: cycle_dict}))


class RandomSCC(RandomBase):
    """
    Generates random strongly connected component using RandomCycle. SCC is embedded in node_space.
    """

    def __init__(self, node_space: list[str], cycle_sizes: list[int]):

        if any(len(node_space) < c_size for c_size in cycle_sizes):
            raise RandomCycleException("node_space must to be greater than cycle_size!")

        if not cycle_sizes:
            raise RandomCycleException("cycle_sizes cannot be empty!")

        random_cycle = RandomCycle(node_space, cycle_sizes[0])
        for c_size in cycle_sizes[1:]:
            random_cycle = random_cycle + RandomCycle(node_space, c_size)

        super().__init__(random_cycle)


class RandomDAG(RandomBase):
    """
    Generates random directed acyclic graph. DAG is embedded in node_space.
    """

    def __init__(self, node_space: list[str], number_of_edges: int, 
                 random_diblob_id: str = RANDOM_DIBLOB_ID):

        max_number_of_edges_in_dag = number_of_edges * (number_of_edges - 1)
        if node_space < max_number_of_edges_in_dag:
            raise RandomDAGException(f"node_space size should be greater\
                                     than {max_number_of_edges_in_dag}!")

        digraph_manager = DigraphManager({random_diblob_id: {}})
        digraph_manager.add_nodes(*node_space)

        node_space_order = list(node_space)
        random.shuffle(node_space_order)

        for _ in range(number_of_edges):
            rand_idx = random.randint(0, number_of_edges - 1)
            tail_id = node_space_order[rand_idx]
            head_id = node_space_order[random.randint(rand_idx + 1, len(node_space_order))]
            digraph_manager.connect_nodes((tail_id, head_id))

        super().__init__(digraph_manager)


class RandomDigraph(RandomBase):
    """
    Generates random digraph as follows:
        - generates random DAG.
        - generates random SCCs.
        - inject SCCs to DAG. 
    """

    def __init__(self,
                node_dag_space: list[str],
                number_of_dag_edges: int,
                *node_scc_space: tuple[tuple[str]],
                min_cycle_size_is_scc: int,
                max_cycle_size_is_scc: int,
                min_number_of_cycles: int,
                max_number_of_cycles: int,
                injection_drop_probability: float = 0.2):

        dag_digraph = RandomDAG(node_dag_space, number_of_dag_edges)
        dag_injections_list = random.sample(node_dag_space, len(node_scc_space))


        for node_space, dag_injection_node in zip(node_scc_space, dag_injections_list):

            number_of_cycles = random.randint(min_number_of_cycles, max_number_of_cycles)
            cycle_sizes = [random.randint(min_cycle_size_is_scc, max_cycle_size_is_scc)
                           for _ in range(number_of_cycles)]

            random_scc = RandomSCC(node_space, cycle_sizes)

            dag_node = dag_digraph.digraph_manager[dag_injection_node]

            dag_digraph |= random_scc

            for injection_edge_id in itertools.product(dag_node.incoming_nodes, node_space):
                if random.random() < injection_drop_probability:
                    dag_digraph.digraph_manager.remove_edges(injection_edge_id)

            for injection_edge_id in itertools.product(node_space, dag_node.outgoing_nodes):
                if random.random() < injection_drop_probability:
                    dag_digraph.digraph_manager.remove_edges(injection_edge_id)

        super().__init__(dag_digraph)
