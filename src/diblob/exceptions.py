"""
Exceptions raised in specific parts of diblob package.
"""

class CollisionException(Exception):
    """
    Raised when and we try add occupied id of Edge/Node/Blob to digraph_manager.
    """

class DiblobKeyAlreadyExistsException(Exception):
    """
    Raised when we try gather nodes to new diblob, but delivered diblob id already exists.
    """

class DiblobGatherException(Exception):
    """
    Raised when we try gather nodes with different parent_id.
    """

class InvalidDiblobId(Exception):
    """
    Raised when we try flat something not registered in digraph_manager diblobs.
    """

class RemoveRootDiblobException(Exception):
    """
    Raised when we try flat root diblob.
    """

class RootDiblobException(Exception):
    """
    Raised when operation is forbidden for root diblob, or operations are 
    available just for diblobs with only one root (root_diblob)
    """

class EdgeAdditionException(Exception):
    """
    Raised when we try add incompatible edges.
    """

class InvalidPathException(Exception):
    """
    Raised when path in Edge __init__ is too short.
    """

class InvalidDigraphDictException(Exception):
    """
    Raised when dict delivered during digraph_manager exception is invalid.
    """

class EmptyBlobException(Exception):
    """
    Raised when we try create empty diblob.
    """
class InvalidConstructionJSON(Exception):
    """
    Raised when delivered json for digraphs creation is invalid.
    """

class MultipleEdgeException(Exception):
    """
    Raised when algorithm try perform operation reserved only for digraphs (not pseudographs).
    """

class CommonResourcesInjection(Exception):
    """
    Raised when we use inject method with the same ids for both of digraphs.
    """

class IllegalJoinException(Exception):
    """
    Raised when we try join blobs with different parent_ids.
    """

class InvalidAdditionException(Exception):
    """
    Raised when we try add two digraphs with more than one diblob (with root_id).
    """

class RandomCycleException(Exception):
    """
    Raised when we try create cycle with node space < size of cycle in the generator.
    """

class RandomDAGException(Exception):
    """
    Raised when we try create random DAG with too many edges.
    """

class InvalidGeneratorParameterException(Exception):
    """
    Raised when we try create random digraph using impossible parameters.
    """

class RenamingException(Exception):
    """
    Raised when an component id try to be changed into occupied id.
    """
