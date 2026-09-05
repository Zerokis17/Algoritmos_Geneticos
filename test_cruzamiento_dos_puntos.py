# Pruebas del Cruzamiento de Dos Puntos (Ejercicio 3)
# Ejecutar:  python -m unittest test_cruzamiento_dos_puntos.py

import random
import unittest

from Ejercicio3cruzamientoDosPuntos import (
    AlgoritmoGenetico,
    cruzamiento_dos_puntos,
    decode_portafolio,
    fitness_portafolio,
)


class TestCruzamientoDosPuntos(unittest.TestCase):
    def test_intercambia_solo_el_segmento_central(self):
        padre1 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        padre2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        hijo1, hijo2 = cruzamiento_dos_puntos(padre1, padre2, 3, 7)

        self.assertEqual(hijo1, [1, 1, 1, 0, 0, 0, 0, 1, 1, 1])
        self.assertEqual(hijo2, [0, 0, 0, 1, 1, 1, 1, 0, 0, 0])

    def test_hijos_conservan_la_longitud(self):
        padre1 = [1, 0, 1, 0, 1, 0, 1, 0]
        padre2 = [0, 1, 0, 1, 0, 1, 0, 1]
        hijo1, hijo2 = cruzamiento_dos_puntos(padre1, padre2, 2, 6)

        self.assertEqual(len(hijo1), len(padre1))
        self.assertEqual(len(hijo2), len(padre2))

    def test_puntos_invertidos_se_ordenan(self):
        padre1 = [1, 1, 1, 1, 1, 1]
        padre2 = [0, 0, 0, 0, 0, 0]

        directo = cruzamiento_dos_puntos(padre1, padre2, 2, 5)
        invertido = cruzamiento_dos_puntos(padre1, padre2, 5, 2)
        self.assertEqual(directo, invertido)

    def test_colas_vienen_del_mismo_padre(self):
        padre1 = [1, 1, 1, 1, 1, 1, 1, 1]
        padre2 = [0, 0, 0, 0, 0, 0, 0, 0]
        i, j = 2, 5
        hijo1, hijo2 = cruzamiento_dos_puntos(padre1, padre2, i, j)

        self.assertEqual(hijo1[:i], padre1[:i])
        self.assertEqual(hijo1[i:j], padre2[i:j])
        self.assertEqual(hijo1[j:], padre1[j:])
        self.assertEqual(hijo2[:i], padre2[:i])
        self.assertEqual(hijo2[i:j], padre1[i:j])
        self.assertEqual(hijo2[j:], padre2[j:])

    def test_pc_cero_copia_a_los_padres(self):
        ga = AlgoritmoGenetico(
            population_size=4,
            chromosome_length=8,
            pc=0.0,
            pm=0.0,
            fitness_func=lambda ph: 0.0,
            decode_func=lambda g: g,
        )
        p1 = [1, 0, 1, 0, 1, 0, 1, 0]
        p2 = [0, 1, 0, 1, 0, 1, 0, 1]
        h1, h2 = ga._crossover(p1, p2)

        self.assertEqual(h1, p1)
        self.assertEqual(h2, p2)
        self.assertIsNot(h1, p1)
        self.assertIsNot(h2, p2)

    def test_pc_uno_siempre_cruza_el_centro(self):
        random.seed(42)
        ga = AlgoritmoGenetico(
            population_size=4,
            chromosome_length=10,
            pc=1.0,
            pm=0.0,
            fitness_func=lambda ph: 0.0,
            decode_func=lambda g: g,
        )
        p1 = [1] * 10
        p2 = [0] * 10
        h1, h2 = ga._crossover(p1, p2)

        self.assertEqual(len(h1), 10)
        self.assertEqual(len(h2), 10)
        self.assertNotEqual(h1, p1)
        self.assertNotEqual(h2, p2)
        self.assertTrue(0 in h1 and 1 in h1)
        self.assertTrue(0 in h2 and 1 in h2)

    def test_run_integra_el_operador_con_el_portafolio(self):
        ga = AlgoritmoGenetico(
            population_size=20,
            chromosome_length=10,
            pc=0.8,
            pm=0.01,
            fitness_func=fitness_portafolio,
            decode_func=decode_portafolio,
            tournament_size=3,
            elitism=True,
        )
        mejor, fitness = ga.run(15)

        self.assertEqual(len(mejor), 10)
        self.assertTrue(all(bit in (0, 1) for bit in mejor))
        self.assertEqual(len(ga.population), 20)
        self.assertEqual(len(ga.max_fitness_history), 15)
        self.assertIsInstance(fitness, float)


if __name__ == "__main__":
    unittest.main()
