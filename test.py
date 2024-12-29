import matplotlib.pyplot as plt
import random
import math


class HexGridGA:
    def __init__(self, grid_size, start, end, population_size, generations, mutation_rate):
        self.grid_size = grid_size
        self.start = start
        self.end = end
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.grid_nodes = self.generate_grid_nodes()
        self.population = self.initialize_population()

    def generate_grid_nodes(self):
        # Generate all nodes in the hexagonal grid
        nodes = set()
        for x in range(-self.grid_size, self.grid_size + 1):
            for y in range(max(-self.grid_size, -x - self.grid_size),
                           min(self.grid_size, -x + self.grid_size) + 1):
                nodes.add((x, y))
        return list(nodes)

    def initialize_population(self):
        # Initialize the population with random paths
        population = []
        for _ in range(self.population_size):
            path = self.grid_nodes[:]
            random.shuffle(path)
            path.remove(self.start)
            path.remove(self.end)
            path = [self.start] + path + [self.end]
            population.append(path)
        return population

    def calculate_turns(self, path):
        # Calculate the number of turns in the path
        turns = 0
        for i in range(1, len(path) - 1):
            prev_step = (path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1])
            next_step = (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])
            if prev_step != next_step:  # A turn occurs when directions differ
                turns += 1
        return turns

    def fitness(self, path):
        # Calculate fitness based on path validity, distance, and number of turns
        if len(set(path)) != len(self.grid_nodes):  # Check if all nodes are visited exactly once
            return 0

        total_distance = sum(math.dist(path[i], path[i + 1]) for i in range(len(path) - 1))
        turns = self.calculate_turns(path)
        
        # Minimize distance and turns (fewer turns are better)
        return 1 / (total_distance + 0.5 * turns)

    def selection(self):
        # Select parents using tournament selection
        tournament_size = 5
        parents = []
        for _ in range(2):
            tournament = random.sample(self.population, tournament_size)
            best = max(tournament, key=self.fitness)
            parents.append(best)
        return parents

    def crossover(self, parent1, parent2):
        # Partially Mapped Crossover (PMX)
        size = len(parent1)
        start, end = sorted(random.sample(range(1, size - 1), 2))
        child = [None] * size
        child[start:end] = parent1[start:end]
        
        for i in range(start, end):
            if parent2[i] not in child:
                pos = i
                while child[pos] is not None:
                    pos = parent2.index(parent1[pos])
                child[pos] = parent2[i]
        
        for i in range(size):
            if child[i] is None:
                child[i] = parent2[i]
        
        return child

    def mutate(self, path):
        # Swap mutation
        if random.random() < self.mutation_rate:
            idx1, idx2 = random.sample(range(1, len(path) - 1), 2)
            path[idx1], path[idx2] = path[idx2], path[idx1]

    def evolve(self):
        new_population = []
        for _ in range(self.population_size):
            parent1, parent2 = self.selection()
            child = self.crossover(parent1, parent2)
            self.mutate(child)
            new_population.append(child)
        self.population = new_population

    def run(self):
        best_path = None
        best_fitness = -float("inf")
        for generation in range(self.generations):
            self.population.sort(key=self.fitness, reverse=True)
            current_best = self.population[0]
            current_fitness = self.fitness(current_best)
            
            if current_fitness > best_fitness:
                best_path = current_best
                best_fitness = current_fitness
            
            self.evolve()
        
        return best_path

    def visualize(self, best_path):
        # Visualize the grid and the path
        fig, ax = plt.subplots(figsize=(8, 8))
        for x, y in self.grid_nodes:
            # Plot hexagonal grid nodes
            ax.plot(x, y, 'o', color='lightgray')

        # Plot path
        x_coords, y_coords = zip(*best_path)
        ax.plot(x_coords, y_coords, '-o', color='blue', label='Path')
        ax.plot(self.start[0], self.start[1], 'go', label='Start')  # Start point in green
        ax.plot(self.end[0], self.end[1], 'ro', label='End')  # End point in red

        ax.legend()
        ax.set_aspect('equal')
        ax.set_title("Hexagonal Grid with Optimal Path")
        plt.grid(False)
        plt.show()


# Parameters
grid_size = 3  # Radius of the hexagonal grid
start = (0, 0)  # Starting point
end = (1, -1)  # Ending point
population_size = 100
generations = 500
mutation_rate = 0.1

# Run GA
ga = HexGridGA(grid_size, start, end, population_size, generations, mutation_rate)
best_path = ga.run()
print("Best Path:", best_path)

# Visualize the result
ga.visualize(best_path)
