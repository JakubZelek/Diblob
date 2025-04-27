import random
import copy
from itertools import combinations


class Criterion:

    @staticmethod
    def avg_distance(test_case_manager_1, test_case_manager_2, cost_function, avg):

        cost_1 = 0
        for test_case in test_case_manager_1.test_case_dict.values():

            test_case_edge = test_case_manager_1.compute_edge_representation(test_case)
            cost_1 += abs(avg - sum(cost_function[value] for value in test_case_edge))

        cost_2 = 0
        for test_case in test_case_manager_2.test_case_dict.values():
            test_case_edge = test_case_manager_1.compute_edge_representation(test_case)
            cost_2 += abs(avg - sum(cost_function[value] for value in test_case_edge))

        print("COST_1", cost_1, "COST_2", cost_2)

        return cost_1 > cost_2


class MutationMethod:
    @staticmethod
    def common_node_mutation(test_case1, test_case2):
        mutations = []
        for idx1, node_id1 in enumerate(test_case1[1:-1]):
            for idx2, node_id2 in enumerate(test_case2[1:-1]):
                if node_id1 == node_id2 and test_case1[idx1] != test_case2[idx2]:
                    mutations.append((node_id1, idx1 + 1, idx2 + 2))

        return mutations

    @staticmethod
    def get_mutated_test_cases(test_case1, test_case2, mutation):
        _, idx_1, idx_2 = mutation
        new_test_case_1 = test_case1[:idx_1] + test_case2[idx_2 - 1 :]
        new_test_case_2 = test_case2[:idx_2] + test_case1[idx_1 + 1 :]
        return new_test_case_1, new_test_case_2


class TestCases:
    def __init__(self, test_cases) -> None:
        self.test_case_dict = {
            hash(tuple(test_case)): test_case for test_case in test_cases
        }

    @staticmethod
    def compute_edge_representation(test_case):
        return [
            (test_case[idx], test_case[idx + 1]) for idx in range(len(test_case) - 1)
        ]

    def rm_test_cases(self, *hash_ids):
        for hash_id in hash_ids:
            self.test_case_dict.pop(hash_id)

    def add_test_cases(self, *test_cases):
        for test_case in test_cases:
            self.test_case_dict[hash(tuple(test_case))] = test_case


class Mutation:
    def __init__(self, test_cases, mutation_method) -> None:
        self.test_case_manager = TestCases(test_cases)
        self.mutation_method = getattr(MutationMethod, mutation_method)
        self.hash_dict = self.__create_hash_dict(self.mutation_method)

    def __create_hash_dict(self, mutation_method):
        test_case_dict = self.test_case_manager.test_case_dict
        test_case_mutation_space = list(test_case_dict)
        hash_dict = {}

        for comb in combinations(test_case_mutation_space, 2):
            mutations = mutation_method(
                test_case_dict[comb[0]], test_case_dict[comb[1]]
            )
            if mutations:
                hash_dict[comb] = mutations

        return hash_dict

    def add_mutation(self, test_case1, test_case2):
        possible_mutations = self.mutation_method(test_case1, test_case2)
        if possible_mutations:
            self.hash_dict[(hash(tuple(test_case1)), hash(tuple(test_case2)))] = (
                possible_mutations
            )
            self.test_case_manager.add_test_cases(test_case1, test_case2)

    def rm_mutation(self, hash_id):
        for key in list(self.hash_dict):
            if hash_id in key:
                self.hash_dict.pop(key)
        self.test_case_manager.rm_test_cases(hash_id)


def mutation_algorithm(
    test_cases,
    cost_function,
    iterations=10,
    number_of_mutations=3,
    mutation_method="common_node_mutation",
    avg=0,
):
    mutation_set = set()
    mutation_manager = Mutation(test_cases, mutation_method)

    for _ in range(iterations):
        potential_new_mutation_manager = copy.deepcopy(mutation_manager)
        test_cases_dict = (
            potential_new_mutation_manager.test_case_manager.test_case_dict
        )

        for _ in range(number_of_mutations):
            key = random.choice(list(potential_new_mutation_manager.hash_dict))
            value = random.choice(list(potential_new_mutation_manager.hash_dict[key]))

            test_1_hash, test_2_hash = key
            test_case_1, test_case_2 = (
                test_cases_dict[test_1_hash],
                test_cases_dict[test_2_hash],
            )
            mut_test_case_1, mut_test_case_2 = MutationMethod.get_mutated_test_cases(
                test_case_1, test_case_2, value
            )

            mutation_hash = (hash(tuple(mut_test_case_1)), hash(tuple(mut_test_case_2)))
            mutation_set.add(mutation_hash)
            # print("MUTATION LENGTH", len(mutation_set))
            potential_new_mutation_manager.test_case_manager.rm_test_cases(test_1_hash)
            potential_new_mutation_manager.test_case_manager.rm_test_cases(test_2_hash)

            potential_new_mutation_manager.test_case_manager.add_test_cases(
                mut_test_case_1, mut_test_case_2
            )
            test_cases = [
                test_case
                for test_case in potential_new_mutation_manager.test_case_manager.test_case_dict.values()
            ]
            potential_new_mutation_manager = Mutation(test_cases, mutation_method)
            test_cases_dict = (
                potential_new_mutation_manager.test_case_manager.test_case_dict
            )

        if Criterion.avg_distance(
            mutation_manager.test_case_manager,
            potential_new_mutation_manager.test_case_manager,
            cost_function,
            avg=avg,
        ):
            mutation_manager = potential_new_mutation_manager
    return mutation_manager


def generate_artificial_test_cases(test_length=5, number_of_tests=4):
    test_cases = []
    cost_function = {}
    for idx_1 in range(number_of_tests):
        test_case = [
            str(idx_2) if idx_2 % 2 == 0 else f"{idx_1}_{idx_2}"
            for idx_2 in range(test_length)
        ]

        edge_repr = TestCases.compute_edge_representation(test_case)
        for elem in edge_repr:
            cost_function[elem] = idx_1 + 1

        test_cases.append(test_case)
    avg = sum(value for value in cost_function.values()) / number_of_tests
    return test_cases, cost_function, avg
