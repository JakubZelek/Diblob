from testing_criterions.SimplePathsCoverage import SimplePathsCoverage
from diblob.factory import DiblobFactory
from testing_criterions.exceptions import InvalidNPathException
from testing_criterions.decorators import (
    validate_source,
    validate_sink,
    validate_reachability,
    validate_diblob,
)


class NPathCoverage:
    @validate_reachability()
    @validate_source()
    @validate_sink()
    @validate_diblob()
    def __init__(self, digraph_manager, n_paths) -> None:
        if n_paths < 2:
            raise InvalidNPathException(
                "n_path argument should be at least equals to 2."
            )

        for reduce in range(n_paths - 1):
            digraph_manager = DiblobFactory.generate_edge_digraph(
                digraph_manager, reduce_value=reduce
            )
        self.digraph_manager = digraph_manager
        self.digraph_manager.add_nodes("S", "T")

        for node_id in self.digraph_manager.nodes:

            if node_id[:2] == "S|":
                self.digraph_manager.connect_nodes(("S", node_id))
            if node_id[-2:] == "|T":
                self.digraph_manager.connect_nodes((node_id, "T"))

    def get_test_cases(self, max_number_of_cycles_in_single_test_case):
        spc = SimplePathsCoverage(self.digraph_manager)

        for test_case in spc.get_test_cases(max_number_of_cycles_in_single_test_case):
            yield test_case[1].split("|") + [t.split("|")[-1] for t in test_case[2:-1]]
