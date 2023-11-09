def best_route(coordinates):
    to_return = [coordinates[0]]
    print(to_return)
    added = [False] * len(coordinates) #list that checks whether a place has been added to route or not
    added[0] = True
    print(added)
    for i in range(len(coordinates) - 1):
        curr = to_return[-1]
        least_dist = 0
        closest_ind = 0
        for j in range(len(coordinates)): #loop to find any place that hasn't been added yet and set its distance to the min distance temporarily
            if squared_distance(curr, coordinates[j]) != 0 and added[j] == False:
                least_dist = squared_distance(curr, coordinates[j])
                closest_ind = j
                break
        print(least_dist)
        print(closest_ind)
        for j in range(len(coordinates)): #finds the nearest neighbor
            if (added[j] != True and coordinates[j] != curr and squared_distance(curr, coordinates[j]) < least_dist):
                least_dist = squared_distance(curr, coordinates[j])
                closest_ind = j
        to_return.append(coordinates[closest_ind])
        added[closest_ind] = True
    return to_return

def squared_distance(coord1, coord2): #the same squared distance function as for the other algorithms
    return (coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2
