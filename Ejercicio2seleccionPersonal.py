# Ejercicio 2 - Seleccion de Personal Estricta

import random
import matplotlib.pyplot as plt

# Clase generica del Algoritmo Genetico 
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


# Definicion especifica para la Seleccion de Personal

random.seed(7)  # semilla fija para que la habilidad de los candidatos sea reproducible
CANDIDATOS = [
    {'name': f'Candidato {i + 1}', 'habilidad': random.randint(50, 100)} for i in range(12)
]
TAMANO_EQUIPO = 5   # Restriccion: el equipo debe tener EXACTAMENTE 5 personas.
PENALTY_FACTOR = 100  # Factor de penalizacion fuerte por cada persona de mas o de menos.


def decode_seleccion(genotype: list[int]) -> dict:
    """Decodifica el genotipo binario en numero de seleccionados, habilidad total e indices."""
    total_habilidad = 0
    selected_items_indices = []
    for i, bit in enumerate(genotype):
        if bit == 1:
            total_habilidad += CANDIDATOS[i]['habilidad']
            selected_items_indices.append(i)
    return {
        'num_seleccionados': len(selected_items_indices),
        'total_habilidad': total_habilidad,
        'selected_items_indices': selected_items_indices
    }


def fitness_seleccion(phenotype: dict) -> float:
    """Aptitud = habilidad total, penalizando si no se seleccionan exactamente 5 personas."""
    num_seleccionados = phenotype['num_seleccionados']
    total_habilidad = phenotype['total_habilidad']

    diferencia = abs(num_seleccionados - TAMANO_EQUIPO)
    return total_habilidad - PENALTY_FACTOR * diferencia


# Parametros del AG
POP_SIZE = 50
CHROM_LEN = len(CANDIDATOS)
PC = 0.8
PM = 0.01
NUM_GENERATIONS = 100

print("\n--- Ejecutando AG para la Seleccion de Personal ---")
seleccion_ga = AlgoritmoGenetico(
    population_size=POP_SIZE,
    chromosome_length=CHROM_LEN,
    pc=PC,
    pm=PM,
    fitness_func=fitness_seleccion,
    decode_func=decode_seleccion,
    selection_method='tournament',
    tournament_size=5,
    elitism=True,
)

final_best_genotype, final_best_fitness = seleccion_ga.run(NUM_GENERATIONS)
final_best_phenotype = decode_seleccion(final_best_genotype)

print(f"\n--- Resultados Finales Seleccion de Personal ---")
print(f"Mejor Genotipo: {''.join(map(str, final_best_genotype))}")
print(f"Mejor Fitness (Habilidad Total): {final_best_fitness:.2f}")
print(f"Numero de Seleccionados: {final_best_phenotype['num_seleccionados']} / {TAMANO_EQUIPO}")

selected_names = [CANDIDATOS[i]['name'] for i in final_best_phenotype['selected_items_indices']]
print(f"Candidatos Seleccionados: {', '.join(selected_names)}")

# Grafica de convergencia (misma logica del Modulo 4 del Colab)
plt.figure(figsize=(7, 5))
plt.plot(range(1, NUM_GENERATIONS + 1), seleccion_ga.max_fitness_history, label='Fitness Maximo')
plt.plot(range(1, NUM_GENERATIONS + 1), seleccion_ga.avg_fitness_history, label='Fitness Promedio')
plt.title('Convergencia del AG: Seleccion de Personal')
plt.xlabel('Generacion')
plt.ylabel('Fitness (Habilidad Total)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('convergencia_ejercicio2.png')
plt.show()