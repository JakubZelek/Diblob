
# Diblob

Diblob is the package for digraphs (pseudographs) computations.
Main assumption is to enable the user easily operate on the json digraphs representations. Because of the popular operations on subgraphs like treating entire subgraph as a point or working on the subgraph separately, the concept of diblob was introduced. 

# Data structure

The core of the diblob is the data structure, where every operation is managed by `GraphManager`. Operations are performed on `Node`, `Edge` and `Blob` components. 


<img width="518" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/1e5394ca-ac78-4e3c-90f7-948bb9a338be">


## `Node`
- `node_id` - id of the node used by `GraphManager`. 
- `diblob_id` - id of the diblob, where node is placed.
- `incoming_nodes` - list of node ids (tails of the edges for which node is head).
- `outgoing_nodes` - list of node ids (heads of the edges for which node is tail).

Incoming/outgoing nodes could be redundant (pseudographs are also considered).

## `Edge`
 - `path` - list of node ids (solution enable treat entire path as the edge).

## `Diblob`
- `diblob_id` - id of the diblob used by `GraphManager`.
- `parent_id` - id of the diblob which is the parent for diblob.
- `children` - ids of the diblobs which are children of the diblob.
- `nodes` - node ids (or diblob ids) embedded in diblob.

