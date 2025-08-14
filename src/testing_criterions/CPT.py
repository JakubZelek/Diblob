"""
Module created for CPT.
"""

from itertools import product
from diblob import DigraphManager
from decimal import Decimal


class NotSCGException(Exception):
    """
    Raised when Digraph for which we want to compute CPP is not strongly connected.
    """


class WeightedDigraphManager(DigraphManager):
    """
    Weighted Digraph Manager - digraph manager with cost function for edges.
    """

    def __init__(
        self,
        digraph_dict_representation: dict,
        cost_function: dict,
        default_cost: int = 1,
    ):

        self.cost_function = cost_function
        self.default_cost = default_cost

        super().__init__(digraph_dict_representation)

        self._set_cost()
        self._set_spanning_tree()

    def _set_cost(self):
        self.cost = {
            edge_id: Decimal(str(self.cost_function.get(edge_id, self.default_cost)))
            for edge_id in self.edges
        }

    def _set_spanning_tree(self):
        self.spanning_tree = {edge_id: edge_id[1] for edge_id in self.edges}

    def connect_nodes(self, *edge_ids: tuple[str, ...]):
        super().connect_nodes(*edge_ids)

        self._set_cost()
        self._set_spanning_tree()

    def update_cost_function(self, cost_function: dict):
        """
        updates cost_function.
        """
        self.cost_function |= cost_function
        self._set_cost()

    def get_edge_elements(self):
        """
        returns minimal and maximal elements.
        """
        minimal_elements = []
        maximal_elements = []

        for node_id, node in self.nodes.items():
            if node.outgoing_dim() == 0:
                maximal_elements.append(node_id)

            if node.incoming_dim() == 0:
                minimal_elements.append(node_id)

        return minimal_elements, maximal_elements

    def least_cost_paths(self):
        """
        Computes shortest path between pairs of nodes (based on cost).
        """
        cost = self.cost

        for node_k, node_i in product(self.nodes, self.nodes):
            if (node_i, node_k) in cost:
                for node_j in self.nodes:

                    if (node_k, node_j) in cost and (
                        (node_i, node_j) not in cost
                        or cost[(node_i, node_j)]
                        > cost[(node_i, node_k)] + cost[(node_k, node_j)]
                    ):

                        self.spanning_tree[(node_i, node_j)] = self.spanning_tree[
                            (node_i, node_k)
                        ]
                        cost[(node_i, node_j)] = cost.get(
                            (node_i, node_k), 0
                        ) + cost.get((node_k, node_j), 0)

                        if node_i == node_j and cost[(node_i, node_j)] < 0:
                            return

    def check_if_digraph_is_strongly_connected(self):
        """
        Validates if graph is SSG.
        """
        self.least_cost_paths()
        cost_function = self.cost

        for tail_id, head_id in product(self.nodes, self.nodes):
            if (tail_id, head_id) not in cost_function:
                return False
        return True


class CPTDigraphManager(WeightedDigraphManager):
    """
    Digraph manager for Chinese Postman Tour search
    """

    def __init__(
        self,
        digraph_dict_representation: dict,
        cost_function: dict,
        default_cost: int = 1,
    ):
        super().__init__(digraph_dict_representation, cost_function, default_cost)

        self._set_delta()
        self._set_basic_cost()
        self.feasible = {}

    def _set_delta(self):
        self.delta = {
            node_id: node.outgoing_dim() - node.incoming_dim()
            for node_id, node in self.nodes.items()
        }

    def _set_basic_cost(self):

        self.basic_cost = Decimal(
            str(
                sum(
                    self.cost_function.get(edge_id, self.default_cost)
                    for edge_id in self.edges
                )
            )
        )

    def connect_nodes(self, *edge_ids: tuple[str, ...]):
        super().connect_nodes(*edge_ids)

        self._set_delta()
        self._set_basic_cost()

    def _split_nodes_based_on_delta(self):
        """
        Splits nodes based on incoming and outgoing nodes number (without equals)
        """
        delta_pos = []
        delta_neq = []

        for node_id in self.nodes:

            if self.delta[node_id] < 0:
                delta_neq.append(node_id)

            elif self.delta[node_id] > 0:
                delta_pos.append(node_id)

        return delta_neq, delta_pos

    def _find_feasible(self, delta_neq, delta_pos):
        """
        feasible - f function from the papier:
        https://www3.cs.stonybrook.edu/~algorith/implement/cpp/distrib/SPAEcpp.pdf
        """

        delta = self.delta
        feasible = self.feasible

        for node_neq, node_pos in product(delta_neq, delta_pos):
            feasible[(node_neq, node_pos)] = (
                -delta[node_neq]
                if -delta[node_neq] < delta[node_pos]
                else delta[node_pos]
            )

            delta[node_neq] += feasible[(node_neq, node_pos)]
            delta[node_pos] -= feasible[(node_neq, node_pos)]

    def _get_residual_diblob_manager_for_cpt(self, delta_neq, delta_pos):
        """
        - Creates residual digraph.
        - Creates residual cost function.
        """

        cost = self.cost
        feasible = self.feasible

        residual_digraph = DigraphManager({"Res": {}})
        residual_digraph.add_nodes(*self.nodes)

        residual_cost = {}

        for node_neq, node_pos in product(delta_neq, delta_pos):
            residual_digraph.connect_nodes((node_neq, node_pos))
            residual_cost[(node_neq, node_pos)] = cost[(node_neq, node_pos)]

            if feasible[(node_neq, node_pos)] != 0:

                residual_digraph.connect_nodes((node_pos, node_neq))
                residual_cost[(node_pos, node_neq)] = -cost[(node_neq, node_pos)]

        return CPTDigraphManager(
            dict(residual_digraph("Res")), residual_cost, self.default_cost
        )

    def _improvements(self, residual_cpt: "CPTDigraphManager"):
        """
        improvement in the algorithm:
        https://www3.cs.stonybrook.edu/~algorith/implement/cpp/distrib/SPAEcpp.pdf
        """

        cost = residual_cpt.cost
        spanning_tree = residual_cpt.spanning_tree
        feasible = self.feasible

        for node_id in self.nodes:

            if cost.get((node_id, node_id), 0) < 0:
                k = 0
                flag = True
                u = node_id
                counter = 0
                while True:  # Emulate a do-while loop to find k to cancel

                    counter += 1
                    v = spanning_tree[(u, node_id)]

                    if cost[(u, v)] < 0 and (flag or k > feasible.get((v, u), 0)):
                        k = feasible.get((v, u), 0)
                        flag = False

                    u = v
                    if u == node_id:
                        break

                while True:  # Emulate a do-while loop to cancel k along the cycle
                    v = spanning_tree[(u, node_id)]

                    if cost[(u, v)] < 0:
                        feasible[(v, u)] = feasible.get((v, u), 0) - k
                    else:
                        feasible[(u, v)] = feasible.get((u, v), 0) + k
                    u = v
                    if u == node_id:
                        break

                return True
        return False

    def _get_cost(self):
        """
        returns the cost of the CPT.
        """
        phi = Decimal(str(0))
        cost = self.cost
        feasible = self.feasible
        nodes = self.nodes

        for tail_id, head_id in product(nodes, nodes):
            phi += cost.get((tail_id, head_id), 0) * feasible.get((tail_id, head_id), 0)
        return phi + self.basic_cost

    def _find_path(self, frm, feasible):
        """
        finds path.
        """
        for node_id in self.nodes:
            if feasible.get((frm, node_id), 0) > 0:
                return node_id

    def _get_cpt(self, start_node):
        """
        returns cpt.
        """
        v = start_node
        feasible = dict(self.feasible)
        edges_will_not_be_processed = set()
        cpt = []

        while True:

            u = v
            v = self._find_path(u, feasible)

            if v is not None:
                feasible[(u, v)] -= 1
                while u != v:
                    p = self.spanning_tree[(u, v)]
                    cpt.append((u, p))
                    u = p
            else:

                bridge_node = self.spanning_tree[(u, start_node)]
                if (u, bridge_node) in edges_will_not_be_processed:
                    break

                v = bridge_node
                for node_id in self.nodes:
                    if (
                        node_id != bridge_node
                        and (u, node_id) in self.edges
                        and (u, node_id) not in edges_will_not_be_processed
                    ):
                        v = node_id
                        break
                edges_will_not_be_processed.add((u, v))
                cpt.append((u, v))

        return cpt

    def compute_cpt(self, start_node):
        """
        compute cpt with the cost of cpt.
        """
        self._set_cost()
        self._set_spanning_tree()
        self._set_delta()
        self._set_basic_cost()
        self.feasible = {}

        if not self.check_if_digraph_is_strongly_connected():
            raise NotSCGException("Digraph is not strongly connected!")

        delta_neq, delta_pos = self._split_nodes_based_on_delta()
        self._find_feasible(delta_neq, delta_pos)

        residual_cpt = self._get_residual_diblob_manager_for_cpt(delta_neq, delta_pos)
        residual_cpt.least_cost_paths()

        while self._improvements(residual_cpt):
            residual_cpt = self._get_residual_diblob_manager_for_cpt(
                delta_neq, delta_pos
            )
            residual_cpt.least_cost_paths()

        cpt, cost = self._get_cpt(start_node), self._get_cost()
        return cpt, cost
