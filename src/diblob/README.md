# Diblob documentation
Diblob package consists of following modules:
- `components`: used by graph manager (node, edge, diblob).
- `digraph_manager`: core of the proposed data structure.
- `factory`: exampes of graph_manager used for more complicated digraphs craetion.
- `alghorimts`: examples of use diblob with basic digraphs alghoritms like DFS, DFSA (modified DFS) and Dijkstra alghorimt.
- `exceptions`: used in modules.
- `tools`: for comfortable work with digraphs.

# Components
## `Node`
Node representation in digraph.
- `node_id` - id of the node used by `GraphManager`. 
- `diblob_id` - id of the diblob, where node is placed.
- `incoming_nodes` - list of node ids (tails of the edges for which node is head).
- `outgoing_nodes` - list of node ids (heads of the edges for which node is tail).

Incoming / outgoing nodes can be redundant (pseudographs are also considered).

## `Edge`
Edge representation in digraph.
 - `path` - list of node ids.

## `Diblob`
Diblob representation in digraph. 
- `diblob_id` - id of the diblob used by `GraphManager`.
- `parent_id` - id of the diblob which is the parent for diblob.
- `children` - ids of the diblobs which are children of the diblob.
- `nodes` - node ids (or diblob ids) embedded in diblob.

# Digraph Manager

DigrahmManager instance creation require digraph dict representation.:
```json
{
"B0": {
    "B1": {
        "B": [{"B2": ["C", "D", "E"]}],
        "A": ["B", {"B0": ["F"]}],
    },
    "B2": {
        "C": ["D"],
        "D": ["E", {"B0": ["F", "G"]}],
        "E": [{"B0": ["F"]}, {"B1": ["A"]}],
    },
    "F": ["G", {"B1": ["B"]}],
    "G": [{"B1": ["A"]}, {"B2": ["D"]}],
},
}
```
