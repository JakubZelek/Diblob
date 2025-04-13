from diblob import DigraphManager
from testing_criterions.SimpleCycleCoverage import SimpleCycleCoverage
from testing_criterions.SimplePathsCoverage import SimplePathCoverage


class PrimePathCoverage:
    def __init__(self, digraph_manager) -> None:
        self.digraph_manager = digraph_manager

    def get_test_cases(self, max_number_of_cycles_in_single_test_case):
        scc = SimpleCycleCoverage(self.digraph_manager)
        spc = SimplePathCoverage(self.digraph_manager)
        for test_case in scc.get_test_cases(max_number_of_cycles_in_single_test_case, 
                                            double_cycle=True):
            yield test_case

        for test_case in spc.get_test_cases(max_number_of_cycles_in_single_test_case):
            yield test_case


from diblob.digraph_manager import DigraphManager
digraph_manager = DigraphManager({'B0':{}})
digraph_manager.add_nodes('S', '1', '2', '3', '4', '5', 'T')
digraph_manager.connect_nodes(('S', '1'), ('1', '2'), ('2', 'T'), ('1', '3'), ('3', '4'), ('4', '5'), ('5', '4'), ('4', '1'))

 
scc = PrimePathCoverage(digraph_manager)
for x in scc.get_test_cases(5):
    print(x)
