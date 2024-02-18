# Diblob documentation
Diblob package consists of following modules:
- `components` - used by graph manager (node, edge, diblob).
- `digraph_manager` - core of the proposed data structure.
- `factory` - examples of graph_manager used for more complicated digraphs creation.
- `algorithms` - examples of use diblob with basic digraphs algorithms like DFS, DFSA (modified DFS) and Dijkstra algorithm.
- `exceptions` - used in modules.
- `tools` - for comfortable work with digraphs.

In entire package methods started with '_' are used by GraphManager (indirectly).

# Components
Components are used by GraphManager for data structure creation. Data Structure consist of instances of classes `Node`, `Edge` and `Diblob`.

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
Edge representation in digraph. Enable to treat some kinds of paths as one edge.

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
Digraph Manager is responsible for data structure management. Is the core of entire package. 
DigraphManager instance creation require digraph dict representation. For instance: 
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
In effect, following digraph has been created:

<img width="551" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/16aeb5fe-78ff-42d5-93a2-77e6d4a94a1f">

### Fields
- `diblobs` - dict where key, value equals diblob_id, Diblob object respectively (keep *B0*, *B1*, *B2* in the picture above).
- `nodes` - dict where key, value equals node_id,  Node object respectively (keep *A*, *B*, *C*, *D*, *E*, *F*, *G* in the picture above).
- `edges` - dict where key, value equals node_id,  list of Edge objects respectively. List is used because multiple edges with the same  
            head and tail are enabled (keeps edges *AB*, *AF*, *BC*, *BD*, *BE*, *CD*, *DE*, *DF*, *DG*, *FB*, *FG*, *GA* in the picture above).
- `root_diblob_id` - root blob_id which represents entire digraphs .Even if digraph doesn't have diblobs inside, entire graphs is treat as diblob. (*B0* in the picture above).

### Methods
- `construct` - helper function used in `__init__`.
- `get_diblobs_common_ancestor` - returns id of common ancestor of diblobs (diblobs have tree structure).
- `get_diblob_descendants` - returns set of diblob id's which are in the diblob subtree, where delivered node_id is the root.
- `get_diblob_edges` - returns set of all edge ids, set of incoming edge ids, set of outgoing edge ids and set of diblob descendants with considered diblob_id as side effect.
- `is_diblob_ancestor` - validates if diblob with id=potential_ancestors is the ancestor of the diblob with delivered diblob_id.
- `flatten` - removes diblobs with delivered ids (removing diblob doesn't implies nodes deletion. Nodes are transferred to the diblob direct ancestor). Root diblob cannot be flattened:

  <img width="813" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/2a6e0532-34b7-4dd2-ae34-d16311aba2e1">

- `gather` - accumulate nodes and diblobs into new diblob:
  
<img width="882" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/132d9ba1-5a09-4e2d-8578-5ef550da6d74">

- `compress_diblob` - compress diblob into single node:

<img width="947" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/2bca3160-1a4d-45b7-9a5a-2fabcc08cc39">

- `merge_edges` - merge edges if they are compatible (head of the first one should equals tail of the second one, and incoming / outgoing edges of the second one should equal 1)
- `get_multiple_edge_ids` - returns list of edge_ids with every occurrence.
- `remove_edges` - remove edges from the digraph (uses objects, no edge_ids)
- `connect_nodes` - creates edges from pair of node_ids.
- `remove_nodes` - remove nodes from the digraph (uses objects, no edge_ids).
- `add_nodes` - add nodes to the digraph (optionally diblob_id can be chosen. Set as root_id if not delivered).
- `compress_edges` - compress edges in the digraph (accumulates nodes with len(incoming_nodes) = len)outgoing_nodes) = 1):
  
<img width="596" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/e1447975-5ad3-49b0-96d9-d9c17131063e">

- `decompress_edges` - reverse operation to compress_edges:
  
<img width="605" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/4b066d0f-3e08-46e2-bd61-e0742ecf10d4">

- `inject` - takes other DigraphManager and inject it to the digraph in place of the selected node:

<img width="915" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/869d7c50-8791-4286-9f24-2964295f2c19">

- `decouple_edges` - convert pseudograph to digraph by edge decoupling:

<img width="814" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/23f69820-fcc8-4b44-880c-b92c49c521b3">

- `reverse_edges` - reverse selected edges (use object, not node_id).
- `sorted` - sort all fields of the digraph structure.
  
GraphManager has also magic methods which enables comfortable work on the structure:
- `__setitem__` enable during implementation new methods with easy components setting:
  
```python
"""
Note that maintaining the structure is covered by other methods. __set_item__ is used just for methods implementation.
For instance digraph_manager[('A', 'B')] = AB not implies that nodes 'A' and 'B' are connected in structure.
Edge object is just registered by GraphManager.

If you want to create correct edge use connect_nodes method  on structure without Edge.
"""
  


digraph_dict = {"B0": {}}
digraph_manager = DigraphManager(digraph_dict)
 
A = Node(node_id='A', diblob_id='B0', incoming_nodes=[], outgoing_nodes=[])
B = Node(node_id='B', diblob_id='B0', incoming_nodes=[], outgoing_nodes=[])
B1 = Diblob(children={}, diblob_id='B1', nodes=['A', 'B'], parent_id='B0')
AB = Edge(['A', 'B'])
 
digraph_manager['A'] = A
digraph_manager['B'] = B
digraph_manager['B1'] = B1
digraph_manager[('A', 'B')] = AB
```

- `__get_item__` enable getting object by it's registered id.
- `__contains__` check if specific id is registered by diblob.
- `__call__` can be used for diblob extraction. For example following code:
```python
digraph_dict = {
                "B0": {
                    "B2": {
                        "E": [{"B0": ["F"]}, {"B1": ["A"]}],
                        "C": ["D"],
                        "D": ["E", {"B0": ["F", "G"]}],
                    },
                    "G": [{"B1": ["A"]}, {"B2": ["D"]}],
                    "F": ["G", {"B1": ["B"]}],
                    "B1": {
                        "B": [{"B2": ["C", "D", "E"]}],
                        "A": ["B", {"B0": ["F"]}],
                    },
                },
                }

digraph_manager = DigraphManager(digraph_dict)
tools.display_digraph(digraph_manager('B1'))

```
returns 

```json
{
"B1": {
    "B": [{"B2": ["C", "D", "E"]}],
    "A": ["B", {"B0": ["F"]}],
},
}
```
Note that outgoing edges are saved. For cutting them use `cut_outgoing_edges` from tools.

# Factory 
Factory enables creation other types of digraphs based on delivered digraph. It's decoupled with GraphManager, because GraphManager working with it's own structure. 
<br><br>
Edge digraph and Biparite digraph can be created just for digraphs with only root diblobs.

## methods:
- `generate_edge_digraph` enable edge digraph creation (edges because nodes):
<img width="993" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/eb9e5376-f7c3-4788-a551-2738f8b5c26b">
In the example default `delimiter` and `reduce_value` was used. Delimiter add separator between node_ids during node_id creation in edge graph, reduce value enable cutting delimiter (for example if we use generate_edge_digraph second time in the graph on the right in the picture, we get for example node with id = "A|C|C|B" with default reduce value = 0, but "A|C|B" if reduce_value = 1 is set).

- `generate_bipartite_digraph` enable bipartite digraph creation:
  
<img width="862" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/c79954a3-f357-4aaa-9aa2-cb4f29df7eaf">

## Aghoritms
In order to working with diblob explanation, DFS, DFSA and Dijkstra algorithms are created. 
For more details check out algorithms.py directly in the code.

## Tools
Tools for diblob which are used for user friendly printing or cutting nodes in json. Tools don't interfere with diblob class, just working with output dict. 
