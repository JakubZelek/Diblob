
# Diblob

Diblob is the package for digraphs (pseudographs) computations.
Main assumption is to enable the user easily operate on the json digraphs representations. Package enables treat subgraph as poin or subraphs extractation for future work. 
Package based on basic python structures (not depend on non-basic packages)

# Data structure

The core of the diblob is the data structure, where every operation is managed by `GraphManager`. Operations are performed on `Node`, `Edge` and `Blob` components. 


<img width="518" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/1e5394ca-ac78-4e3c-90f7-948bb9a338be">


## `Node`
Node representation in digraph.
- `node_id` - id of the node used by `GraphManager`. 
- `diblob_id` - id of the diblob, where node is placed.
- `incoming_nodes` - list of node ids (tails of the edges for which node is head).
- `outgoing_nodes` - list of node ids (heads of the edges for which node is tail).

Incoming/outgoing nodes could be redundant (pseudographs are also considered).

## `Edge`
Edge representation in digraph.
 - `path` - list of node ids.

Path is keep as list, which enables treat chain of node ids as edge:

<img width="521" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/048eaba4-e8f2-4940-9312-c2edb72804b7">


## `Diblob`
Diblob representation in digraph. 
- `diblob_id` - id of the diblob used by `GraphManager`.
- `parent_id` - id of the diblob which is the parent for diblob.
- `children` - ids of the diblobs which are children of the diblob.
- `nodes` - node ids (or diblob ids) embedded in diblob.

Diblobs which share the same graph creates tree-based structure. Moreover, entire graph is also treat as diblob (root):

<img width="760" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/04efed64-f957-4feb-81f9-ac2af97a2034">


