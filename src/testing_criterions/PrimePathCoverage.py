from testing_criterions.SimpleCycleCoverage import SimpleCycleCoverage
from testing_criterions.SimplePathsCoverage import SimplePathsCoverage
from testing_criterions.decorators import (
    validate_source,
    validate_sink,
    validate_reachability,
    validate_diblob,
)


class PrimePathCoverage:
    @validate_reachability()
    @validate_source()
    @validate_sink()
    @validate_diblob()
    def __init__(self, digraph_manager) -> None:
        self.digraph_manager = digraph_manager

    def get_test_cases(self, max_number_of_cycles_in_single_test_case):
        scc = SimpleCycleCoverage(self.digraph_manager)
        spc = SimplePathsCoverage(self.digraph_manager)

        for test_case in scc.get_test_cases(
            max_number_of_cycles_in_single_test_case, double_cycle=True
        ):
            yield test_case
        for test_case in spc.get_test_cases(max_number_of_cycles_in_single_test_case):
            yield test_case
