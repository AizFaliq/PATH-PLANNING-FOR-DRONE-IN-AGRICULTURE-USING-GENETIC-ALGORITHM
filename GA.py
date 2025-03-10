# prepare data for GA
# need keys and coordinate
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import random
import matplotlib.pyplot as plt
import math
from shapely.geometry import LineString

# Parameters
POPULATION_SIZE = 100
MUTATION_RATE = 0.5
CROSSOVER_RATE = 0.7
GENERATIONS = 500
TOURNAMENT_SELECTION_SIZE = 3

# Euclidean distance formula
def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Function to calculate the total distance for a given route
def total_distance(route, locations):
    # print("Route", route)
    total = 0
    for i in range(len(route)):
        start = route[i]
        end = route[(i + 1) % len(route)]
        total += euclidean_distance(locations[start]['latitude'], locations[start]['longitude'],
                           locations[end]['latitude'], locations[end]['longitude'])
    return total

def has_overlapping_edges(route, locations):
    edges = [
        LineString([
            (locations[route[i]]['longitude'], locations[route[i]]['latitude']),
            (locations[route[(i + 1) % len(route)]]['longitude'], locations[route[(i + 1) % len(route)]]['latitude'])
        ])
        for i in range(len(route))
    ]
    for i, edge1 in enumerate(edges):
        for j, edge2 in enumerate(edges):
            if i != j and edge1.crosses(edge2):
                return True
    return False

# Fitness function
def fitness(route, locations):
    distance = total_distance(route, locations)
    overlap_penalty = 1e6 if has_overlapping_edges(route, locations) else 0
    fitness_value = 1 / (distance+overlap_penalty) if distance != 0 else float('inf')
    return fitness_value

# Function to select the population
def select_population(locations, size, start_node, end_node):
    population = []
    for _ in range(size):
        route = list(locations.keys())
        route.remove(start_node)  # Exclude start node
        route.remove(end_node)  # Exclude end node
        random.shuffle(route)  # Shuffle remaining nodes
        route = [start_node] + route + [end_node]  # Fix start and end nodes
        distance = total_distance(route, locations)
        population.append([distance, route])
    population = sorted(population, key=lambda x: x[0])
    fittest = population[0]
    return population, fittest

# Function to perform tournament selection
def tournament_selection(population):
    tournament = random.sample(population, TOURNAMENT_SELECTION_SIZE)
    return sorted(tournament, key=lambda x: x[0])[0]

# Function to perform crossover
def crossover(parent1, parent2):
    start = random.randint(0, len(parent1) - 2)
    end = random.randint(start + 1, len(parent1) - 1)
    child_p1 = parent1[start:end]
    child = [item for item in parent2 if item not in child_p1]
    return child[:start] + child_p1 + child[start:]

# Function to perform mutation
def mutate(route):
    if random.random() < MUTATION_RATE:
        idx1, idx2 = random.sample(range(len(route)), 2)
        route[idx1], route[idx2] = route[idx2], route[idx1]
    return route

# Evolving the population over generations
def evolve_population(population, locations):
    new_population = []
    for _ in range(POPULATION_SIZE):
        parent1 = tournament_selection(population)[1]
        parent2 = tournament_selection(population)[1]
        
        # Extract start and end routes
        start_route = parent1[0]
        end_route = parent1[-1]
        
        # Remove start and end from parent routes
        core_parent1 = parent1[1:-1]
        core_parent2 = parent2[1:-1]
        
        # Perform crossover or copy
        if random.random() < CROSSOVER_RATE:
            child_core = crossover(core_parent1, core_parent2)
        else:
            child_core = core_parent1.copy()
        
        # Mutate the middle part
        mutated_child_core = mutate(child_core)
        
        # Reattach start and end routes
        child = [start_route] + mutated_child_core + [end_route]
        
        # Calculate the total distance
        new_population.append([total_distance(child, locations), child])
    
    return sorted(new_population)


def plot_metrics(distances, fitness_values):
    plt.figure(figsize=(12, 5))

    # Plot distances
    plt.subplot(1, 2, 1)
    plt.plot(distances, label='Distance')
    plt.xlabel('Generation')
    plt.ylabel('Distance (m)')
    plt.title('Fittest Route Distance Over Generations')
    plt.legend()

    # Plot fitness values
    plt.subplot(1, 2, 2)
    plt.plot(fitness_values, label='Fitness', color='orange')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title('Fitness Over Generations')
    plt.legend()

    plt.tight_layout()
    


# Main function
def GA(selected_circle, start_node, end_node):

    print("Entering GA")
    locations = selected_circle
    population, fittest = select_population(locations, POPULATION_SIZE, start_node, end_node)

    print(f"Initial fittest route: {fittest[1]} with distance: {fittest[0]:.2f} m and fitness: {fitness(fittest[1], locations):.6f}")

    distances = [fittest[0]]
    fitness_values = [fitness(fittest[1], locations)]

    for generation in range(GENERATIONS):
        population = evolve_population(population, locations)
        population.sort(key=lambda x: x[0])
        fittest = population[0]
        distances.append(fittest[0])
        fitness_values.append(fitness(fittest[1], locations))
        
    fitness_value = fitness(fittest[1], locations) * 1e6
    print(f"Final fittest route: {fittest[1]} with distance: {fittest[0]:.2f} m and fitness: {fitness_value:.6f} ")


    best_generation = fitness_values.index(max(fitness_values))
    best_fitness = max(fitness_values) * 1e6
    print(f"Best fitness achieved at generation {best_generation} with fitness value {best_fitness:.6f}")

    final_route =fittest[1]
    coordinates = [(locations[route]['latitude'], locations[route]['longitude']) for route in final_route]
    plot_metrics(distances, fitness_values)
    print("Final Route :", coordinates)

    return coordinates