# prepare data for GA
# need keys and coordinate
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import random
import matplotlib.pyplot as plt
import math

# Parameters
POPULATION_SIZE = 150
MUTATION_RATE = 0.5
CROSSOVER_RATE = 0.7
GENERATIONS = 1000
TOURNAMENT_SELECTION_SIZE = 3

# Euclidean distance formula
def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Function to calculate the total distance for a given route
def total_distance(route, locations):
    print("Route", route)
    total = 0
    for i in range(len(route)):
        start = route[i]
        end = route[(i + 1) % len(route)]
        total += euclidean_distance(locations[start]['latitude'], locations[start]['longitude'],
                           locations[end]['latitude'], locations[end]['longitude'])
    return total

# Fitness function
def fitness(route,locations):
    distance = total_distance(route, locations)
    return 1 / distance if distance != 0 else float('inf')

# Function to select the population
def select_population(locations, size):
    population = []
    for _ in range(size):
        route = list(locations.keys())
        random.shuffle(route)
        distance = total_distance(route, locations)
        population.append([distance, route])
    population = sorted(population)
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
        child = crossover(parent1, parent2) if random.random() < CROSSOVER_RATE else parent1.copy()
        new_population.append([total_distance(mutate(child), locations), child])
    return sorted(new_population)

# Main function
def GA(selected_circle):

    # area_coordinate = {}
    # for i, circle in enumerate(selected_circle):
    #     area_coordinate[f"Location {i+1}"] = {
    #         'latitude': circle["center"][0],
    #         'longitude': circle["center"][1]
    #     }

    # print("Area coordinate: ", area_coordinate)


    locations = selected_circle
    population, fittest = select_population(locations, POPULATION_SIZE)

    print(f"Initial fittest route: {fittest[1]} with distance: {fittest[0]:.2f} m and fitness: {fitness(fittest[1], locations):.2f}")

    distances = [fittest[0]]
    fitness_values = [fitness(fittest[1], locations)]

    for generation in range(GENERATIONS):
        population = evolve_population(population, locations)
        fittest = population[0]
        distances.append(fittest[0])
        fitness_values.append(fitness(fittest[1], locations))

    print(f"Final fittest route: {fittest[1]} with distance: {fittest[0]:.2f} m and fitness: {fitness(fittest[1], locations):.2f}")

    plt.plot(distances)
    plt.xlabel('Generation')
    plt.ylabel('Distance (m)')
    plt.title('Fittest Route Distance Over Generations')
    plt.show()

    plt.plot(fitness_values)
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title('Fitness Over Generations')
    plt.show()

    best_generation = fitness_values.index(max(fitness_values))
    best_fitness = max(fitness_values)
    print(f"Best fitness achieved at generation {best_generation} with fitness value {best_fitness:.2f}")