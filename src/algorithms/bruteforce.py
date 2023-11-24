#coordinates is a list of the coordinates of all the places to be visited. will soon be updated to mean the
#latitude and longitude of the places. 
def best_route(coordinates): #table containing distances between places
    routes = permute(coordinates)
    best = routes[0]
    best_cost = squared_distance(best[0], [0, 0])
    for i in range(1, len(best)):
            best_cost += squared_distance(best[i], best[i - 1])
    for route in routes:
        cost = squared_distance([0, 0], route[0])
        for i in range(1, len(route)):
            cost += squared_distance(route[i], route[i - 1])
        if cost < best_cost:
            best_cost = cost
            best = route
    return best

def permute(coordinates): #generates every possible route one could take through all places
    to_return = [[coordinates[0]]]
    for i in range(1, len(coordinates)):
        new_to_return = []
        for j in range (len(to_return)):
            current_list = to_return[j]
            for k in range(len(current_list) + 1):
                new_to_return.append(current_list[0:k] + [coordinates[i]] + current_list[k:])
        to_return = new_to_return
    return to_return
    
def squared_distance(coord1, coord2):
    return (coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2

def select_coords(coords, indices):
    to_return = []
    for index in indices:
        to_return.append(coords[index])
    return to_return

def costof(coordinates):
    cost = squared_distance([0, 0], coordinates[0])
    for i in range(1, len(coordinates)):
        cost += squared_distance(coordinates[i], coordinates[i - 1])
    return cost
