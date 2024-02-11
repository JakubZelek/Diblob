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
    Raised when operation is forbidden for root diblob.
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
