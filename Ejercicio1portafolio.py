# Ejercico 1 - Portafolio de Inversiones

import random
import matplotlib.pyplot as plt


#Clase generica del Algoritmo Genetico
class AlgoritmoGenetico:
    def __init__(self, population_size, chromosome_length, pc, pm,
                 fitness_func, decode_func,
                 selection_method='tournament', tournament_size=3,
                 elitism=True):
        self.population_size = population_size
        self.chromosome_length = chromosome_length
        self.pc = pc
        self.pm = pm
        self.fitness_func = fitness_func
        self.decode_func = decode_func
        self.selection_method = selection_method
        self.tournament_size = tournament_size
        self.elitism = elitism

        self.population = self._initialize_population()
        self.max_fitness_history = []
        self.avg_fitness_history = []

    def _initialize_population(self):
        return [[random.randint(0, 1) for _ in range(self.chromosome_length)]
                for _ in range(self.population_size)]

    def _evaluate(self, population):
        return [self.fitness_func(self.decode_func(g)) for g in population]

    def _select(self, population, fitnesses):
        competidores = random.sample(list(zip(population, fitnesses)), self.tournament_size)
        competidores.sort(key=lambda x: x[1], reverse=True)
        return competidores[0][0]

    def _crossover(self, p1, p2):
        if random.random() > self.pc:
            return p1[:], p2[:]
        punto = random.randint(1, self.chromosome_length - 1)
        return p1[:punto] + p2[punto:], p2[:punto] + p1[punto:]

    def _mutate(self, genotype):
        return [1 - bit if random.random() < self.pm else bit for bit in genotype]

    def run(self, num_generations):
        best_genotype_global = None
        best_fitness_global = float('-inf')

        for gen in range(num_generations):
            fitnesses = self._evaluate(self.population)

            self.max_fitness_history.append(max(fitnesses))
            self.avg_fitness_history.append(sum(fitnesses) / len(fitnesses))

            idx_mejor = fitnesses.index(max(fitnesses))
            if fitnesses[idx_mejor] > best_fitness_global:
                best_fitness_global = fitnesses[idx_mejor]
                best_genotype_global = self.population[idx_mejor][:]

            nueva_poblacion = [self.population[idx_mejor][:]] if self.elitism else []

            while len(nueva_poblacion) < self.population_size:
                p1 = self._select(self.population, fitnesses)
                p2 = self._select(self.population, fitnesses)
                h1, h2 = self._crossover(p1, p2)
                nueva_poblacion.append(self._mutate(h1))
                if len(nueva_poblacion) < self.population_size:
                    nueva_poblacion.append(self._mutate(h2))

            self.population = nueva_poblacion

        return best_genotype_global, best_fitness_global


# Definicion especifica para el Portafolio de Inversiones

PROYECTOS = [
    {'name': 'Proyecto A', 'costo': 500, 'retorno': 700},
    {'name': 'Proyecto B', 'costo': 300, 'retorno': 450},
    {'name': 'Proyecto C', 'costo': 800, 'retorno': 1200},
    {'name': 'Proyecto D', 'costo': 200, 'retorno': 250},
    {'name': 'Proyecto E', 'costo': 600, 'retorno': 900},
    {'name': 'Proyecto F', 'costo': 400, 'retorno': 500},
    {'name': 'Proyecto G', 'costo': 700, 'retorno': 1000},
    {'name': 'Proyecto H', 'costo': 100, 'retorno': 150},
    {'name': 'Proyecto I', 'costo': 900, 'retorno': 1300},
    {'name': 'Proyecto J', 'costo': 350, 'retorno': 480},
]
PRESUPUESTO_MAX = 2500  # Restriccion: costo total no puede superar este valor
PENALTY_FACTOR = 5      # Factor de penalizacion fuerte por exceder el presupuesto


def decode_portafolio(genotype: list[int]) -> dict:
    """Decodifica el genotipo binario en costo total, retorno total e indices seleccionados."""
    total_costo = 0
    total_retorno = 0
    selected_items_indices = []
    for i, bit in enumerate(genotype):
        if bit == 1:
            total_costo += PROYECTOS[i]['costo']
            total_retorno += PROYECTOS[i]['retorno']
            selected_items_indices.append(i)
    return {
        'total_costo': total_costo,
        'total_retorno': total_retorno,
        'selected_items_indices': selected_items_indices
    }


def fitness_portafolio(phenotype: dict) -> float:
    """Aptitud = retorno total, con fuerte penalizacion si se excede el presupuesto."""
    total_costo = phenotype['total_costo']
    total_retorno = phenotype['total_retorno']

    if total_costo > PRESUPUESTO_MAX:
        return total_retorno - PENALTY_FACTOR * (total_costo - PRESUPUESTO_MAX)
    return float(total_retorno)


# Parametros del AG
POP_SIZE = 50
CHROM_LEN = len(PROYECTOS)
PC = 0.8
PM = 0.01
NUM_GENERATIONS = 100

print("\n--- Ejecutando AG para el Portafolio de Inversiones ---")
portafolio_ga = AlgoritmoGenetico(
    population_size=POP_SIZE,
    chromosome_length=CHROM_LEN,
    pc=PC,
    pm=PM,
    fitness_func=fitness_portafolio,
    decode_func=decode_portafolio,
    selection_method='tournament',
    tournament_size=5,
    elitism=True,
)

final_best_genotype, final_best_fitness = portafolio_ga.run(NUM_GENERATIONS)
final_best_phenotype = decode_portafolio(final_best_genotype)

print(f"\n--- Resultados Finales Portafolio de Inversiones ---")
print(f"Mejor Genotipo: {''.join(map(str, final_best_genotype))}")
print(f"Mejor Fitness (Retorno Total): {final_best_fitness:.2f}")
print(f"Costo Total: {final_best_phenotype['total_costo']}")
print(f"Presupuesto Maximo: {PRESUPUESTO_MAX}")

selected_names = [PROYECTOS[i]['name'] for i in final_best_phenotype['selected_items_indices']]
print(f"Proyectos Seleccionados: {', '.join(selected_names)}")

# --- Grafica de convergencia (misma logica del Modulo 4 del Colab) ---
plt.figure(figsize=(7, 5))
plt.plot(range(1, NUM_GENERATIONS + 1), portafolio_ga.max_fitness_history, label='Fitness Maximo')
plt.plot(range(1, NUM_GENERATIONS + 1), portafolio_ga.avg_fitness_history, label='Fitness Promedio')
plt.title('Convergencia del AG: Portafolio de Inversiones')
plt.xlabel('Generacion')
plt.ylabel('Fitness (Retorno Total)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('convergencia_ejercicio1.png')
plt.show()