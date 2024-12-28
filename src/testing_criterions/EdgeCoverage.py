from diblob import DigraphManager
from CPTTestCasesGenerator import TestCasesGenerator

class EdgeCoverage:
    def __init__(self, digraph_manager) -> None:
        self.digraph_manager = digraph_manager

    def get_test_cases(self):
        tcs = TestCasesGenerator(self.digraph_manager,
                                 source='s_cpt',
                                 sink='t_cpt')
        test_cases = tcs.generate_test_cases(1)
        return test_cases


digraph_manager = DigraphManager({"B0": {}})
digraph_manager.add_nodes('S', 'T', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10')
digraph_manager.connect_nodes(('S', '1'), ('1', '2'), ('1', '3'), ('1', '4'), ('2', '5'), ('3', '5'), ('4', '5'),
                              ('5', '6'), ('6', '7'), ('7', '5'), ('6', '8'), ('8', '9'), ('9', '6'), ('9', '7'), ('7', '10'),
                              ('10', '9'), ('8', 'T'), ('9', 'T'), ('10', 'T'))

node_coverage = EdgeCoverage(digraph_manager)
test_cases = node_coverage.get_test_cases()
print(test_cases)
