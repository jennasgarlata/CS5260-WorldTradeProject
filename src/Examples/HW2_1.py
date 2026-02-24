#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
from ..DataTypes import Action, Heuristic, State
from ..ProblemFormulations import ExplicitGraph
from ..SearchStrategies import BreadthFirstSearch, DepthFirstSearch, HeuristicDepthFirstSearch
from ..SearchStrategies import GreedyBestFirstSearch, UniformCostSearch

# Generate the explicit homework graph
states = { 'S': State('S'), 'A': State('A'), 'B': State('B'), 'C': State('C'),
           'D': State('D'), 'E': State('E'), 'G1': State('G1'), 'G2': State('G2') }
goals = [ states['G1'], states['G2'] ]
actions = { 'SA': Action([lambda state, s=states: state == s['S']], 1, states['A']),
            'SD': Action([lambda state, s=states: state == s['S']], 4, states['D']),
            'AB': Action([lambda state, s=states: state == s['A']], 2, states['B']),
            'AC': Action([lambda state, s=states: state == s['A']], 2, states['C']),
            'BD': Action([lambda state, s=states: state == s['B']], 2, states['D']),
            'CE': Action([lambda state, s=states: state == s['C']], 4, states['E']),
            'CG1': Action([lambda state, s=states: state == s['C']], 5, states['G1']),
            'DE': Action([lambda state, s=states: state == s['D']], 2, states['E']),
            'EG1': Action([lambda state, s=states: state == s['E']], 2, states['G1']),
            'EG2': Action([lambda state, s=states: state == s['E']], 1, states['G2']) }
heuristics = { states['S']: 7, states['A']: 4, states['B']: 2, states['C']: 3,
               states['D']: 5, states['E']: 2, states['G1']: 0, states['G2']: 0 }
graph = ExplicitGraph(states.values(), actions.values(), Heuristic(lambda state, h=heuristics: h[state]))

# Search for solutions using various search strategies
bfs_solution = graph.search(states['S'], goals, BreadthFirstSearch(False))
dfs_solution = graph.search(states['S'], goals, DepthFirstSearch(False))
hdfs_solution = graph.search(states['S'], goals, HeuristicDepthFirstSearch(False))
hdfs_wo_reached_solution = graph.search(states['S'], goals, HeuristicDepthFirstSearch(True))
gbfs_solution = graph.search(states['S'], goals, GreedyBestFirstSearch(False))
ucs_solution = graph.search(states['S'], goals, UniformCostSearch(False))

# Output the paths found by each strategy
print('\nBreadth-First Search:')
bfs_solution.print_solution()
bfs_solution.print_visited_order()
print('\nDepth-First Search:')
dfs_solution.print_solution()
dfs_solution.print_visited_order()
print('\nHeuristic Depth-First Search (with reached):')
hdfs_solution.print_solution()
hdfs_solution.print_visited_order()
print('\nHeuristic Depth-First Search (without reached):')
hdfs_wo_reached_solution.print_solution()
hdfs_wo_reached_solution.print_visited_order()
print('\nGreedy Best-First Search:')
gbfs_solution.print_solution()
gbfs_solution.print_visited_order()
print('\nUniform Cost Search:')
ucs_solution.print_solution()
ucs_solution.print_visited_order()
