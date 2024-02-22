"""
Module consists of Edge, Diblob and Node class which are 
components used by DigraphManager.
"""

from diblob.exceptions import InvalidPathException

class Node:
    """
    Node representation in digraph.

    Args: 
        node_id (str): unique id of the node.
        diblob_id (str): unique id of the diblob in which node is placed.
        incoming_nodes (list[str]): list of incoming node ids.
        outgoing_nodes (list[str]): list of outgoing node ids.

    Note: {incoming}/{outgoing}_nodes can be redundant (pseudograph enabled).
    """

    def __init__(self,
                 node_id: str,
                 diblob_id: str,
                 incoming_nodes: list[str],
                 outgoing_nodes: list[str]):

        self.node_id = node_id
        self.diblob_id = diblob_id
        self.incoming_nodes = incoming_nodes
        self.outgoing_nodes = outgoing_nodes


    def get_incoming_edges(self):
        """
        Returns set of edge ids where the node is head.
        """
        return {(incoming, self.node_id) for incoming in self.incoming_nodes}


    def get_outgoing_edges(self):
        """
        Returns set of edge ids where the node is tail.
        """
        return {(self.node_id, outgoing) for outgoing in self.outgoing_nodes}


    def incoming_dim(self):
        """
        Number of incoming nodes.
        """
        return len(self.incoming_nodes)


    def outgoing_dim(self):
        """
        Number of outgoing nodes.
        """
        return len(self.outgoing_nodes)


    def _add_incoming(self, node_id: str):
        """
        Adds new node_id to incoming nodes list.
        """
        self.incoming_nodes.append(node_id)


    def _add_outgoing(self, node_id: str):
        """
        Adds new node_id to outgoing nodes list.
        """
        self.outgoing_nodes.append(node_id)


    def _rm_incoming(self, node_id: str):
        """
        Removes node_id from incoming nodes list.
        """
        self.incoming_nodes.remove(node_id)


    def _rm_outgoing(self, node_id: str):
        """
        Removes node_id from outgoing nodes list.
        """
        self.outgoing_nodes.remove(node_id)


class Edge:
    """
    Edge representation in digraph.
    Args:
        path (list[str]): path which contains source and destination node_ids.
                          path accumulation is enabled - in effect we can get
                          path with the length > 2. 
    Example: if we have digraph A -> B -> C -> D, we can accumulate it and treat as
             A -> B with edge [A, B, C, D].
    """

    def __init__(self, path: list[str]):

        if len(path) < 2:
            raise InvalidPathException("Edge path should be of the length > 2!")

        self.path = path

    def get_tail_and_head(self):
        """
        Returns tail and head of the edge.
        """
        return self.path[0], self.path[-1]

    def get_id(self):
        """
        Returns edge_id.
        """
        return (self.path[0], self.path[-1])

    def _reverse(self):
        """
        Reverses path of the edge
        """
        self.path = self.path[::-1]


class Diblob:
    """
    Subgraph of the graph.

    Args: 
        diblob_id (str): unique id of the diblob.
        children (set): set of diblob_ids which is the subgraphs of the considered graph.
        nodes (list[str]): list of node_ids which are located in the diblob.
        parent_id (str): id of the diblob in which the considered diblob is contained. 
    """
    def __init__(self,
                 diblob_id: str,
                 children: set,
                 nodes: list[str],
                 parent_id: str = None) -> None:

        self.diblob_id = diblob_id
        self.parent_id = parent_id
        self.children = children
        self.nodes = nodes

    def _add_children(self, *child_ids: tuple[str]):
        """
        Adds diblob_ids to the diblob.
        """
        self.children |= set(child_ids)

    def _add_nodes(self, *node_ids: tuple[str]):
        """
        Adds node_ids to the diblob.
        """
        self.nodes |= set(node_ids)
