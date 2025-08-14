class InvalidSinkSourceException(Exception):
    """Raised if sink or source is present in the digraph manager. Used in TestCasesGenerator"""


class LackOfEdgeElementException(Exception):
    """Raised if there is no edge element in the CPTDigraph"""


class LackOfSinkException(Exception):
    """Raised when the sink T is not present in the DigraphManager"""


class LackOfSourceException(Exception):
    """Raised when the source S is not present in the DigraphManager"""


class NotSingleSourceException(Exception):
    """Raised when the S is not the single source"""


class NotSingleSinkException(Exception):
    """Raised when the T is not the single sink"""


class InvalidNodeException(Exception):
    """Raised when the forbidden node_id is present in the digraph"""


class NodeNotReachableException(Exception):
    """Raised when the vertex is not reachable from S"""


class ForbiddenCostFunctionKeyException(Exception):
    """Raised, when forbidden key is used in cost function"""


class InvalidNSwitchException(Exception):
    """Raised when invalid value for NSwitch is delivered."""


class InvalidNPathException(Exception):
    """Raised when invalid value for NPath is delivered."""


class MultipleDiblobException(Exception):
    """Raised when operation enable to use jus one Diblob in the method (not subdiblob)."""
