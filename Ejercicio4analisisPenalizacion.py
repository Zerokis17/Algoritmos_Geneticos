# Ejercicio 4 - Analisis experimental del factor de penalizacion
# Compara PENALTY_FACTOR=5 (Ejercicio 1) contra una penalizacion mas suave.
# No modifica Ejercicio1portafolio.py: reutiliza el mismo AG e instancia.

import json
import random
from pathlib import Path

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
PENALTY_FUERTE = 5
PENALTY_SUAVE = 1

POP_SIZE = 50
CHROM_LEN = len(PROYECTOS)
PC = 0.8
PM = 0.01
NUM_GENERATIONS = 100
TOURNAMENT_SIZE = 5
SEEDS = [7, 11, 23, 42, 99]


def decode_portafolio(genotype):
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
        'selected_items_indices': selected_items_indices,
    }


def make_fitness(penalty_factor):
    def fitness_portafolio(phenotype):
        total_costo = phenotype['total_costo']
        total_retorno = phenotype['total_retorno']
        if total_costo > PRESUPUESTO_MAX:
            return total_retorno - penalty_factor * (total_costo - PRESUPUESTO_MAX)
        return float(total_retorno)
    return fitness_portafolio


class AlgoritmoGenetico:
    """Misma logica del Ejercicio 1, con metricas de factibilidad por generacion."""

    def __init__(self, population_size, chromosome_length, pc, pm,
                 fitness_func, decode_func, tournament_size=3, elitism=True):
        self.population_size = population_size
        self.chromosome_length = chromosome_length
        self.pc = pc
        self.pm = pm
        self.fitness_func = fitness_func
        self.decode_func = decode_func
        self.tournament_size = tournament_size
        self.elitism = elitism

        self.population = self._initialize_population()
        self.max_fitness_history = []
        self.avg_fitness_history = []
        self.feasible_ratio_history = []
        self.best_is_feasible_history = []
        self.best_cost_history = []
        self.best_return_history = []

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

        for _ in range(num_generations):
            phenotypes = [self.decode_func(g) for g in self.population]
            fitnesses = [self.fitness_func(ph) for ph in phenotypes]

            factibles = [ph['total_costo'] <= PRESUPUESTO_MAX for ph in phenotypes]
            idx_mejor = fitnesses.index(max(fitnesses))
            mejor_ph = phenotypes[idx_mejor]

            self.max_fitness_history.append(max(fitnesses))
            self.avg_fitness_history.append(sum(fitnesses) / len(fitnesses))
            self.feasible_ratio_history.append(sum(factibles) / len(factibles))
            self.best_is_feasible_history.append(bool(factibles[idx_mejor]))
            self.best_cost_history.append(mejor_ph['total_costo'])
            self.best_return_history.append(mejor_ph['total_retorno'])

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


def optima_enumeracion():
    """Enumeracion completa (2^10). No es un resultado del AG; es la cota del problema."""
    mejor_factible = None
    mejor_irrestricto = None
    n_factibles = 0

    for mask in range(1 << CHROM_LEN):
        genotype = [(mask >> i) & 1 for i in range(CHROM_LEN)]
        ph = decode_portafolio(genotype)
        if ph['total_costo'] <= PRESUPUESTO_MAX:
            n_factibles += 1
            if mejor_factible is None or ph['total_retorno'] > mejor_factible['total_retorno']:
                mejor_factible = {**ph, 'genotype': genotype}
        if mejor_irrestricto is None or ph['total_retorno'] > mejor_irrestricto['total_retorno']:
            mejor_irrestricto = {**ph, 'genotype': genotype}

    return {
        'espacio': 1 << CHROM_LEN,
        'n_factibles': n_factibles,
        'mejor_factible': mejor_factible,
        'mejor_irrestricto': mejor_irrestricto,
    }


def mean(values):
    values = list(values)
    return sum(values) / len(values)


def mean_series(listas):
    n = len(listas[0])
    return [mean(run[t] for run in listas) for t in range(n)]


def primera_generacion_umbral(ratios, umbral=0.8):
    for t, r in enumerate(ratios, start=1):
        if r >= umbral:
            return t
    return None


def ejecutar_corrida(penalty, seed):
    random.seed(seed)
    ga = AlgoritmoGenetico(
        population_size=POP_SIZE,
        chromosome_length=CHROM_LEN,
        pc=PC,
        pm=PM,
        fitness_func=make_fitness(penalty),
        decode_func=decode_portafolio,
        tournament_size=TOURNAMENT_SIZE,
        elitism=True,
    )
    mejor, fitness = ga.run(NUM_GENERATIONS)
    ph = decode_portafolio(mejor)
    return {
        'seed': seed,
        'penalty': penalty,
        'best_genotype': ''.join(map(str, mejor)),
        'best_fitness': fitness,
        'best_cost': ph['total_costo'],
        'best_return': ph['total_retorno'],
        'best_feasible': ph['total_costo'] <= PRESUPUESTO_MAX,
        'selected': [PROYECTOS[i]['name'] for i in ph['selected_items_indices']],
        'max_fitness_history': ga.max_fitness_history,
        'avg_fitness_history': ga.avg_fitness_history,
        'feasible_ratio_history': ga.feasible_ratio_history,
        'best_is_feasible_history': ga.best_is_feasible_history,
        'best_cost_history': ga.best_cost_history,
        'best_return_history': ga.best_return_history,
        'final_feasible_ratio': ga.feasible_ratio_history[-1],
        'initial_feasible_ratio': ga.feasible_ratio_history[0],
        'gen_80_factible': primera_generacion_umbral(ga.feasible_ratio_history, 0.8),
    }


def resumen_condicion(corridas):
    return {
        'penalty': corridas[0]['penalty'],
        'n_runs': len(corridas),
        'mean_best_fitness': mean(c['best_fitness'] for c in corridas),
        'mean_best_cost': mean(c['best_cost'] for c in corridas),
        'mean_best_return': mean(c['best_return'] for c in corridas),
        'runs_best_feasible': sum(1 for c in corridas if c['best_feasible']),
        'mean_initial_feasible_ratio': mean(c['initial_feasible_ratio'] for c in corridas),
        'mean_final_feasible_ratio': mean(c['final_feasible_ratio'] for c in corridas),
        'mean_feasible_ratio_history': mean_series([c['feasible_ratio_history'] for c in corridas]),
        'mean_max_fitness_history': mean_series([c['max_fitness_history'] for c in corridas]),
        'mean_avg_fitness_history': mean_series([c['avg_fitness_history'] for c in corridas]),
        'mean_best_cost_history': mean_series([c['best_cost_history'] for c in corridas]),
        'mean_best_return_history': mean_series([c['best_return_history'] for c in corridas]),
        'mean_best_is_feasible': mean_series(
            [list(map(int, c['best_is_feasible_history'])) for c in corridas]
        ),
        'corridas': [
            {
                'seed': c['seed'],
                'best_genotype': c['best_genotype'],
                'best_fitness': c['best_fitness'],
                'best_cost': c['best_cost'],
                'best_return': c['best_return'],
                'best_feasible': c['best_feasible'],
                'selected': c['selected'],
                'initial_feasible_ratio': c['initial_feasible_ratio'],
                'final_feasible_ratio': c['final_feasible_ratio'],
                'gen_80_factible': c['gen_80_factible'],
            }
            for c in corridas
        ],
    }


def guardar_graficas(res_fuerte, res_suave, out_dir):
    import matplotlib.pyplot as plt

    gens = list(range(1, NUM_GENERATIONS + 1))

    plt.figure(figsize=(8, 5))
    plt.plot(gens, [r * 100 for r in res_fuerte['mean_feasible_ratio_history']],
             label=f'Penalizacion fuerte (k={PENALTY_FUERTE})')
    plt.plot(gens, [r * 100 for r in res_suave['mean_feasible_ratio_history']],
             label=f'Penalizacion suave (k={PENALTY_SUAVE})')
    plt.title('Supervivencia de soluciones factibles (promedio de 5 semillas)')
    plt.xlabel('Generacion')
    plt.ylabel('Porcentaje de la poblacion con costo <= 2500')
    plt.ylim(0, 105)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_dir / 'comparacion_factibilidad_ejercicio4.png')
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(gens, res_fuerte['mean_best_cost_history'],
             label=f'Costo del mejor (k={PENALTY_FUERTE})')
    plt.plot(gens, res_suave['mean_best_cost_history'],
             label=f'Costo del mejor (k={PENALTY_SUAVE})')
    plt.axhline(PRESUPUESTO_MAX, color='black', linestyle='--', label='Presupuesto maximo')
    plt.title('Costo del mejor individuo por generacion (promedio de 5 semillas)')
    plt.xlabel('Generacion')
    plt.ylabel('Costo')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_dir / 'comparacion_costo_ejercicio4.png')
    plt.close()

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)
    axes[0].plot(gens, res_fuerte['mean_max_fitness_history'], label='Fitness maximo')
    axes[0].plot(gens, res_fuerte['mean_avg_fitness_history'], label='Fitness promedio')
    axes[0].set_title(f'Convergencia con k={PENALTY_FUERTE}')
    axes[0].set_xlabel('Generacion')
    axes[0].set_ylabel('Fitness penalizado')
    axes[0].legend()
    axes[0].grid(True)

    axes[1].plot(gens, res_suave['mean_max_fitness_history'], label='Fitness maximo')
    axes[1].plot(gens, res_suave['mean_avg_fitness_history'], label='Fitness promedio')
    axes[1].set_title(f'Convergencia con k={PENALTY_SUAVE}')
    axes[1].set_xlabel('Generacion')
    axes[1].legend()
    axes[1].grid(True)
    fig.suptitle('El fitness no es comparable entre paneles: cambia la escala de la penalizacion')
    fig.tight_layout()
    fig.savefig(out_dir / 'comparacion_fitness_ejercicio4.png')
    plt.close()


def imprimir_reporte(optimo, res_fuerte, res_suave):
    mf = optimo['mejor_factible']
    mi = optimo['mejor_irrestricto']
    print('=== Cota del problema (enumeracion de 1024 genotipos) ===')
    print(f"Espacio de busqueda: {optimo['espacio']}")
    print(f"Soluciones factibles: {optimo['n_factibles']}")
    print(f"Optimo factible: retorno={mf['total_retorno']}, costo={mf['total_costo']}, "
          f"genotipo={''.join(map(str, mf['genotype']))}")
    print(f"Optimo irrestricto: retorno={mi['total_retorno']}, costo={mi['total_costo']}")

    for titulo, res in (('FUERTE k=5', res_fuerte), ('SUAVE k=1', res_suave)):
        print(f'\n=== Resultados AG — {titulo} ===')
        print(f"Mejor fitness medio: {res['mean_best_fitness']:.2f}")
        print(f"Mejor costo medio: {res['mean_best_cost']:.2f}")
        print(f"Mejor retorno medio (sin penalizar): {res['mean_best_return']:.2f}")
        print(f"Corridas cuyo mejor global es factible: {res['runs_best_feasible']}/{res['n_runs']}")
        print(f"% factible inicial medio: {100 * res['mean_initial_feasible_ratio']:.1f}")
        print(f"% factible final medio: {100 * res['mean_final_feasible_ratio']:.1f}")
        print('Detalle por semilla:')
        for c in res['corridas']:
            print(
                f"  seed={c['seed']} geno={c['best_genotype']} "
                f"fit={c['best_fitness']:.1f} costo={c['best_cost']} "
                f"retorno={c['best_return']} factible={c['best_feasible']} "
                f"%fact0={100 * c['initial_feasible_ratio']:.0f} "
                f"%fact100={100 * c['final_feasible_ratio']:.0f} "
                f"gen>=80%={c['gen_80_factible']}"
            )


if __name__ == '__main__':
    out_dir = Path(__file__).resolve().parent
    optimo = optima_enumeracion()

    corridas_fuerte = [ejecutar_corrida(PENALTY_FUERTE, seed) for seed in SEEDS]
    corridas_suave = [ejecutar_corrida(PENALTY_SUAVE, seed) for seed in SEEDS]
    res_fuerte = resumen_condicion(corridas_fuerte)
    res_suave = resumen_condicion(corridas_suave)

    payload = {
        'parametros': {
            'population_size': POP_SIZE,
            'chromosome_length': CHROM_LEN,
            'pc': PC,
            'pm': PM,
            'num_generations': NUM_GENERATIONS,
            'tournament_size': TOURNAMENT_SIZE,
            'elitism': True,
            'presupuesto_max': PRESUPUESTO_MAX,
            'penalty_fuerte': PENALTY_FUERTE,
            'penalty_suave': PENALTY_SUAVE,
            'seeds': SEEDS,
        },
        'optimo_enumeracion': {
            'espacio': optimo['espacio'],
            'n_factibles': optimo['n_factibles'],
            'mejor_factible': {
                'genotype': ''.join(map(str, optimo['mejor_factible']['genotype'])),
                'total_costo': optimo['mejor_factible']['total_costo'],
                'total_retorno': optimo['mejor_factible']['total_retorno'],
                'proyectos': [PROYECTOS[i]['name'] for i in optimo['mejor_factible']['selected_items_indices']],
            },
            'mejor_irrestricto': {
                'genotype': ''.join(map(str, optimo['mejor_irrestricto']['genotype'])),
                'total_costo': optimo['mejor_irrestricto']['total_costo'],
                'total_retorno': optimo['mejor_irrestricto']['total_retorno'],
            },
        },
        'fuerte': res_fuerte,
        'suave': res_suave,
    }
    (out_dir / 'resultados_ejercicio4.json').write_text(
        json.dumps(payload, indent=2), encoding='utf-8'
    )

    imprimir_reporte(optimo, res_fuerte, res_suave)
    guardar_graficas(res_fuerte, res_suave, out_dir)
    print('\nArchivos: resultados_ejercicio4.json, comparacion_*_ejercicio4.png')
