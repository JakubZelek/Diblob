from diblob import DigraphManager
from diblob.factory import DiblobFactory
from CPTTestCasesGenerator import TestCasesGenerator


class NSwitchCoverage:
    def __init__(self, digraph_manager, n_switch) -> None:
        for reduce in range(n_switch - 1):
            digraph_manager = DiblobFactory.generate_edge_digraph(digraph_manager, reduce_value=reduce)
        self.digraph_manager = digraph_manager

    def get_test_cases(self):
        tcs = TestCasesGenerator(self.digraph_manager,
                                 source='s_cpt',
                                 sink='t_cpt')
        test_cases = tcs.generate_test_cases(1)


        return [test_case[0].split('|') + [t.split('|')[-1] 
                for t in test_case[1:]] for test_case in test_cases]



digraph_manager = DigraphManager({"B0": {}})
digraph_manager.add_nodes('S', 'T', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10')
digraph_manager.connect_nodes(('S', '1'), ('1', '2'), ('1', '3'), ('1', '4'), ('2', '5'), ('3', '5'), ('4', '5'),
                              ('5', '6'), ('6', '7'), ('7', '5'), ('6', '8'), ('8', '9'), ('9', '6'), ('9', '7'), ('7', '10'),
                              ('10', '9'), ('8', 'T'), ('9', 'T'), ('10', 'T'))

node_coverage = NSwitchCoverage(digraph_manager, n_switch=2)
test_cases = node_coverage.get_test_cases()
print(test_cases)