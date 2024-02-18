# Diblob documentation
Diblob package consists of following modules:
- `components` - used by graph manager (node, edge, diblob).
- `digraph_manager` - core of the proposed data structure.
- `factory` - exampes of graph_manager used for more complicated digraphs craetion.
- `alghorimts` - examples of use diblob with basic digraphs alghoritms like DFS, DFSA (modified DFS) and Dijkstra alghorimt.
- `exceptions` - used in modules.
- `tools` - for comfortable work with digraphs.

In entire package methods started with '_' are used by GraphManager (indirectly).

# Components
Componenst are used by GraphManager for data structure creation. Data Structure consist of instances of classes `Node`, `Edge` and `Diblob`.

## `Node`
Node representation in digraph.
Incoming / outgoing nodes can be redundant (pseudographs are also considered).
### Fields
- `node_id` - id of the node used by `GraphManager`. 
- `diblob_id` - id of the diblob, where node is placed.
- `incoming_nodes` - list of node ids (tails of the edges for which node is head).
- `outgoing_nodes` - list of node ids (heads of the edges for which node is tail).

### Methods
- `get_incoming_edges(self)` - returns set of edge ids where the node is head.
- `get_outgoing_edges(self)` - returns set of edge ids where the node is tail.
- `incoming_dim(self)` - number of incoming nodes.
- `outgoing_dim(self)` - number of outgoing nodes.
- `_add_incoming(self, node_id: str)` - adds new node_id to incoming_nodes.
- `_add_outgoing(self, node_id: str)` - adds new node_id to outgoing_nodes.
- `_rm_incoming(self, node_id: str)` - removes node_id from incoming_nodes.
- `_rm_outgoing(self, node_id: str)` - removes node_id from outgoing_nodes.

## `Edge`
Edge representation in digraph. Enable treateing some kinds of paths as one edge.

### Fields

 - `path` - list of node ids.

### Methods
- `get_tail_and_head(self)` -  returns tail and head of the edge.
- `get_id(self)` - returns edge_id (head, tail).
- `_reverse(self)` - reverse path field.
## `Diblob`

### Fields
Diblob representation in digraph. 

- `diblob_id` - id of the diblob used by `GraphManager`.
- `parent_id` - id of the diblob which is the parent for diblob.
- `children` - ids of the diblobs which are children of the diblob.
- `nodes` - node ids (or diblob ids) embedded in diblob.

### Methods

- `_add_children(self, *child_ids: tuple[str])` - adds diblob_ids to the diblob.
- `_add_nodes(self, *node_ids: tuple[str])` - adds node_ids to the diblob.
# Digraph Manager
Digraph Manager is responsible for data structure managment. Is the core of entire package. 
DigrahmManager instance creation require digraph dict representation. For instance: 
```python
digraph_dict = {
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

graph_manager = GraphManager(digraph_dict)
```
