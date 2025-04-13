from diblob import DigraphManager
from testing_criterions.SimplePathsCoverage import SimplePathCoverage
from diblob.factory import DiblobFactory


class NPathCoverage:
    def __init__(self, digraph_manager, n_paths) -> None:

        for reduce in range(n_paths - 1):
            digraph_manager = DiblobFactory.generate_edge_digraph(digraph_manager, reduce_value=reduce)
        self.digraph_manager = digraph_manager
        self.digraph_manager.add_nodes('S', 'T')

        for node_id in self.digraph_manager.nodes:
            if node_id[:2] == 'S|':
                self.digraph_manager.connect_nodes(('S', node_id))
            if node_id[-2:] == '|T':
                self.digraph_manager.connect_nodes((node_id, 'T'))

    def get_test_cases(self, max_number_of_cycles_in_single_test_case):
        spc = SimplePathCoverage(self.digraph_manager)

        for test_case in spc.get_test_cases(max_number_of_cycles_in_single_test_case):
            yield test_case[1].split('|') + [t.split('|')[-1] for t in test_case[2:-1]]
            # test_case = test_case[0].split('|') + [t.split('|')[-1] 
            #     for t in test_case[1:]]



from diblob.digraph_manager import DigraphManager
digraph_manager = DigraphManager({'B0':{}})
digraph_manager.add_nodes('S', '1', '2', '3', '4', '5', 'T')
digraph_manager.connect_nodes(('S', '1'), ('1', '2'), ('2', 'T'), ('1', '3'), ('3', '4'), ('4', '5'), ('5', '4'), ('4', '1'))

 
scc = NPathCoverage(digraph_manager, n_paths=3)
for x in scc.get_test_cases(3):
    print(x)

