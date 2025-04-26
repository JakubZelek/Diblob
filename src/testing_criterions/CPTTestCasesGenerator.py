from copy import deepcopy
from testing_criterions import CPTDigraphManager
from testing_criterions.exceptions import InvalidSinkSourceException, LackOfEdgeElementException


class TestCasesGenerator:
    """
    Generates test cases for criterions which can be served by CPT algorithm.
    """
    def __init__(self,
                 digraph_manager,
                 source='S',
                 sink='T',
                 cost_function=None,
                 default_cost=1) -> None:
    
        if cost_function is None:
            cost_function = {}
        
        if source in digraph_manager or sink in digraph_manager:
            raise InvalidSinkSourceException(
                'Sink and sources should be unique over digraph namespace!'
                )

        self.source = source
        self.sink = sink
        self.digraph_manager = digraph_manager

        dict_json_representation = dict(digraph_manager(digraph_manager.root_diblob_id))
        self.cpt = CPTDigraphManager(dict_json_representation, cost_function=
                                     {edge_id: cost_function.get(edge_id, default_cost)
                                      for edge_id in digraph_manager.edges})

        self.minimal_elements, self.maximal_elements = self.cpt.get_edge_elements()
        if not self.minimal_elements or not self.maximal_elements:
            raise LackOfEdgeElementException(
                'Should be at least one minimal/maximal element in the diblob!'
                )

    def __get_additional_nodes_and_edges(self, k):
        sink = self.sink
        source = self.source

        nodes_to_add = [sink + source + str(number) for number in range(k)] + [sink, source]

        minimal_edges = [(self.source, node_id) for node_id in self.minimal_elements]
        maximal_edges = [(node_id, self.sink) for node_id in self.maximal_elements]

        sink_source_edges = [(sink, sink + source + str(number)) for number in range(k)] +\
                            [(sink + source + str(number), source) for number in range(k)]

        return nodes_to_add, minimal_edges, maximal_edges, sink_source_edges


    def __get_cost(self, edge_list, cost):
        return {edge_id: cost for edge_id in edge_list}

    def __set_params(self, k, minimal_edges_cost=1, maximal_edges_cost=1, sink_source_cost=1):
        """"Case 1: Minimal total number of test cases."""
        cpt = deepcopy(self.cpt)
        nodes_to_add, minimal_edges, maximal_edges, sink_source_edges = self.__get_additional_nodes_and_edges(k)
        edges = minimal_edges + maximal_edges + sink_source_edges

        cpt.add_nodes(*nodes_to_add)
        cpt.connect_nodes(*edges)

        cpt.update_cost_function(self.__get_cost(minimal_edges, cost=minimal_edges_cost))
        cpt.update_cost_function(self.__get_cost(maximal_edges, cost=maximal_edges_cost))
        cpt.update_cost_function(self.__get_cost(sink_source_edges, cost=sink_source_cost))

        return cpt

    def __extract_test_cases(self, test_cases):
        test_case_list = []
        test_case = []
        skip_flag = False

        for elem in test_cases:
            if not skip_flag and elem[1] != self.sink:
                test_case.append(elem[1])
            if elem[1] == self.sink:
                test_case_list.append(test_case)
                test_case = []
                skip_flag = True
            if elem[1] == self.source:
                skip_flag = False

        return test_case_list


    def generate_test_cases(self, k, maximal_edges_cost = 1,
                             minimal_edges_cost = 1, sink_source_cost=1):
        """generates test cases based on delivered setting.

        Args:
            k (int): the number of test cases will be generated. Sometimes minimal
            number of test cases is less than delivered k. 
            Then the minimal number of test cases is computed.
            maximal_edges_cost (int, optional): cost of the edges with the form (_, sink).
            minimal_edges_cost (int, optional): cost of the edges with the form (source, _).
            sink_source_cost (int, optional): cost of the edges with the form (sink, _), (_, source).

        Returns:
            list(list): generated test cases.
        """
        cpt = self.__set_params(k, minimal_edges_cost, maximal_edges_cost, sink_source_cost)
        test_cases, _ = cpt.compute_cpt(start_node=self.source)
        return self.__extract_test_cases(test_cases)



# digraph_manager = DigraphManager({"B0": {}})
# digraph_manager.add_nodes('S', 'T', '0', '1', '2', '3', '4', '5', '6', '7')
# digraph_manager.connect_nodes(('S', '0'), ('0', '1'), ('1', '2'), ('1', '3'), ('3', '4'), ('1', '4'), ('2', '4'),
#                               ('4', '5'), ('4', '6'), ('5', '7'), ('6', '7'), ('7', '0'), ('7', 'T'))

# tg = TestCasesGenerator(digraph_manager=digraph_manager,
#                         source='source',
#                         sink='sink',
#                         default_cost=10,
#                         cost_function={('S', '0'): 1})

# a = tg.generate_test_cases(k=1,sink_source_cost=200)
# b = tg.generate_test_cases(k=5,sink_source_cost=200)


# a = """
# 1	Start
# 2	Start : OpenWeb[1]
# 3	OpenShop
# 4	OpenShop : LoginMembers[2]
# 5	Login
# 6	Login : BuyProducts[4]
# 7	AddToCard
# 8	AddToCard : PaymentProcess[5]
# 9	CheckOut
# 10	CheckOut : PaymentProcess[5]
# 11	Payment
# 12	Payment : PaymentSelection[6]
# 13	OnlineTransfer
# 14	OnlineTransfer : PaymentConfirm[6]
# 15	ValidatePayment
# 16	ValidatePayment : PaymentUnsucessful[4]
# 17	InvalidPayment
# 18	InvalidPayment : Return[1]
# 19	Order
# 20	Order : LoginToBuy[5]
# 21	Login
# 22	Login : OpenProductCatalog[3]
# 23	Catalog
# 24	Catalog : OpenProductList[3]
# 25	ViewProduct
# 26	ViewProduct : ViewProductDetails[3]
# 27	ProductDetails
# 28	ProductDetails : Return[1]
# 29	Catalog
# 30	Catalog : OpenProductList[3]
# 31	ViewProduct
# 32	ViewProduct : ViewProductDetails[3]
# 33	ProductDetails
# 34	ProductDetails : BuyProducts[4]
# 35	Order
# 36	Order : LoginToBuy[5]
# 37	Login
# 38	Login : BuyProducts[4]
# 39	AddToCard
# 40	AddToCard : PaymentProcess[5]
# 41	CheckOut
# 42	CheckOut : PaymentProcess[5]
# 43	Payment
# 44	Payment : PaymentSelection[6]
# 45	CreditCard
# 46	CreditCard : PaymentConfirm[6]
# 47	ValidatePayment
# 48	ValidatePayment : End[6]
# 49	End
# """

# b = """
# 1	Start
# 2	Start : OpenWeb[1]
# 3	OpenShop
# 4	OpenShop : OpenProductCatalog[2]
# 5	Catalog
# 6	Catalog : OpenProductList[3]
# 7	ViewProduct
# 8	ViewProduct : ViewProductDetails[3]
# 9	ProductDetails
# 10	ProductDetails : End[6]
# 11	End"""

# c = """
# 1	Start
# 2	Start : OpenWeb[1]
# 3	OpenShop
# 4	OpenShop : SearchProductDetails[2]
# 5	SearchProduct
# 6	SearchProduct : OpenProductDetails[3]
# 7	ProductDetails
# 8	ProductDetails : End[6]
# 9	End
# """


# def foo(x):
#     nodes = set()
#     edges = set()
#     start_edge = None
#     for idx, i in enumerate(x.split('\n')):
#         if idx%2 == 1:
#             try:
#                 nodes.add(i.split('\t')[1])
#                 if start_edge:
#                     edges.add((start_edge, i.split('\t')[1]))
#                 start_edge = i.split('\t')[1]
#             except:
#                 continue
#     return nodes, edges

# nodes = foo(a)[0] | foo(b)[0] | foo(c)[0]
# edges = foo(a)[1] | foo(b)[1] | foo(c)[1]

# print(len(nodes))
# print(len(edges))


# digraph_manager = DigraphManager({"B0": {}})
# digraph_manager.add_nodes(*nodes)
# digraph_manager.add_nodes('Blik', 'ShopCard')
# digraph_manager.connect_nodes(*edges)
# digraph_manager.connect_nodes(('Payment', 'Blik'), ('Blik', 'ValidatePayment'), ('Payment', 'ShopCard'), ('ShopCard', 'ValidatePayment'))


# COST_FUNCTION = {("Start", "OpenShop"): 1, ("Order", "Login"): 1, ('CheckOut', 'Payment'): 2, ('AddToCard', 'CheckOut'): 2}
# print(digraph_manager)
# tg = TestCasesGenerator(digraph_manager=digraph_manager,
#                         source='source',
#                         sink='sink',
#                         default_cost=5,
#                         cost_function=COST_FUNCTION)

# a = tg.generate_test_cases(k=4,sink_source_cost=1000)
# b = tg.generate_test_cases(k=5 ,sink_source_cost=1000)

# def compute_cost(test_case, cost_function, default_value=5):
#     cost = 0
#     start = test_case[0]

#     for node in test_case[1:]:
#         cost += cost_function.get((start, node), default_value)
#         start = node

#     return cost
    
# print([compute_cost(x, COST_FUNCTION) for x in a])
# print([compute_cost(x, COST_FUNCTION) for x in b])

# print(sum([compute_cost(x, COST_FUNCTION) for x in a]))
# print(sum([compute_cost(x, COST_FUNCTION) for x in b]))

# print(b)


# """

# Step	Results
# 1	Start
# 2	Start : 1
# 3	OpenShop
# 4	OpenShop : trans name
# 5	SearchProducst
# 6	SearchProducst : trans name
# 7	ProductDetails
# 8	ProductDetails : trans name
# 9	Catalog
# 10	Catalog : trans name
# 11	ViewProduct
# 12	ViewProduct : trans name
# 13	ProductDetails
# 14	ProductDetails : trans name
# 15	end

# 1	Start
# 2	Start : 1
# 3	OpenShop
# 4	OpenShop : trans name
# 5	Catalog
# 6	Catalog : trans name
# 7	ViewProduct
# 8	ViewProduct : trans name
# 9	ProductDetails
# 10	ProductDetails : trans name
# 11	Order
# 12	Order : 1
# 13	Login
# 14	Login : trans name
# 15	AddToCard
# 16	AddToCard : 2
# 17	CheckOut
# 18	CheckOut : 2
# 19	Payment
# 20	Payment : trans name
# 21	CreaditCard
# 22	CreaditCard : trans name
# 23	Validate Payment
# 24	Validate Payment : trans name
# 25	InvalidPayment
# 26	InvalidPayment : trans name
# 27	Order
# 28	Order : 1
# 29	Login
# 30	Login : trans name
# 31	AddToCard
# 32	AddToCard : 2
# 33	CheckOut
# 34	CheckOut : 2
# 35	Payment
# 36	Payment : trans name
# 37	Onlinetransfer
# 38	Onlinetransfer : trans name
# 39	Validate Payment
# 40	Validate Payment : trans name
# 41	InvalidPayment
# 42	InvalidPayment : trans name
# 43	Order
# 44	Order : 1
# 45	Login
# 46	Login : trans name
# 47	AddToCard
# 48	AddToCard : 2
# 49	CheckOut
# 50	CheckOut : 2
# 51	Payment
# 52	Payment : trans name
# 53	blik1
# 54	blik1 : trans name
# 55	Validate Payment
# 56	Validate Payment : trans name
# 57	InvalidPayment
# 58	InvalidPayment : trans name
# 59	Order
# 60	Order : 1
# 61	Login
# 62	Login : trans name
# 63	AddToCard
# 64	AddToCard : 2
# 65	CheckOut
# 66	CheckOut : 2
# 67	Payment
# 68	Payment : trans name
# 69	blik2
# 70	blik2 : trans name
# 71	Validate Payment
# 72	Validate Payment : trans name
# 73	end

# 1	Start
# 2	Start : 1
# 3	OpenShop
# 4	OpenShop : trans name
# 5	Login
# 6	Login : trans name
# 7	Catalog
# 8	Catalog : trans name
# 9	ViewProduct
# 10	ViewProduct : trans name
# 11	ProductDetails
# 12	ProductDetails : trans name
# 13	end
# """

# for elem in b:
#     x = str(elem).replace("'", "")[1:-1]
#     print(f'({x})')