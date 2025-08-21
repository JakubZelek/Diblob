
# Diblob

Diblob is a lightweight Python package for test case coverage of directed graphs (digraphs), with a focus on SESE graphs (Single Entry, Single Exit — graphs with one source and one sink). It is primarily developed for testing purposes and provides a simple, dependency-free solution built entirely on standard Python data structures.

## Overview

The package focuses on JSON-based representations of digraphs, enabling intuitive and flexible operations. It provides functionality to:
- Treat a subgraph as a node for higher-level abstractions. 
- Extract subgraphs for further analysis or processing.
- Generate test coverage based on multiple criteria ([Go to Testing Criterions](#testing-criterions)):
  - Node Coverage (test cases streaming),
  - Edge Coverage (including various variants, see [papier](http://sciencedirect.com/science/article/abs/pii/S0957417425008383))
  - NSwitch Coverage,
  - Cycle Coverage (test cases streaming),
  - Simple Paths Coverage (test cases streaming, separated from simple cycles),
  - Prime Path Coverage (test cases streaming),
  - Acyclic Path (NPath) Coverage (test cases streaming).


## Installation
Package requires python with version >= 3.10.
- The package can be installed using [pip](https://pypi.org/project/diblob/) (`pip install diblob`).
- For the packages necessary only for testing, use `pip install -r requirements.txt`.

# Structure of the solution

The core of Diblob revolves around its data structure, managed by the GraphManager. Operations within Diblob are executed on Node, Edge, and Blob components.


<img width="518" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/1e5394ca-ac78-4e3c-90f7-948bb9a338be">


## Node
The Node representation in digraph, that consists of the following fields:

- `node_id`: The identifier for the node used by GraphManager.
- `diblob_id`: The identifier of the diblob where the node is located.
- `incoming_nodes`: A list of node identifiers (tails of the edges for which the node is the head).
- `outgoing_nodes`: A list of node identifiers (heads of the edges for which the node is the tail).

Both incoming and outgoing nodes can be redundant, as pseudographs are accommodated as well.

## Edge
The representation of an edge in a digraph:
 - `path`: A list of node IDs that the edge connects.

## Diblob
The representation of a diblob within a digraph:
- `diblob_id`: The identifier for the diblob, used by GraphManager.
- `parent_id`: The identifier of the parent diblob to this diblob.
- `children`: IDs of diblobs that are children of this diblob.
- `nodes`: diblob IDs contained within this diblob.

Diblobs sharing the same graph form a tree-based structure. Furthermore, the entire graph is treated as a diblob (root_id).

<img width="760" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/04efed64-f957-4feb-81f9-ac2af97a2034">

## Examples

A digraph data structure can be created as follows:
```python
from diblob import DigraphManager

digraph_dict = {"B0": {"A": ["B", "F"],
                       "B": ["C", "D", "E"],
                       "C": ["D"],
                       "D": ["E", "F", "G"],
                       "E": ["F", "A"],
                       "F": ["G", "B"],
                       "G": ["A", "D"]}}

digraph_manager = DigraphManager(digraph_dict)
```
Note that digraphs stored in a JSON files can be easily loaded using json.load and applied as the inputs to the DigraphManager.
To illustrate, let's create blobs B1 and B2 in the digraph, each containing specific nodes. 
Blob B1 will include nodes A and B, while B2 will encompass nodes C, D, and E:

```python
from diblob import tools

digraph_manager.gather('B1', {'A', 'B'})
digraph_manager.gather('B2', {'C', 'D', 'E'})

tools.display_digraph(digraph_manager('B0'))
```
The result is as follows (where display_digraph is a helper function used for printing a human-friendly output in Python):
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
Now, let's compress the created diblobs into nodes:
```python
digraph_manager.compress_diblob('B1')
digraph_manager.compress_diblob('B2')

tools.display_digraph(digraph_manager('B0'))
```
The result is as follows:
```json
{
"B0": {
    "F": ["G", "B1"],
    "B2": ["F", "B1", "G", "F"],
    "B1": ["F", "B2", "B2", "B2"],
    "G": ["B1", "B2"],
},
}
```
# Documentation
The Diblob package is composed of the following modules:
- `components`: Utilized by the Graph Manager, this module includes node, edge, and diblob components.
- `digraph_manager`: Serves as the core of the proposed data structure.
- `factory`: Provides examples of using the graph_manager for creating more complex digraphs.
- `algorithms`: Contains examples of employing Diblob with basic digraph algorithms such as DFS, DFSA (a modified version of DFS), and the Dijkstra algorithm.
- `exceptions`: Defines exceptions that are utilized across the modules.
- `tools`: Offers utilities for convenient work with digraphs.
- `testing_criterions`: Contains test coverage algorithms for test suits generation.


Within the entire package, methods prefixed with an underscore ('_') are intended for internal use by the GraphManager.

# Components
Components are utilized by the GraphManager for the creation of the data structure, which consists of instances of the Node, Edge, and Diblob classes.

## Node
Node Representation in a Digraph:
Nodes in a digraph can have overlapping incoming and outgoing nodes, accommodating pseudographs as well.

### Fields
- `node_id`: The identifier of the node, used by GraphManager.
- `diblob_id`: The identifier of the diblob in which the node is located.
- `incoming_nodes`: A list of node IDs (tails of the edges for which this node is the head).
- `outgoing_nodes`: A list of node IDs (heads of the edges for which this node is the tail).
### Methods
- `get_incoming_edges(self)`: Returns a set of edge IDs where the node is the head.
- `get_outgoing_edges(self)`: Returns a set of edge IDs where the node is the tail.
- `incoming_dim(self)`: Returns the number of incoming nodes.
- `outgoing_dim(self)`: Returns the number of outgoing nodes.
- `_add_incoming(self, node_id: str)`: Adds a new node_id to incoming_nodes.
- `_add_outgoing(self, node_id: str)`: Adds a new node_id to outgoing_nodes.
- `_rm_incoming(self, node_id: str)`: Removes a node_id from incoming_nodes.
- `_rm_outgoing(self, node_id: str)`: Removes a node_id from outgoing_nodes.

## Edge
Edge Representation in a Digraph:
This representation allows for treating certain types of paths as a single edge, 
facilitating more efficient and simplified graph analyses.

### Fields

 - `path`: A list of node IDs that constitute the sequence of nodes this edge traverses.

The path is maintained as a list, enabling the treatment of a chain of node IDs as a single edge. 
This approach is particularly useful in operations like `compress_edges`, where multiple consecutive edges are consolidated into one for simplified graph representation.

<img width="521" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/048eaba4-e8f2-4940-9312-c2edb72804b7">

### Methods
- `get_tail_and_head(self)`: Returns the tail and head nodes of the edge, indicating the direction of traversal.
- `get_id(self)`: Returns the edge_id, uniquely identifying the edge by its head and tail nodes.
- `_reverse(self)`: Reverses the order of nodes in the path field, effectively inverting the direction of the edge.
## Diblob

### Fields
Diblob Representation in a Digraph:

- `diblob_id`: The unique identifier for the diblob, utilized by GraphManager.
- `parent_id`: The identifier of the parent diblob, establishing a hierarchical relationship within the graph.
- `children`: A list of identifiers for diblobs that are children of this diblob, further defining the structure of the graph.
- `nodes`: A list of node IDs (or diblob IDs) that are contained within this diblob, representing the diblob's internal structure.

### Methods

- `_add_children(self, *child_ids: tuple[str])`: Adds one or more diblob_ids to the diblob, expanding its child elements.
- `_add_nodes(self, *node_ids: tuple[str])`: Incorporates one or more node_ids into the diblob, enhancing its internal structure.
# Digraph Manager
The Digraph Manager is at the heart of the package, overseeing the management of the data structure. It is crucial for the entire package's functionality. To create an instance of `DigraphManager`, a dictionary representation of the digraph is required, such as:
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
As a result, the following digraph has been created:

<img width="469" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/642c8ca9-027b-47a3-acd2-6775bb359dd9">



### Fields
- `diblobs`: A dictionary where each key-value pair corresponds to diblob_id and its associated Diblob object, respectively. This includes `B0`, `B1`, and `B2` as shown in the diagram.
- `nodes`: A dictionary where each key-value pair corresponds to node_id and its associated Node object, respectively. This includes nodes `A`, `B`, `C`, `D`, `E`, `F`, and `G` as depicted in the diagram.
- `edges`: A dictionary where each key-value pair corresponds to node_id and a list of Edge objects, respectively. A list is used to accommodate multiple edges sharing the same head and tail, encapsulating edges `AB`, `AF`, `BC`, `BD`, `BE`, `CD`, `DE`, `DF`, `DG`, `FB`, `FG`, and `GA` as illustrated in the diagram.
- `root_diblob_id`: The root `diblob_id` representing the entire digraph. Even if the digraph contains no internal diblobs, the entire graph is treated as a single diblob (`B0` in the diagram)..

### Methods
- `construct(self, diblob_id: str, graph_dict_representation: dict, gather_dict: dict, edges_to_connect: list[str])`
  - `diblob_id: str`: The ID of the diblob being considered (for recursion).
  - `graph_dict_representation: dict`: The provided dictionary representation of the digraph.
  - `gather_dict: dict` A dictionary used to accumulate the results of recursion.
  - `edges_to_connect: list[str]`: A list of edge IDs to be connected during the digraph's construction.
<br /><br />  Constructs a diblob using recursion. This helper function is utilized in the __init__ method for diblob construction.
- `get_diblobs_common_ancestor(self, diblob_id1: str, diblob_id2: str)`
  - `diblob_id1: str`: The ID of the first diblob.
  - `diblob_id2: str`: The ID of the second diblob.
<br /><br /> Returns the `diblob_id` of the common ancestor of two diblobs, based on their IDs. Diblobs are structured as a tree.
- `get_diblob_descendants(self, diblob_id: str)`
  - `diblob_id: str`: The ID of the diblob whose descendants are being searched.
<br /><br /> Returns a set of diblob_ids that are descendants in the subtree for which the diblob with the given diblob_id is the root.
- `get_diblob_edges(self, diblob_id: str)`
  - `diblob_id: str`: The ID of the diblob being considered.
<br /><br /> Returns a set of all edge IDs, incoming edge IDs, outgoing edge IDs, and the set of diblob descendants for the specified diblob_id. This method also has side effects on the considered diblob.
- `is_diblob_ancestor(self, potential_ancestors: set, diblob_id: str)`
  - `potential_ancestors: set`: A set of IDs of potential ancestor diblobs.
  - `diblob_id: str`: The ID of the diblob being considered.
<br /><br /> Validates whether a diblob with the given diblob_id is an ancestor among the provided potential ancestors.
- `flatten(self, *diblob_ids: tuple[str])`
  - `*diblob_ids: tuple[str]`: IDs of the diblobs to be flattened.
<br /><br /> Flattens the structure by removing diblobs with the provided IDs. Note that removing a diblob does not imply the deletion of its nodes; instead, nodes are transferred to the diblob's direct ancestor. The root diblob cannot be flattened.

  <img width="966" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/2fce8b1b-4668-48c6-afe3-1a9849700106">



- `gather(self, new_diblob_id: str, node_ids: set[str])`
  - `new_diblob_id: str`: The ID of the new diblob that will be created.
  - `node_ids: set[str]`: The IDs of the nodes that will be included in the new diblob.
 <br /><br /> Accumulates nodes and existing diblobs into a new diblob specified by new_diblob_id.
  
<img width="1056" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/96e93370-fc6f-4c0d-8002-d5f930dd8e0a">


- `compress_diblob(self, diblob_id: str)`
  - `diblob_id: str`: The ID of the Diblob that is to be compressed.
 <br /><br /> This method compresses the specified Diblob into a single node, effectively consolidating its structure for simplified representation:

<img width="939" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/589d935f-0dab-49c7-aec3-22be0be92404">

- `join_diblobs(self, diblob_fst_id: str, diblob_snd_id: str, join_id: str)`
  - `diblob_fst_id: str`: The ID of the first Diblob that is to be joined.
  - `diblob_snd_id: str`: The ID of the second Diblob that is to be compressed.
  - `join_id: str`: The ID of the joined Diblob.
 <br /><br /> This method join two diblobs which have the same `parent_id`:

<img width="1028" alt="image" src="https://github.com/JakubZelek/Diblob/assets/72871011/a74ecf81-bee4-4e81-b598-e890fa14ec21">

- `merge_edges(self, edge_1: Edge, edge_2: Edge)`
  - `edge_1: Edge`: The first edge to be merged.
  - `edge_2: Edge`: The second edge to be merged.
 <br /><br /> Merges two compatible edges into one, provided the head of edge_1 is the same as the tail of edge_2, and edge_2 has exactly one incoming and one outgoing edge.
- `get_multiple_edge_ids(self, *edge_ids : tuple[str])`
  - `*edge_ids : tuple[str]`: The edge IDs for which the operation will be performed.
<br /><br /> Returns a list of edge IDs, including every occurrence of the specified edges.
- `remove_edges(self, *edges: tuple[Edge])`
  - `*edges: tuple[Edge]`: The edges to be removed.
<br /><br /> Removes the specified edges from the digraph. This method operates directly on edge objects, not on edge IDs.
- `connect_nodes(self, *edge_ids: tuple[str])`
  - `*edge_ids: tuple[str]`: Pairs of node IDs for which edges will be created.
<br /><br /> Creates edges between pairs of nodes.
- `remove_nodes(self, *nodes: tuple[Node])`
  - `*nodes: tuple[Node]`: The nodes to be removed.
<br /><br /> Removes the specified nodes from the digraph. This method operates directly on node objects, not on node IDs.
- `add_nodes(self, *node_ids: tuple[str], diblob_id: str=None)`
  - `*node_ids: tuple[str]`: The node IDs to be added.
  - `diblob_id: str`: The diblob ID where the nodes will be placed. If not provided, nodes are added to the root diblob.
<br /><br /> Adds nodes to the digraph. Optionally, a diblob_id can be specified to place the nodes within a specific diblob; otherwise, they are added to the root.
- `compress_edges(self)` - Compresses edges in the digraph by accumulating nodes where both the number of incoming and outgoing nodes is exactly one.
  
<img width="596" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/e1447975-5ad3-49b0-96d9-d9c17131063e">

- `decompress_edges(self)` Performs the reverse operation of `compress_edges`.
  
<img width="605" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/4b066d0f-3e08-46e2-bd61-e0742ecf10d4">

- `inject(self, digraph_manager: GraphManager, node_id: str)`
  - `digraph_manager: DiraphManager`: The digraph that will be injected.
  - `node_id`: The ID of the node that will be replaced by the injected digraph.
<br /><br /> Incorporates another GraphManager instance into the current digraph by replacing a specified node with the entire structure of the other digraph:

<img width="1075" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/614e76e0-9a33-46d0-9439-397f29324d11">


- `decouple_edges(self)`: Transforms a pseudograph into a digraph by decoupling edges.

<img width="814" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/23f69820-fcc8-4b44-880c-b92c49c521b3">

- `reverse_edges(self, *edges: tuple[Edge])`
- `*edges: tuple[Edge]`: The edges to be reversed.
<br /><br />  Reverses the direction of the specified edges within the digraph. This operation is performed on the edge objects themselves, rather than their node IDs.
- `sorted(self)`: Sorts all elements within the digraph structure, ensuring an orderly arrangement of nodes, edges, and possibly diblobs.
  
GraphManager has also magic methods which enables comfortable work on the structure:
- `__setitem__`: Enables working with structure in new methods:
  
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

- `__get_item__`: Enables retrieval of an object using its registered ID. This method simplifies accessing nodes, edges, or diblobs directly by their identifiers.
- `__contains__`: Checks if a specific ID is registered within the graph. This can be particularly useful for verifying the presence of a node, edge, or diblob without directly accessing the item.
- `__call__`: Facilitates operations such as diblob extraction, making the GraphManager more versatile. For instance, the following code snippet demonstrates how to use this method:
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
Please note that outgoing edges are preserved. To remove them, utilize the `cut_outgoing_edges` function available in the `tools` module.

# Factory 
The Factory is designed to facilitate the creation of various types of digraphs from a given input digraph. It operates independently from the GraphManager to ensure separation of concerns, as the GraphManager is dedicated to managing its internal graph structure.
<br><br>
Edge digraphs and Bipartite digraphs can only be created from digraphs that consist solely of root diblobs.

## methods:
- `generate_edge_digraph(digraph_manager: DigraphManager, reduce_value: int = 0, delimiter: str = '|')`
  - `digraph_manager: DigraphManager`: The DigraphManager instance that serves as the foundation for constructing the edge digraph.
  - `reduce_value: int`: Specifies the reduction value used as a numerical delimiter.
  - `delimiter: str`: The delimiter employed for creating node IDs derived from edges.
<br><br> Enables the creation of an edge digraph, where edges are transformed into nodes:
<img width="1022" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/151e5f9b-35ee-4f43-8613-3c908880efd0">

In the example default `delimiter` and `reduce_value` was used. Delimiter add separator between node_ids during node_id creation in edge graph, reduce value enable cutting delimiter (for example if we use generate_edge_digraph second time in the graph on the right in the picture, we get for instance the node with node_id = `"A|C|C|B"` with default reduce value = 0, but `"A|C|B"` if reduce_value = 1 is set).

- `generate_bipartite_digraph(digraph_manager: DigraphManager)`
  - `digraph_manager: DigraphManager` - DigraphManager which is the base for bipartite digraph contruction.
 <br><br> enable bipartite digraph creation:

<img width="1028" alt="image" src="https://github.com/Zeleczek-kodowniczek/Diblob/assets/72871011/1f3a686e-c1ef-4a41-8fa2-58a67a83fd12">

- `generate_flow_digraph(digraph_manager: DigraphManager)`
  - `digraph_manager: DigraphManager` - DigraphManager which is the base for flow digraph contruction.
 <br><br> enable flow digraph creation (commonly used in control flow algorithm like the Ford-Fulkerson algorithm):

<img width="944" alt="image" src="https://github.com/JakubZelek/Diblob/assets/72871011/9739207a-73d9-4ca4-98c8-e41116a17509">

## Algorithms
In order to working with diblob explanation, DFS, DFSA and Dijkstra algorithms are created. 

- DFS - Deep first search alghoritm.
- DFSA - modification of the DFS (with the nodes visit time)
- DijkstraAlgorithm - the shortes paths between node and the others.

Algorithm use duck typing. GraphManager instance have to be delivered during creation. Then `run` methon can be used on selected node_id (in DijkstraAlgorithm `cost_function` as a dict can be also delivered)

Example of run:

 <br><br>
```python
from diblob import DigraphManager
from diblob.algorithms import DFS, DFSA, DijkstraAlgorithm

digraph_dict = {"B0": {"A": ["B", "F"],
                       "B": ["C", "D", "E"],
                       "C": ["D"],
                       "D": ["E", "F", "G"],
                       "E": ["F", "A"],
                       "F": ["G", "B"],
                       "G": ["A", "D"]}}

digraph_manager = DigraphManager(digraph_dict)

dfs = DFS(digraph_manager)
dfsa = DFSA(digraph_manager)
da = DijkstraAlgorithm(digraph_manager)

dfs.run('A')
dfsa.run('B')
da.run('C')
```
## Tools
Tools for diblob which are used for user friendly printing or cutting nodes in json.
Tools deliver following functions:
- `display_digraph(d: dict, indent=0)`: Enables printing dict in json format (work as print).
- `cut_outgoing_edges(digraph_manager, diblob_id: str)`: Cuts outgoing nodes of the Digraph (can be used with GraphManager `__call__`)
- `sort_outgoing_nodes_in_dict_repr(node_lst: list)`: Sorts outgoing nodes.
<br> Example: `['C', 'B', 'A', {'G1': ['A', 'C', 'B']}] -> ['A', 'B', 'C', {'G1': ['A', 'B', 'C']}]`
- `list_groupby`: Works like groupby from itertools (no need data to be sorted).

  
## Generators
Random digraphs can be generated using generators module. 
Digraphs which can be generated:
- random cycle
- random directed acyclic graph
- random strongly connected graph (as a sum of cycles)
- random graph as a combination of DAG and the others (injection)

example of usage can be found in notebooks: 
https://github.com/JakubZelek/Diblob/tree/main/notebooks

# Testing Criterions
The package enables to generate test suits for SESE digraphs based on the specific criterions.

The example of the usage will be presented on this particular digraphs:
<img width="800" alt="image" src="https://github.com/user-attachments/assets/c8b5b7c5-e823-4522-a4eb-0015082c8846">
## Node Coverage

The goal of this criterion is to cover all nodes in the graph, so we are looking for a test suit $P = [p_1, p_2, \dots, p_n]$, such that $\forall v \in V$, $\exists p \in P$ such that $v \in p$.


To generate test suit let's use `NodeCoverage` from `testing_criterions`: 
```python
from diblob.digraph_manager import DigraphManager
from testing_criterions.NodeCoverage import NodeCoverage

digraph_manager = DigraphManager({"B0": {"S": ["1"],
                                         "1": ["2", "3", "4"],
                                         "T": [],
                                         "6": ["1"],
                                         "4": ["5"],
                                         "3": ["5"],
                                         "5": ["6", "T"],
                                         "2": ["5"],
                                     }})
node_coverage = NodeCoverage(digraph_manager)
for test_case in node_coverage.get_test_cases():
   print(test_case)

```
The output is as follows:
```python
 ["S", "1", "2", "5", "6", "1", "2", "5", "T"],
 ["S", "1", "2", "5", "T"],
 ["S", "1", "3", "5", "T"],
 ["S", "1", "4", "5", "T"]
```
The algorithm working as follows:
- run DFS on 'S',
- run DijkstraAlgorithm on reversed graph on 'T',
- connect paths generathed from the first and second step appriopriatelly.

`node_coverage.get_test_cases()` is a generator. In effect, there is no need to generate entire test_suit at once, that's enable testers starting testing immediatelly - before he generate entire suit.
Note that the test case `["S", "1", "2", "5", "T"]` has all nodes from `["S", "1", "2", "5", "6", "1", "2", "5", "T"]`. In effect, it would be removed from test suit and node coverage criterion would be met. It could be easily done by the user accumulating test_cases and them removing overlapping ones, but then the user lose the effect of generator.

## Edge Coverage
In this criterion we want to cover all edges in the digraph (as a main criterion), so we are looking for a test suit $P = [p_1, p_2, \dots, p_n]$, such that $\forall e \in E$, $\exists p \in P$ such that $e \in E$.

Edge coverage use Chinese Postman Tour algorithm to generate optimal test suit for the following criterions:
- Minimal total cost of the test suit (weighted edges).
- Minimal number of test cases in the suit.
- Set number of test cases in the suit, minimalize the cost.

Criterions and algorithms are described in this [papier](https://www.sciencedirect.com/science/article/pii/S0957417425008383?dgcid=author).
The example of the usage is as follows:

```python
from diblob.digraph_manager import DigraphManager
from testing_criterions.EdgeCoverage import EdgeCoverage

digraph_manager = DigraphManager({"B0": {"S": ["1"],
                                         "1": ["2", "3", "4"],
                                         "T": [],
                                         "6": ["1"],
                                         "4": ["5"],
                                         "3": ["5"],
                                         "5": ["6", "T"],
                                         "2": ["5"],
                                     }})
edge_coverage = EdgeCoverage(digraph_manager)

test_cases = edge_coverage.get_test_cases_minimal_number_of_test_cases(
    cost_function={("5", "6"): 10, ("6", "1"): 10}, default_cost=1
)

test_cases = edge_coverage.get_test_cases_minimal_total_cost(
    cost_function={("5", "6"): 10, ("6", "1"): 10}, default_cost=1
)

test_cases = edge_coverage.get_test_cases_set_number_of_test_cases(
    cost_function={("5", "6"): 10, ("6", "1"): 10}, default_cost=1, k=3
)
```
The outputs:

```python
#minimal_number_of_test_cases
[['S', '1', '3', '5', '6', '1', '2', '5', '6', '1', '4', '5', 'T']]
#minimal_total_cost
[['S', '1', '3', '5', 'T'], ['S', '1', '4', '5', '6', '1', '2', '5', 'T']]
#set_number_of_test_cases
[['S', '1', '4', '5', 'T'], ['S', '1', '2', '5', 'T'], ['S', '1', '3', '5', '6', '1', '2', '5', 'T']]
```
Note the argument applied to the functions:
  - `default_cost`: the default cost of all edges
  - `cost_function`: the costs of the edges (dict), override the `default_cost`
  - `k`: number of the test_cases in `get_test_cases_set_number_of_test_cases` method

## NSwitch Coverage
NSwitch coverage is a software testing criterion that requires tests to cover all possible sequences of exactly N transitions between states in a system's control flow or state machine.

For example:
  - 1-Switch coverage ensures that every individual transition is tested (equivalent to edge coverage),
  - 2-Switch coverage ensures that every possible pair of consecutive transitions is tested (all adjacent edges),
  - and so on.

The algorithm uses mechanism described in the same [papier](https://www.sciencedirect.com/science/article/pii/S0957417425008383?dgcid=author).

The strategy is as follows:
  - For choosen `n` create `DiblobFactory.generate_edge_digraph` recursivelly (n-1 times) and accumulate costs of edges,
  - Add 'S' and 'T' to keep the graph requirements, set the cost of the new edges to `default_cost`.
  - Run EdgeCoverage algorithm for the generated digraph

The example of the usage:

```python
from diblob.digraph_manager import DigraphManager
from testing_criterions.NSwitchCoverage import NSwitchCoverage

digraph_manager = DigraphManager({"B0": {"S": ["1"],
                                         "1": ["2", "3", "4"],
                                         "T": [],
                                         "6": ["1"],
                                         "4": ["5"],
                                         "3": ["5"],
                                         "5": ["6", "T"],
                                         "2": ["5"],
                                     }})
node_coverage = NSwitchCoverage(digraph_manager)

test_cases = edge_coverage.get_test_cases_minimal_number_of_test_cases(
    cost_function={("5", "6"): 10, ("6", "1"): 10}, default_cost=1
)

test_cases = edge_coverage.get_test_cases_minimal_total_cost(
    cost_function={("5", "6"): 10, ("6", "1"): 10}, default_cost=1
)

test_cases = edge_coverage.get_test_cases_set_number_of_test_cases(
    cost_function={("5", "6"): 10, ("6", "1"): 10}, default_cost=1, k=3
)
```
Note, that the methods are exactly the same as in the edge coverage (because in practice, the criterion is edge coverage on the modified graph). The result is as follows:
```python
#minimal_number_of_test_cases
[['S', '1', '2', '5', '6', '1', '2', '5', 'T'], ['S', '1', '3', '5', '6', '1', '3', '5', 'T'], ['S', '1', '4', '5', '6', '1', '4', '5', 'T']]
#minimal_total_cost
[['S', '1', '2', '5', '6', '1', '2', '5', 'T'], ['S', '1', '3', '5', '6', '1', '3', '5', 'T'], ['S', '1', '4', '5', '6', '1', '4', '5', 'T']]
#set_number_of_test_cases
[['S', '1', '2', '5', '6', '1', '2', '5', 'T'], ['S', '1', '3', '5', '6', '1', '3', '5', 'T'], ['S', '1', '4', '5', 'T'], ['S', '1', '4', '5', '6', '1', '4', '5', 'T']]
```
## Simple Cycle Coverage

The implementation uses [Johnson Algorithm](https://arxiv.org/pdf/2105.10094) for cycles. The strategy is as follows:
  - Decompose the digraph into strongly connected components using Tarjan algorithm,
  - Starting from 'S' go to the next cycle (going through the strongly connected components),
  - Try accumulate cycles until reach `maksimal_number_of_cycles` going through the cycles. If it's not possible, go to 'T',
  - Go to 'T' if next cycle cannot be reached or `maksimal_number_of_cycles` is achieved.

In effect, the solution returns the generator for test cases as in the Node Coverage criterion.
The example usage is as follows:

```python
from diblob.digraph_manager import DigraphManager
from testing_criterions.SimpleCycleCoverage import SimpleCycleCoverage

digraph_manager = DigraphManager({"B0": {"S": ["1"],
                                         "1": ["2", "3", "4"],
                                         "T": [],
                                         "6": ["1"],
                                         "4": ["5"],
                                         "3": ["5"],
                                         "5": ["6", "T"],
                                         "2": ["5"],
                                     }})
simple_cycle = SimpleCycleCoverage(digraph_manager)

for test_case in simple_cycle.get_test_cases(maksimal_number_of_cycles=1):
   print(test_case)

for test_case in simple_cycle.get_test_cases(maksimal_number_of_cycles=5):
   print(test_case)

```

The results are as follows:

```python
#maksimal_number_of_cycles=1
["S", "1", "2", "5", "6", "1", "2", "5", "T"],
["S", "1", "3", "5", "6", "1", "2", "5", "T"],
["S", "1", "4", "5", "6", "1", "2", "5", "T"]

#maksimal_number_of_cycles=5
["S", "1", "2", "5", "6", "1", "3", "5", "6", "1", "4", "5", "6", "1", "2", "5", "T"]
```
  
In the first scenario, where algorithm find the cycle, immediatelly go to the 'T', In the second scenatio, it try to accumulate 5 simple cycles,
because in the graph there is just 3 simple cycles and entire graph can be covered with the single test_case, the one test_case is returned.

## Simple Paths Coverage
The Simple Path is a path, that cannot be extended backward or forward, and does'n not contain repeated nodes.

The Algorith uses [Johnson Algorithm](https://arxiv.org/pdf/2105.10094) for cycles on the modified graph (just first iteration of the jonson algorithm, on added node).
The strategy is as follows:
- for every node, construct new digraph adding one artificial node and connect it appropriatelly with the candidates for simple cycles,
- Run the modified Jonson Algorithm (only one iteration).

In effect we obtained the generator for Simple Paths.
The example usage is as follows:
```python
from diblob.digraph_manager import DigraphManager
from testing_criterions.SimplePathsCoverage import SimplePathsCoverage

digraph_manager = DigraphManager({"B0": {"S": ["1"],
                                         "1": ["2", "3", "4"],
                                         "T": [],
                                         "6": ["1"],
                                         "4": ["5"],
                                         "3": ["5"],
                                         "5": ["6", "T"],
                                         "2": ["5"],
                                     }})
simple_path = SimplePathsCoverage(digraph_manager)

for test_case in simple_path.get_test_cases(max_number_of_simple_paths_in_single_test_case=1):
   print(test_case)



```
The result is as follows:

```python
['S', '1', '2', '5', '6', '1', '2', '5', 'T']
['S', '1', '2', '5', 'T']
['S', '1', '3', '5', '6', '1', '2', '5', 'T']
['S', '1', '3', '5', 'T']
['S', '1', '4', '5', '6', '1', '2', '5', 'T']
['S', '1', '4', '5', 'T']
['S', '1', '2', '5', '6', '1', '2', '5', 'T']
['S', '1', '2', '5', '6', '1', '3', '5', 'T']
['S', '1', '2', '5', '6', '1', '4', '5', 'T']
['S', '1', '4', '5', '6', '1', '2', '5', 'T']
['S', '1', '4', '5', '6', '1', '3', '5', 'T']
['S', '1', '3', '5', '6', '1', '2', '5', 'T']
['S', '1', '3', '5', '6', '1', '4', '5', 'T']
['S', '1', '2', '5', '6', '1', '3', '5', 'T']
['S', '1', '2', '5', '6', '1', '4', '5', 'T']
    
```

## Prime Paths Coverage
The Prime Path Coverage criterion is described in the following [papier](https://arxiv.org/abs/1809.08446).
This is the combination of Simple Paths Coverage and Simple Cycle Coverage.

The example usage is as follows:

```python
from diblob.digraph_manager import DigraphManager
from testing_criterions.PrimePathCoverage import PrimePathCoverage

digraph_manager = DigraphManager({"B0": {"S": ["1"],
                                         "1": ["2", "3", "4"],
                                         "T": [],
                                         "6": ["1"],
                                         "4": ["5"],
                                         "3": ["5"],
                                         "5": ["6", "T"],
                                         "2": ["5"],
                                     }})
prime_path = PrimePathCoverage(digraph_manager)

for test_case in prime_path.get_test_cases(1):
   print(test_cases)

```
With the result as a combination of  Simple Paths Coverage and Simple Cycle Coverage:

```python
['S', '1', '2', '5', '6', '1', '2', '5', '6', '1', '2', '5', 'T'],
['S', '1', '3', '5', '6', '1', '3', '5', '6', '1', '2', '5', 'T'],
['S', '1', '4', '5', '6', '1', '4', '5', '6', '1', '2', '5', 'T'],
['S', '1', '2', '5', '6', '1', '2', '5', 'T'],
['S', '1', '2', '5', 'T'],
['S', '1', '3', '5', '6', '1', '2', '5', 'T'],
['S', '1', '3', '5', 'T'],
['S', '1', '4', '5', '6', '1', '2', '5', 'T'],
['S', '1', '4', '5', 'T'],
['S', '1', '2', '5', '6', '1', '2', '5', 'T'],
['S', '1', '2', '5', '6', '1', '3', '5', 'T'],
['S', '1', '2', '5', '6', '1', '4', '5', 'T'],
['S', '1', '4', '5', '6', '1', '2', '5', 'T'],
['S', '1', '4', '5', '6', '1', '3', '5', 'T'],
['S', '1', '3', '5', '6', '1', '2', '5', 'T'],
['S', '1', '3', '5', '6', '1', '4', '5', 'T'],
['S', '1', '2', '5', '6', '1', '3', '5', 'T'],
['S', '1', '2', '5', '6', '1', '4', '5', 'T']
```
Note, that the test_cases are also get from generator (there is no need to generate entire test_suit at one) In this case is very usefull, because the number of prime paths grows very fast.

## Acyclic Path Coverage (NPATH)
The NPath Coverage is a metric, that enable to extend simple paths with:
- Cycles with common node in the path for n=2,
- Cycles with common node in the path edge for n=3,
- and so on.

The algorithm is as follows:
- generate new digraph with `DiblobFactory.generate_edge_digraph` recursivelly (run `n-1` times), in effect, if we enable common nodes for n=2, we remove them with operation and just looking for Simple Paths (and so on)
- Run Simple Path Criterion.

The example usage is as follows:

```python
from diblob.digraph_manager import DigraphManager
from testing_criterions.NPathCoverage import NPathCoverage

digraph_manager = DigraphManager({"B0": {"S": ["1"],
                                         "1": ["2", "3", "4"],
                                         "T": [],
                                         "6": ["1"],
                                         "4": ["5"],
                                         "3": ["5"],
                                         "5": ["6", "T"],
                                         "2": ["5"],
                                     }})
n_paths = NPathCoverage(digraph_manager)

for test_case in n_paths.get_test_cases(1):
   print(test_cases)

```

The result is as follows:

```python
['S', '1', '2', '5', '6', '1', '2', '5', '6', '1', '2', '5', 'T']
['S', '1', '2', '5', '6', '1', '3', '5', '6', '1', '2', '5', 'T']
['S', '1', '2', '5', '6', '1', '4', '5', '6', '1', '2', '5', 'T']
['S', '1', '2', '5', '6', '1', '2', '5', 'T']
['S', '1', '3', '5', '6', '1', '3', '5', 'T']
['S', '1', '4', '5', '6', '1', '4', '5', 'T']
['S', '1', '2', '5', 'T']
['S', '1', '2', '5', '6', '1', '3', '5', 'T']
['S', '1', '2', '5', '6', '1', '4', '5', 'T']
['S', '1', '3', '5', 'T']
['S', '1', '3', '5', '6', '1', '2', '5', 'T']
['S', '1', '3', '5', '6', '1', '4', '5', 'T']
['S', '1', '4', '5', '6', '1', '2', '5', 'T']
['S', '1', '4', '5', '6', '1', '3', '5', 'T']
['S', '1', '4', '5', 'T']
```
## Future Works
Future Works

Planned improvements for Diblob include:

  - New testing criteria will be added to expand coverage options (heuristics for NP-Complete problems)
  - Algorithms will be improved and optimized for better performance and scalability.
  - Documentation will be extended, including more examples and detailed explanations.
