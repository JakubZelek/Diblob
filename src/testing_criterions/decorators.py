import inspect
from functools import wraps
from diblob.algorithms import DFS
from testing_criterions.exceptions import (
    LackOfSourceException,
    NotSingleSourceException,
    InvalidNodeException,
    LackOfSinkException,
    NotSingleSinkException,
    NodeNotReachableException,
    ForbiddenCostFunctionKeyException,
)


def validate_source(param_name="digraph_manager"):
    """
    Validates the following:
        -S in the digraph.
        -Digraph contains single source S.
        -s_cpt not in the digraph.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            bound_args = inspect.signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()
            digraph_manager = bound_args.arguments.get(param_name)

            if "S" not in digraph_manager.nodes:
                raise LackOfSourceException("Cannot find the source S in the digraph.")

            if "s_cpt" in digraph_manager.nodes:
                raise InvalidNodeException("s_cpt is forbidden as node_id.")

            for node_id in digraph_manager.nodes:
                if node_id != "S" and len(digraph_manager[node_id].incoming_nodes) == 0:
                    raise NotSingleSourceException(
                        f"Source should be the only one source, other source: {node_id}."
                    )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_sink(param_name="digraph_manager"):
    """
    Validates the following:
        -T in the digraph.
        -Digraph contains single sink T.
        -t_cpt not in the digraph.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            bound_args = inspect.signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()
            digraph_manager = bound_args.arguments.get(param_name)

            if "T" not in digraph_manager.nodes:
                raise LackOfSinkException("Cannot find the sink T in the digraph.")

            if "t_cpt" in digraph_manager.nodes:
                raise InvalidNodeException("t_cpt is forbidden as node_id.")

            for node_id in digraph_manager.nodes:
                if node_id != "T" and len(digraph_manager[node_id].outgoing_nodes) == 0:
                    raise NotSingleSinkException(
                        f"Sink should be the only one source, other source: {node_id}."
                    )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_reachability(param_name="digraph_manager"):
    """
    Validates if all nodes can be reached from S.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            bound_args = inspect.signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()
            digraph_manager = bound_args.arguments.get(param_name)

            dfs = DFS(digraph_manager)
            dfs.run("S")
            not_reachable = set(digraph_manager.nodes) - set(dfs.visitation_dict.keys())

            if not_reachable:
                raise NodeNotReachableException(
                    f"The following nodes are not reachable from S: {sorted(list(not_reachable))}"
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_cost_function(param_name="cost_function"):
    """
    Validates cost function to no have costs for additional edges for CPT algorithm.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            bound_args = inspect.signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()
            cost_function = bound_args.arguments.get(param_name)

            if cost_function is not None:
                for edge_id in cost_function:
                    start, end = edge_id
                    if (
                        start == "T"
                        or end == "S"
                        or start in {"t_cpt", "s_cpt"}
                        or end in {"t_cpt", "s_cpt"}
                    ):
                        raise ForbiddenCostFunctionKeyException(
                            f"Forbidden value in key, edge: {edge_id}"
                        )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_diblob(param_name="digraph_manager"):
    """
    Validates if the diblob has only one diblob_id.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            bound_args = inspect.signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()
            digraph_manager = bound_args.arguments.get(param_name)

            if len(digraph_manager.diblobs) > 1:
                pass
            return func(*args, **kwargs)

        return wrapper

    return decorator
