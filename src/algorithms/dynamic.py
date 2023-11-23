def best_route(coordinates): #assumes that the starting point is the origin, however can easily be adjusted
    route_to_cost = {}
    """ keys in route_to_cost are bitstrings (code to be updated to use actual bitstrings, right now I am having an issue with using the library for it) of length 
    len(coordinates) entries. Say there are 10 places, then the bitstring 1000100011 is a key to represent routes that go through the first, fifth, ninth and 
    tenth places. Each value is a dict whose keys are ending place and value is a list representing the route. For example, the value corresponding to the key
    above is itself a dictionary, which will have keys 0, 4, 8, 9 (because of zero indexing) and the corresponding value will be the shortest route going through
    places 0, 4, 8, 9 ending with the key (if they key is 0, the shortest route going through those places ending in place 0.)"""
    for i in range(0, len(coordinates)): #this loop  initializes the dictionary for all sub-routes of length 1.
        to_add = '0' * len(coordinates)
        to_add =  to_add[0:i] + '1' + to_add[i+1:]
        route_to_cost[to_add] = {i : [i]} 
    
    adjacency_matrix = [[0] * len(coordinates)]
    for _ in range(len(coordinates) - 1):
        adjacency_matrix.append([0] * len(coordinates))
    for i in range(len(coordinates)):
        for j in range(len(coordinates)):
            adjacency_matrix[i][j] = squared_distance(coordinates[i], coordinates[j])
    distances = [0] * len(coordinates)
    for i in range(len(coordinates)):
        distances[i] = squared_distance([0, 0], coordinates[i])
    
    #now the major dynammic programming step
    for i in range(1, len(coordinates)): #loop through all sub-routes of length i
        new_route_to_cost = {}
        for key in route_to_cost:
            for j in range(0, len(coordinates)):
                if key[j] == '0': #now how have bit in the key that is a 0. First of all, make it a 1. If you went 
                #through every entry in route_to_cost[key], and appended this new place onto the back, you would get the best route passing
                #through all other places and j that end at place j. 
                    new_bit_string = key[0:j] + '1' + key[j + 1:]
                    best_cost = None
                    if new_bit_string not in new_route_to_cost:
                        new_route_to_cost[new_bit_string] = {}

                    for entry in route_to_cost[key]:
                        cost = cost_function(route_to_cost[key][entry] + [j], coordinates, adjacency_matrix, distances)
                        if best_cost == None or cost < best_cost:
                            best_cost = cost
                            new_route_to_cost[new_bit_string][j] = route_to_cost[key][entry] + [j] 

        route_to_cost = new_route_to_cost
    final_best_cost = None
    final_route = []
    key = '1' * len(coordinates)
    for entry in route_to_cost[key]: #final loop, since at this point route_to_cost stores all optimal subroutes ending with each different place, we just need 
      #to see which is the best place to end up at
        cost = cost_function(route_to_cost[key][entry], coordinates, adjacency_matrix, distances)
        if final_best_cost == None or cost < final_best_cost:
            final_best_cost = cost
            final_route = route_to_cost[key][entry]
    return select_coords(coordinates, final_route)



def select_coords(coords, indices): #helper to make convert a route of the for [i1, i2, i3, ...] (i's are indexes) into actual coordinates
    to_return = []
    for index in indices:
        to_return.append(coords[index])
    return to_return

def squared_distance(coord1, coord2):
    global count
    count += 1
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
