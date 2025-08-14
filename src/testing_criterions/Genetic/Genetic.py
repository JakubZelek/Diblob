def create_digraph_json_from_test_case_list(test_case_list):
    digraph_dict = {}

    for test_case in test_case_list:
        prev_node_id = None

        for node_id in test_case:
            if prev_node_id:
                neigh_list = digraph_dict.setdefault(prev_node_id, [])
                if node_id not in neigh_list:
                    neigh_list.append(node_id)
            prev_node_id = node_id
        digraph_dict.setdefault(prev_node_id, [])

    return {"B0": digraph_dict}


class TestCaseHead:
    def __init__(self) -> None:
        self.next = None
        self.cost = 0

    def set_cost(self, cost):
        self.cost = cost

    def get_cost(self):
        return self.cost


class TestCaseNode:
    def __init__(self, value) -> None:
        self.next = None
        self.prev = None
        self.cost = 0
        self.value = value

    def set_cost(self, cost):
        self.cost = cost


class Mutation:
    def __init__(self, test_cases, cost_function) -> None:
        self.test_cases = test_cases
        self.mutation_dict = {}
        self.test_case_list = []
        self.cost_function = cost_function

    def create_mutation_resources(self):
        for test_case in self.test_cases:
            head = TestCaseHead()
            self.test_case_list.append(head)
            prev = head
            prev_id = None
            test_case_cost = 0
            cost_function = self.cost_function
            for node_id in test_case:

                test_case_node = TestCaseNode(node_id)
                test_case_node.prev = prev
                prev.next = test_case_node
                self.mutation_dict.setdefault(node_id, []).append(test_case_node)
                if prev_id is not None:

                    node_cost = cost_function[(prev_id, node_id)]
                    test_case_node.set_cost(node_cost)
                    test_case_cost += node_cost
                prev_id = node_id
                prev = test_case_node

            head.set_cost(test_case_cost)

    def calculate_cost(self, prev, current):
        return cost_function[(prev, current)]

    def compare_cost(self, test_case_node_1, test_case_node_2, avg=0):
        prev = test_case_node_1.prev
        test_case_node_1_prev_cost = test_case_node_1.cost

        while isinstance(prev, TestCaseNode):
            test_case_node_1_prev_cost += prev.cost
            prev = prev.prev
        cost_1 = prev.cost
        head_1 = prev
        prev = test_case_node_2.prev
        test_case_node_2_prev_cost = test_case_node_2.cost
        while isinstance(prev, TestCaseNode):
            test_case_node_2_prev_cost += prev.cost
            prev = prev.prev

        cost_2 = prev.cost
        head_2 = prev

        next_1_cost = cost_1 - test_case_node_1_prev_cost
        next_2_cost = cost_2 - test_case_node_2_prev_cost

        potential_cost_1 = test_case_node_1_prev_cost + next_2_cost
        potential_cost_2 = test_case_node_2_prev_cost + next_1_cost

        avg_difference_1 = abs(avg - cost_1) + abs(avg - cost_2)
        avg_difference_2 = abs(avg - potential_cost_1) + abs(avg - potential_cost_2)

        if avg_difference_1 > avg_difference_2:
            head_1.set_cost(potential_cost_1)
            head_2.set_cost(potential_cost_2)
            test_1_next = test_case_node_1.next
            test_2_next = test_case_node_2.next

            test_1_next.cost, test_2_next.cost = test_2_next.cost, test_1_next.cost
            test_1_next.prev = test_case_node_2
            test_2_next.prev = test_case_node_1
            test_case_node_1.next = test_2_next
            test_case_node_2.next = test_1_next

        return avg_difference_1, avg_difference_2


import random


def run_algorithm(
    test_cases, cost_function, iterations=1000000, threshold=0, avg=None, pop=None
):

    m = Mutation(test_cases, cost_function)
    m.create_mutation_resources()
    dist = 0

    cost = 0
    for test_case in m.test_case_list:
        cost += test_case.cost

    print("COST", cost)
    print("AVG", avg)
    print("COMPUTETD AVG", cost / len(m.test_case_list))
    print(m.test_case_list[1].cost)

    if avg is None:
        avg = cost / len(m.test_case_list)

    for test_case in m.test_case_list:
        dist += abs(avg - test_case.cost)

    iterator = 0
    if pop is not None:
        for i in pop:
            m.mutation_dict.pop(i)
    m.mutation_dict = {
        key: value for key, value in m.mutation_dict.items() if len(value) > 1
    }

    dist_values = []
    iter_values = []
    while iterator < iterations and dist > threshold:

        iterator += 1
        mutate = random.choice(list(m.mutation_dict.keys()))
        x, y = random.sample(m.mutation_dict[mutate], 2)

        old_cost, new_cost = m.compare_cost(x, y, avg=avg)

        if new_cost < old_cost:
            dist = dist - old_cost + new_cost

        print("iteration ", iterator, "cost", dist)
        if iterator % 100 == 0:
            dist_values.append(dist)
            iter_values.append(iterator)
    return m.test_case_list, dist_values, iter_values
