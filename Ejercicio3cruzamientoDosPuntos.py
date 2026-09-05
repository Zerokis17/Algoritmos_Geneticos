import random

def cruzamiento_dos_puntos(p1, p2, punto1, punto2):
    i, j = (punto1, punto2) if punto1 < punto2 else (punto2, punto1)
    hijo1 = p1[:i] + p2[i:j] + p1[j:]
    hijo2 = p2[:i] + p1[i:j] + p2[j:]
    return hijo1, hijo2


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
        """Cruzamiento de dos puntos con probabilidad pc.

        Si no ocurre el cruzamiento (random() > pc), se copian los padres.
        Si ocurre, se eligen dos indices distintos en [1, L-1] para que
        el segmento central nunca sea vacio y ambas colas existan.
        """
        if random.random() > self.pc:
            return p1[:], p2[:]
        punto1, punto2 = sorted(random.sample(range(1, self.chromosome_length), 2))
        return cruzamiento_dos_puntos(p1, p2, punto1, punto2)

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



# Asi se demuestra el nuevo operador sin romper ni duplicar el problema.

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
PRESUPUESTO_MAX = 2500
PENALTY_FACTOR = 5


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


def _bits(cromosoma):
    return ''.join(map(str, cromosoma))


def demostrar_cruzamiento_dos_puntos():
    """Muestra un ejemplo fijo del operador, util para la sustentacion."""
    padre1 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    padre2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    i, j = 3, 7
    hijo1, hijo2 = cruzamiento_dos_puntos(padre1, padre2, i, j)

    marca = ' ' * i + '^' + '-' * (j - i - 1) + '^'
    print("\n--- Demostracion: Cruzamiento de Dos Puntos ---")
    print(f"Padre 1: {_bits(padre1)}")
    print(f"Padre 2: {_bits(padre2)}")
    print(f"Cortes:  {marca}   (i={i}, j={j})")
    print(f"Hijo  1: {_bits(hijo1)}   <- cola de P1 + centro de P2 + cola de P1")
    print(f"Hijo  2: {_bits(hijo2)}   <- cola de P2 + centro de P1 + cola de P2")
    print("Interpretacion: solo se intercambia el segmento central [3:7].")
    return hijo1, hijo2


POP_SIZE = 50
CHROM_LEN = len(PROYECTOS)
PC = 0.8
PM = 0.01
NUM_GENERATIONS = 100


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    demostrar_cruzamiento_dos_puntos()

    print("\n--- Ejecutando AG con Cruzamiento de Dos Puntos ---")
    print("(Problema: Portafolio de Inversiones / Mochila)")
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

    print(f"\n--- Resultados Finales (Crossover de Dos Puntos) ---")
    print(f"Mejor Genotipo: {_bits(final_best_genotype)}")
    print(f"Mejor Fitness (Retorno Total): {final_best_fitness:.2f}")
    print(f"Costo Total: {final_best_phenotype['total_costo']}")
    print(f"Presupuesto Maximo: {PRESUPUESTO_MAX}")

    selected_names = [PROYECTOS[i]['name'] for i in final_best_phenotype['selected_items_indices']]
    print(f"Proyectos Seleccionados: {', '.join(selected_names)}")

    plt.figure(figsize=(7, 5))
    plt.plot(range(1, NUM_GENERATIONS + 1), portafolio_ga.max_fitness_history, label='Fitness Maximo')
    plt.plot(range(1, NUM_GENERATIONS + 1), portafolio_ga.avg_fitness_history, label='Fitness Promedio')
    plt.title('Convergencia del AG: Cruzamiento de Dos Puntos')
    plt.xlabel('Generacion')
    plt.ylabel('Fitness (Retorno Total)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('convergencia_ejercicio3.png')
    plt.show()
