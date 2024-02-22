"""
Tools used in diblob.
"""
import json


def display_digraph(d: dict, indent: int=0):
    """
    Print digraph json in the human friendly format
    """
    def display(d, indent=0):
        for key, value in d.items():
            print(' ' * indent + f'"{key}": ', end='')
            if isinstance(value, dict):
                print('{')
                display(value, indent + 4)
                print(' ' * indent + '},')
            elif isinstance(value, list):
                print(json.dumps(value) + ',')
            else:
                print(f'"{value}",')

    print('{')
    display(dict(d), indent)
    print('}')


def cut_outgoing_edges(digraph_manager, diblob_id: str):
    """
    Extract digraph from diblob and cut outgoing edges. 
    Representation can be used for working with cleaned subgraphs.
    """

    diblob_dict = digraph_manager(diblob_id)
    _, _, outgoing_edges, _ = digraph_manager.get_diblob_edges(diblob_id)

    outgoing_nodes = {node for node, _ in outgoing_edges}


    def get_diblob_path(node_id: str):
        diblob = digraph_manager[digraph_manager[node_id].diblob_id]

        new_diblob_id = diblob.diblob_id
        path = [new_diblob_id]

        while new_diblob_id != diblob_id:

            diblob = digraph_manager[new_diblob_id]
            new_diblob_id = diblob.parent_id
            path.append(new_diblob_id)

        return path[::-1]


    for node in outgoing_nodes:
        neighs = eval(f"diblob_dict{str(get_diblob_path(node)).replace(', ', '][')}['{node}']")

        filtered_outgoing_nodes = [edge[1] for edge in outgoing_edges if edge[0] == node]
        elements_to_remove = [{key: sorted(value)}
                                for key, value in list_groupby(
                                filtered_outgoing_nodes, {node: digraph_manager[node].diblob_id
                                for node in filtered_outgoing_nodes}).items()]

        for elem in elements_to_remove:
            neighs.remove(elem)

    return diblob_dict


def sort_outgoing_nodes_in_dict_repr(node_lst: list):
    """
    Sorts delivered dict (lists inside).

    Args:
        node_lst: list of node ids.
    Example:
        ['C', 'B', 'A', {'G1': ['A', 'C', 'B']}] -> ['A', 'B', 'C', {'G1': ['A', 'B', 'C']}]
    """
    node_lst.sort(key= lambda x: list(x.keys())[0]
                    if isinstance(x, dict) else x)
    for node in node_lst:
        if isinstance(node, dict):
            sort_outgoing_nodes_in_dict_repr(node[list(node)[0]])


def sort_digraph_dict(dict_repr: dict):
    """
    Sorts entire dict representation using sort_out_nodes_in_dict_repr.
    """
    for value in dict_repr.values():
        if isinstance(value, dict):
            sort_digraph_dict(value)
        else:
            sort_outgoing_nodes_in_dict_repr(value)


def list_groupby(lst: list, map_dict: dict):
    """
    Groupby for list (work as groupby from itertools, but not sorted data required).
    """
    result_dict = {}
    for elem in lst:
        result_dict.setdefault(map_dict[elem], []).append(elem)
    return result_dict
