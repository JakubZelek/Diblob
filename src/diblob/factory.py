"""
Functions for working with digraph_manager
"""
from diblob.digraph_manager import DigraphManager
from diblob.exceptions import MultipleEdgeException


class DiblobFactory:
    """
    Transform digraph into specific kind of digraph based of digraph_manager.
    """

    @staticmethod
    def generate_edge_digraph(digraph_manager: DigraphManager,
                              reduce_value: int = 0,
                              delimiter: str = '|'):
        """
        Generates L(G) based on delivered digraph_manager.
        """

        if len(digraph_manager.diblobs) > 1:
            raise MultipleEdgeException("Edge digraph can be computed only for digraph_manager\
                                         with only root_diblob!")

        root_diblob_id = digraph_manager.root_diblob_id
        edge_graph_manager = DigraphManager({root_diblob_id: {}})

        edge_node_ids = set()
        grouped_nodes = set()

        for edge_id in digraph_manager.edges:
            grouped_nodes |= {edge_id[0], edge_id[1]}

            for idx, edge in enumerate(digraph_manager[edge_id]):
                edge_node_id = delimiter.join(edge.path[:-1]) + delimiter +\
                            delimiter.join(edge.path[-1].split(delimiter)[reduce_value:])
                edge_node_ids.add(edge_node_id if idx == 0 else edge_node_id + f"_{idx}")

        edge_graph_manager.add_nodes(*(edge_node_ids |
                                       (set(digraph_manager.nodes) - grouped_nodes)))

        def counter_list(list_of_nodes):
            counter_dict = {}
            output_list = []

            for node_id in list_of_nodes:
                counter_dict[node_id] = counter_dict.get(node_id, 0) + 1
                output_list.append((node_id, counter_dict[node_id] - 1))

            return output_list

        edges_to_connect = set()

        for edge_id in digraph_manager.edges:
            outgoing_counted_nodes = counter_list(digraph_manager[edge_id[1]].outgoing_nodes)

            for outgoing_counted_node in outgoing_counted_nodes:

                for idx, edge in enumerate(digraph_manager[edge_id]):

                    outgoing_node_id, count = outgoing_counted_node[0], outgoing_counted_node[1]
                    outgoing_edge =  digraph_manager[(edge_id[1], outgoing_node_id)][count]

                    tail = delimiter.join(edge.path[:-1]) + delimiter +\
                        delimiter.join(edge.path[-1].split(delimiter)[reduce_value:])
                    tail = tail if idx == 0 else tail + f"_{idx}"

                    head = delimiter.join(outgoing_edge.path[:-1]) + delimiter +\
                        delimiter.join(outgoing_edge.path[-1].split(delimiter)[reduce_value:])
                    head = head if count == 0 else head + f"_{count}"

                    edges_to_connect.add((tail, head))

        edge_graph_manager.connect_nodes(*edges_to_connect)

        return edge_graph_manager


    @staticmethod
    def generate_bipartite_digraph(digraph_manager: DigraphManager):
        """
        Generates BG(G) digraph (with directed arcs).
        """

        if len(digraph_manager.diblobs) > 1: 
            raise MultipleEdgeException("Bipartite can be computed only for digraph_manager\
                                         with only root_diblob!")

        bipartite_digraph_dict = {digraph_manager.root_diblob_id: {node_id + '`': [] for node_id\
                                in digraph_manager.nodes} | {node_id + '``': []
                                                           for node_id in digraph_manager.nodes}}
        for node in digraph_manager.nodes.values():
            bipartite_digraph_dict[digraph_manager.root_diblob_id][node.node_id + '`'] =\
                                [node_id + '``' for node_id in sorted(node.outgoing_nodes)]
        return DigraphManager(bipartite_digraph_dict)


    @staticmethod
    def generate_flow_digraph(digraph_manager: DigraphManager):
        """
        Generates digraph with splitted nodes. Splitted node is divided 
        to two connected nodes, where the first one and the second one inherit 
        incoming_nodes and outgoing_nodes respectively.
        """

        root_diblob_id = digraph_manager.root_diblob_id
        flow_graph_manager = DigraphManager({root_diblob_id: {}})

        node_ids = {node_id + '`' for node_id in digraph_manager.nodes} |\
                   {node_id + '``' for node_id in digraph_manager.nodes}
        flow_graph_manager.add_nodes(*node_ids)

        edges_to_connect = set()

        for node_id, node in digraph_manager.nodes.items():

            node_split_tail = node_id + '`'
            node_split_head = node_id + '``'

            edges_to_connect |= {(incoming_node + '``', node_split_tail)
                                 for incoming_node in node.incoming_nodes}
            edges_to_connect |= {(node_split_head, outgoing_node + '`')
                                 for outgoing_node in node.outgoing_nodes}

            edges_to_connect.add((node_split_tail, node_split_head))

        flow_graph_manager.connect_nodes(*edges_to_connect)
        return flow_graph_manager
