# pylint: disable=protected-access

import json


from diblob.components import Edge, Node, Diblob
from diblob.tools import list_groupby
from diblob.exceptions import (CollisionException,
                               RemoveRootDiblobException,
                               DiblobKeyAlreadyExistsException,
                               InvalidDiblobId,
                               RootDiblobException,
                               DiblobGatherException,
                               EdgeAdditionException,
                               InvalidDigraphDictException,
                               InvalidConstructionJSON,
                               CommonResourcesInjection,
                               IllegalJoinException)



class DigraphManager:
    """
    DigraphManager operates on Node, Edge and Diblob class. 
    All operations on the digraph are managed indirectly by manager.

    Arg:
        digraph_dict_representation (dict): representation of the digraph in dictionary form.
    
    Assumptions: 
        - Digraphs_dict_representation should contain diblob_id which covers entire digraphs.
        - Every id in the digraph (diblob_id, node_id, edge_id) is unique 
          over diblob_id | node_id | edge_id.
        - If intersection of two diblobs is nonempty implies one of them is 
          the ancestor of the other.
    """

    def __init__(self, digraph_dict_representation: dict):

        if not isinstance(digraph_dict_representation, dict):
            raise InvalidDigraphDictException(f"digraph_dict_representation should\
                                               be of dict type, not\
                                              {type(digraph_dict_representation)}")

        if not digraph_dict_representation:
            raise InvalidDigraphDictException("Delivered dict cannot be empty!")

        root_diblob_id = list(digraph_dict_representation)[0]

        if not isinstance(digraph_dict_representation[root_diblob_id], dict):
            raise InvalidDigraphDictException("Delivered dict should contains diblob_id\
                                               which cover entire digraph!")

        self.diblobs = {}
        self.nodes = {}
        self.edges = {}
        self.root_diblob_id = root_diblob_id

        gather_dict = {}
        edges_to_connect = []

        self._construct(self.root_diblob_id, digraph_dict_representation,
                       gather_dict, edges_to_connect)
        self.connect_nodes(*edges_to_connect)

        root_nodes = {node_id for gather_lst in gather_dict.values()
                      for node_id in gather_lst if node_id not in gather_dict}

        gather_dict.pop(self.root_diblob_id)
        root_children = set(gather_dict)


        self[self.root_diblob_id] = Diblob(self.root_diblob_id, root_children, root_nodes)

        for diblob_id, nodes in reversed(gather_dict.items()):
            self.gather(diblob_id, set(nodes))


    def __setitem__(self, key: str | tuple[str, str], value: Diblob | Node | Edge) -> None:

        if key in set(self.diblobs) | set(self.nodes):
            raise CollisionException('Key should be unique over diblobs | nodes | edges')

        if isinstance(value, Diblob) and isinstance(key, str):
            self.diblobs[key] = value

        elif isinstance(value, Node) and isinstance(key, str):
            self.nodes[key] = value

        elif isinstance(value, Edge) and isinstance(key, tuple):

            if len(key) != 2 or not (isinstance(key[0], str) and
                                     isinstance(key[1], str)):
                raise TypeError(f"The key of the Edge should be of type tuple[str, str],\
                                  not tuple[{type(key[0])},{type(key[1])}]!")

            self.edges.setdefault(key, []).append(value)

        else:
            raise TypeError(f"Key: value pair should be one of str:\
                            Diblob, str: Node, tuple: Edge, not {type(key)}: {type(value)}!")


    def __getitem__(self, key: str | tuple[str, str]):
        return (self.diblobs | self.nodes | self.edges)[key]


    def __contains__(self, key: str | tuple[str, str]):
        return key in set(self.diblobs | self.nodes | self.edges)


    def __call__(self, diblob_id: str):
        repr_dict = {diblob_id: {}}
        nodes = self[diblob_id].nodes

        for node_id in nodes:
            node = self[node_id]

            if isinstance(node, Diblob):
                repr_dict[diblob_id][node_id] = self(node_id)[node_id]
            else:
                outgoing_nodes_grouped_by_diblob = list_groupby(node.outgoing_nodes,
                                    map_dict={node_id: self[node_id].diblob_id
                                    for node_id in node.outgoing_nodes})

                repr_dict[diblob_id][node_id] = outgoing_nodes_grouped_by_diblob.get(diblob_id, [])\
                                              + [{key: value} for key, value in \
                                              outgoing_nodes_grouped_by_diblob.items()
                                              if key != diblob_id]
        return repr_dict



    def __repr__(self):
        lines = []

        def display(digraph_dict, indent=0):
            for key, value in digraph_dict.items():
                lines.append(' ' * indent + f'"{key}": ')

                if isinstance(value, dict):
                    lines.append('{\n')
                    display(value, indent + 4)
                    lines.append(' ' * indent + '},\n')

                elif isinstance(value, list):
                    lines.append(json.dumps(value) + ',\n')

                else:
                    lines.append(f'"{value}",\n')

        lines.append('{\n')
        display(self(self.root_diblob_id), 0)
        lines.append('}\n')

        return ''.join(lines)


    def _construct(self, diblob_id: str, digraph_dict_representation: dict,
                  gather_dict: dict, edges_to_connect: list[str]):
        """ 
        Used in __init__. Constructs graphs based on delivered dictionary.
        """
        gather_dict[diblob_id] = []
        sub_digraph_dict_representation = digraph_dict_representation[diblob_id]

        for key in sub_digraph_dict_representation:
            value = sub_digraph_dict_representation[key]

            if isinstance(value, dict):
                self._construct(key, {key: sub_digraph_dict_representation[key]},
                               gather_dict, edges_to_connect)

            elif isinstance(value, list):
                self[key] = Node(key, self.root_diblob_id, [], [])

                for head in value:
                    if isinstance(head, dict):
                        head_key = list(head)[0]
                        for node_id in head[head_key]:
                            edges_to_connect.append((key, node_id))
                    else:
                        edges_to_connect.append((key, head))
            else:
                raise InvalidConstructionJSON('Invalid json delivered!')

            gather_dict[diblob_id].append(key)


    def get_diblobs_common_ancestor(self, diblob_id1: str, diblob_id2: str):
        """
        Returns common ancestor diblob_id for diblob_id1 and diblob_id2.
        """

        ancestors_of_diblob_id1 = []
        ancestors_of_diblob_id2 = []

        while diblob_id1:
            ancestors_of_diblob_id1.append(diblob_id1)
            diblob_id1 = self[diblob_id1].parent_id

        while diblob_id2:
            ancestors_of_diblob_id2.append(diblob_id2)
            diblob_id2 = self[diblob_id2].parent_id

        common_ancestor = None

        for b1, b2 in zip(ancestors_of_diblob_id1[::-1], ancestors_of_diblob_id2[::-1]):
            if b1 == b2:
                common_ancestor = b1
            else:
                break

        return common_ancestor


    def get_diblob_descendants(self, diblob_id: str):
        """
        Returns diblob_ids which are descendants of the diblob.
        """

        descendants = set()
        diblob_children = self[diblob_id].children
        descendants |= diblob_children

        for child_id in diblob_children:
            descendants |= self.get_diblob_descendants(child_id)
        return descendants


    def get_diblob_edges(self, diblob_id: str):
        """
        Returns edge_ids, incoming edge_ids, outgoing edge_ids, 
        descendants_with_diblob_id of the diblob.
        """

        descendants_with_diblob_id = self.get_diblob_descendants(diblob_id)
        descendants_with_diblob_id.add(diblob_id)

        inside_edges = set()
        incoming_edges = set()
        outgoing_edges = set()

        for edge_id in self.edges:

            tail_diblob_id = self[edge_id[0]].diblob_id
            head_diblob_id = self[edge_id[1]].diblob_id

            if tail_diblob_id in descendants_with_diblob_id and\
               head_diblob_id in descendants_with_diblob_id:

                inside_edges.add(edge_id)

            elif tail_diblob_id in descendants_with_diblob_id:
                outgoing_edges.add(edge_id)

            elif head_diblob_id in descendants_with_diblob_id:
                incoming_edges.add(edge_id)

        return inside_edges, incoming_edges, outgoing_edges, descendants_with_diblob_id


    def is_diblob_ancestor(self, potential_ancestors: set, diblob_id: str):
        """
        Checks the diblob has ancestors with id present in potential_ancestors. 

        Args:
            potential_ancestor_diblob_id (str): id of potential ancestor diblob.
            diblob_id (str): id of the diblob.
        """

        if diblob_id in potential_ancestors:
            return False

        diblob_parent_id = self[diblob_id].parent_id

        while diblob_parent_id:
            if diblob_parent_id in potential_ancestors:
                return True
            diblob_parent_id = self[diblob_parent_id].parent_id

        return False


    def flatten(self, *diblob_ids: tuple[str, ...]):
        """
        Removes diblobs from the digraph_manager and flat part of the digraph included in diblobs.

        Args:
            diblob_ids (str): id of the diblobs will be flattened. 
        """

        if self.root_diblob_id in diblob_ids:
            raise RemoveRootDiblobException(f'diblob with id = {self.root_diblob_id} is the\
                                          root of the digraph. Cannot be removed!')

        invalid_ids = set(diblob_ids) - set(self.diblobs)
        if invalid_ids:
            raise InvalidDiblobId(f"Digraph doesn't contain diblobs with IDs in {invalid_ids} !")


        for diblob_id in diblob_ids:
            diblob = self[diblob_id]

            parent_diblob = self[self[diblob_id].parent_id]

            for node_id in diblob.nodes:
                node = self[node_id]

                if isinstance(node, Node):
                    self[node_id].diblob_id = parent_diblob.diblob_id
                else:
                    self[node_id].parent_id = parent_diblob.diblob_id

            parent_diblob.children |= diblob.children
            parent_diblob.children.remove(diblob_id)

            parent_diblob.nodes |= diblob.nodes
            parent_diblob.nodes.remove(diblob_id)

            self.diblobs.pop(diblob_id)


    def gather(self, new_diblob_id: str, node_ids: set[str]):
        """
        Creates new diblob based on delivered node_ids.
        node_ids must be inside in the same parent diblob.

        Args:
            new_diblob_key (str): id of the diblob will be created
            node_ids (set): set of nodes will be gathered together.
        """

        if new_diblob_id in self:
            raise DiblobKeyAlreadyExistsException(f"id = {new_diblob_id} is already occupied!")


        node = self[list(node_ids)[0]]
        parent_diblob = self[node.parent_id] if isinstance(node, Diblob) else self[node.diblob_id]

        if node_ids - parent_diblob.nodes:
            raise DiblobGatherException('All nodes should have the same \
                                        diblob_id during gathering!')


        diblob_children = set()
        parent_id = parent_diblob.diblob_id

        for node_id in node_ids:
            node = self[node_id]

            if isinstance(node, Node):
                node.diblob_id = new_diblob_id
            else:
                diblob_children.add(node_id)
                node.parent_id = new_diblob_id


        self[new_diblob_id] = Diblob(new_diblob_id, diblob_children, node_ids, parent_id)

        parent_diblob.nodes.add(new_diblob_id)
        parent_diblob.children.add(new_diblob_id)
        parent_diblob.nodes -= node_ids


    def compress_diblob(self, diblob_id: str):
        """
        Compress diblob to node.
        """

        if self.root_diblob_id == diblob_id:
            raise RootDiblobException('Root diblob cannot be compressed!')

        _, diblob_incoming_edges,\
        diblob_outgoing_edges, descendants =  self.get_diblob_edges(diblob_id)

        descendants.remove(diblob_id)
        self.flatten(*descendants)

        diblob = self[diblob_id]

        nodes_to_remove = [self[node_id] for node_id in diblob.nodes]

        incoming_edges = [(tail, diblob_id) for tail, _ in
                          self.get_multiple_edge_ids(*diblob_incoming_edges)]

        outgoing_edges = [(diblob_id, head) for _, head in
                          self.get_multiple_edge_ids(*diblob_outgoing_edges)]

        self.remove_nodes(*nodes_to_remove)

        self.diblobs.pop(diblob_id)
        self.diblobs[diblob.parent_id].children.remove(diblob_id)
        self[diblob_id] = Node(diblob_id, diblob.parent_id, [], [])

        self.connect_nodes(*incoming_edges)
        self.connect_nodes(*outgoing_edges)


    def merge_edges(self, edge_1: Edge, edge_2: Edge):
        """
        Merges two edges.
        """

        if edge_1.path != edge_2.path:
            if edge_1.path[-1] != edge_2.path[0]:
                raise EdgeAdditionException(f"Edges are incompatible:\
                                                {edge_1.path}, {edge_2.path}")
            node_id = edge_1.path[-1]

            if len(self[node_id].incoming_nodes) != 1 or\
            len(self[node_id].outgoing_nodes) != 1:

                raise EdgeAdditionException("Only edges where common node with\
                                            len(incoming_nodes) == len(outgoing_nodes) == 1\
                                            can be added!")


            path = edge_1.path[:-1] + edge_2.path
            tail, head = path[0], path[-1]

            self.remove_nodes(self[node_id])

            self[tail].outgoing_nodes.append(head)
            self[head].incoming_nodes.append(tail)

            self[(tail, head)] = Edge(path)


    def get_multiple_edge_ids(self, *edge_ids : tuple[str, ...]):
        """
        Returns edge_ids as many times occurred in DigraphManager list of edges.
        """
        result = []
        for edge_id in edge_ids:
            result += [edge_id] * len(self[edge_id])
        return result


    def remove_edges(self, *edges: tuple[Edge, ...]):
        """
        Removes edges from the graph.
        """

        for edge in edges:
            tail, head = edge.path[0], edge.path[-1]

            self[tail].outgoing_nodes.remove(head)
            self[head].incoming_nodes.remove(tail)
            self.edges[(tail, head)].remove(edge)

            if not self.edges[(tail, head)]:
                self.edges.pop((tail, head))


    def connect_nodes(self, *edge_ids: tuple[str, ...]):
        """
        Adds edges in existing graph structure.
        """

        for edge_id in edge_ids:
            tail, head = edge_id[0], edge_id[1]
            self[tail].outgoing_nodes.append(head)
            self[head].incoming_nodes.append(tail)
            self[(tail,head)] = Edge(path=[tail, head])        


    def remove_nodes(self, *nodes: tuple[Node, ...]):
        """
        Removes nodes from the graph.
        """

        for node in nodes:
            node_id = node.node_id

            for incoming_node in set(node.incoming_nodes):
                self.remove_edges(*self[(incoming_node, node_id)])

            for outgoing_node in set(node.outgoing_nodes):
                self.remove_edges(*self[(node_id, outgoing_node)])

            self[node.diblob_id].nodes.remove(node_id)
            self.nodes.pop(node_id)


    def add_nodes(self, *node_ids: tuple[str], diblob_id: str=None):
        """
        Adds nodes to the graph structure.
        """

        if not diblob_id:
            diblob_id = self.root_diblob_id

        for node_id in node_ids:
            self[node_id] = Node(node_id, diblob_id, [], [])

        self[diblob_id].nodes |= set(node_ids)


    def compress_edges(self):
        """
        Compress edges by gathering them to paths.
        """
        nodes_to_compress = {node_id for node_id in self.nodes if
                             len(self[node_id].incoming_nodes) == 1 and
                             len(self[node_id].outgoing_nodes) == 1}

        while nodes_to_compress:

            node_id = nodes_to_compress.pop()
            node = self[node_id]

            incoming_node_id = node.incoming_nodes[0]
            outgoing_node_id = node.outgoing_nodes[0]

            self.merge_edges(self[(incoming_node_id, node_id)][0],
                             self[(node_id, outgoing_node_id)][0])


    def decompress_edges(self):
        """
        Reverse operation to compress_edges.
        """

        for edge_lst in list(self.edges.values()):
            for edge in list(edge_lst):

                if len(edge.path) > 2:
                    node_ids = edge.path
                    self.remove_edges(edge)
                    self.add_nodes(*node_ids[1:-1])
                    self.connect_nodes(*list(zip(node_ids[:-1], node_ids[1:])))


    def inject(self, digraph_manager: "DigraphManager", node_id: str):
        """
        Replace node by diblob.
        """
        namespace = (set(digraph_manager.diblobs) & set(self.diblobs)) |\
                    (set(digraph_manager.nodes) & set(self.nodes))
        if namespace:
            raise CommonResourcesInjection(f"Injection can be performed only with new ID\
                                            (not occupied). Common {namespace=}")

        node = self[node_id]

        injected_diblob_root_id = digraph_manager.root_diblob_id
        self.diblobs |= digraph_manager.diblobs
        self.nodes |= digraph_manager.nodes
        self.edges |= digraph_manager.edges

        self[injected_diblob_root_id].parent_id = node.diblob_id
        self[node.diblob_id]._add_children(injected_diblob_root_id)
        self[node.diblob_id]._add_nodes(injected_diblob_root_id)


        for injected_node_id in digraph_manager[injected_diblob_root_id].nodes:


            if isinstance(digraph_manager[injected_node_id], Node):

                self.connect_nodes(*[(incoming_node_id, injected_node_id)
                                for incoming_node_id in node.incoming_nodes])

                self.connect_nodes(*[(injected_node_id, outgoing_node_id)
                                for outgoing_node_id in node.outgoing_nodes])


        self.remove_nodes(node)


    def join_diblobs(self, diblob_fst_id: str, diblob_snd_id: str, join_id: str):
        """
        Join two diblobs to diblob with join_id.
        """

        fst_diblob = self[diblob_fst_id]
        snd_diblob = self[diblob_snd_id]

        if fst_diblob.parent_id != snd_diblob.parent_id:
            raise IllegalJoinException(f"Diblobs during joining must have the same parent_id:\
                                       {fst_diblob.parent_id} != {snd_diblob.parent_id}")

        join_node_ids = self[diblob_fst_id].nodes | self[diblob_snd_id].nodes
        self.flatten(diblob_fst_id, diblob_snd_id)
        self.gather(join_id, join_node_ids)


    def decouple_edges(self):
        """
        In pseudoghraph transforms multiple edges into different ones with point in the middle.
        """

        edge_dict = dict(self.edges)

        for edge_id, edge_lst in edge_dict.items():
            if len(edge_lst) > 1:

                tail, head = edge_id[0], edge_id[1]
                diblob_id = self.get_diblobs_common_ancestor(self[tail].diblob_id,
                                                         self[head].diblob_id)

                for idx, edge in enumerate(list(edge_lst)[:-1]):
                    self.remove_edges(edge)
                    decouple_node_id = f"dec{idx + 1}({tail},{head})"
                    self.add_nodes(decouple_node_id, diblob_id=diblob_id)
                    self.connect_nodes((tail, decouple_node_id), (decouple_node_id, head))


    def reverse_edges(self, *edges: tuple[Edge, ...]):
        """
        reverse delivered edges (not edge_id because of pseudograph properties).
        """

        for edge in edges:
            tail, head = edge.get_tail_and_head()
            self.remove_edges(edge)
            self.connect_nodes((head, tail))


    def sorted(self):
        """
        Sort components of the graph structure.
        """
        self.edges = dict(sorted(self.edges.items()))
        self.nodes = dict(sorted(self.nodes.items()))
        self.diblobs = dict(sorted(self.diblobs.items()))

        for node in self.nodes.values():
            node.outgoing_nodes = sorted(node.outgoing_nodes)
            node.incoming_nodes = sorted(node.incoming_nodes)
