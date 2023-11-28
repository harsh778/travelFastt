import random
import numpy as np
import time
import math
import copy
#implementation for the genetic algorithm - only really useful for more than 15 places or so

sum_36 = 0.0
for i in range(1, 100):
    sum_36 += 1.0/i
def best_route(coordinates):
    coordinates = random.sample(coordinates, len(coordinates))
    adjacency_matrix, distances = generate_adj_and_dist(coordinates)
    solutions, costs = generate_init_sols(100, coordinates) #generate some number of initial_solutions
    """Now, we want our genetic algorithm to work as follows: we generate 36 new solutions by crossing over, 10 solutions by mutating
    current solutions, and 4 completely random solution. The fittest 50 of these solutions are moved into the next generation"""
    converged = False
    for a in range (1000):
        num1 = math.floor(a / 1000 * 100)
        num2 = math.floor((100 - num1) / 2)
        num3 = 100 - num1 - num2
        new_solutions = []
        new_costs = []
        for i in range(num1):
            index1 = -1
            while (index1 < 0 or index1 > 99):
                a = random.uniform(0, 0.2)
                index1 = math.floor(1/(a * sum_36) - 5)
            index2 = -1
            while (index2 < 0 or index2 > 99):
                a = random.uniform(0, 0.2)
                index2 = math.floor(1/(a * sum_36) - 10)
            if index1 == index2:
                index2 += random.randint(1, 3)
            if index2 >= len(solutions):
                index2 = len(solutions) - 1
            new_sol = ordinary_crossover(solutions[index1], solutions[index2])
            new_solutions.append(new_sol)
            new_cost = cost_function(new_sol, coordinates, adjacency_matrix, distances)
            new_costs.append(new_cost)
        for i in range(num2):
            index = -1
            while (index < 0 or index > 99):
                a = random.uniform(0, 0.2)
                index = math.floor(1/(a * sum_36) - 10)
            new_sol = mutate(solutions[index])
            new_solutions.append(new_sol)
            new_cost = cost_function(new_sol, coordinates, adjacency_matrix, distances)
            new_costs.append(new_cost)
        solutions_to_add, costs_to_add = generate_init_sols(num3,coordinates)
        new_solutions = new_solutions + solutions_to_add
        new_costs = new_costs + costs_to_add
        curr_argsort = np.argsort(costs)
        new_argsort = np.argsort(new_costs)
        next_gen_sols = []
        next_gen_costs = []
        i = 0
        j = 0
        for _ in range(100):
            if costs[curr_argsort[i]] < costs[new_argsort[j]]:
                next_gen_sols.append(solutions[curr_argsort[i]])
                next_gen_costs.append(costs[curr_argsort[i]])
                i += 1
            elif costs[curr_argsort[i]] >= costs[new_argsort[j]]:
                next_gen_sols.append(new_solutions[new_argsort[j]])
                next_gen_costs.append(new_costs[new_argsort[j]])
                j += 1
        solutions, costs = next_gen_sols, next_gen_costs
    return solutions[0], costs[0], solutions[99], costs[99]
            
            
    
def ordinary_crossover(sol1, sol2):
    num = random.randint(0, math.floor(len(sol1) / 2))
    end_elements = set()
    for i in range(len(sol1) - 1 - num, len(sol1)):
        end_elements.add(sol1[i])
    child = []
    end_list = []
    for place in sol2:
        if place not in end_elements:
            child.append(place)
        else:
            end_list.append(place)
    end_list = random.sample(end_list, len(end_list))
    child = child + end_list
    return child
        
def mutate(solution):
    sol = copy.deepcopy(solution)
    a = random.randint(0, 2)
    max_length = int(len(sol) / 3)
    ind = random.randint(0, len(sol) - 1 - max_length)
    mutation_length = random.randint(2, max_length)
    mutated = sol[ind: ind + mutation_length]
    if a == 0:
        mutated = random.sample(mutated, len(mutated))
        sol[ind: ind + mutation_length] = mutated
    else:
        sol[ind: ind + mutation_length] = []
        insert_ind = random.randint(0, len(sol))
        sol = sol[:insert_ind] + mutated + sol[insert_ind:]
    return sol
        
def generate_adj_and_dist(coordinates):
    adjacency_matrix = [[0] * len(coordinates)]
    for _ in range(len(coordinates) - 1):
        adjacency_matrix.append([0] * len(coordinates))
    for i in range(len(coordinates)):
        for j in range(len(coordinates)):
            adjacency_matrix[i][j] = squared_distance(coordinates[i], coordinates[j])
    distances = [0] * len(coordinates)
    for i in range(len(coordinates)):
        distances[i] = squared_distance([0, 0], coordinates[i])
    return adjacency_matrix, distances    
        
def generate_init_sols(num, coordinates):
    costs = []
    solutions = []
    solution = []
    for i in range(len(coordinates)):
        solution.append(i)
    for _ in range(num):
        solution = random.sample(solution, len(solution))
        solutions.append(solution)
        adjacency_matrix, distances = generate_adj_and_dist(coordinates)
        costs.append(cost_function(solution, coordinates, adjacency_matrix, distances))
    return solutions, costs

def squared_distance(coord1, coord2):
    return (coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2


def cost_function(route, coordinates, adjacency_matrix, distances): 
    cost = distances[route[0]]
    for i in range(1, len(route)):
        cost += adjacency_matrix[route[i]][route[i-1]]
    return cost
    

def costof(coordinates): #helper that is later useful for testing
    cost = squared_distance([0, 0], coordinates[0])
    for i in range(1, len(coordinates)):
        cost += squared_distance(coordinates[i], coordinates[i - 1])
    return cost
