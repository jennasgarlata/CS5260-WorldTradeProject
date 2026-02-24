#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import List, Union
from ..DataTypes import Action, Heuristic, Node, Solution, State
from .SearchStrategy import SearchStrategy

class DepthFirstSearch(SearchStrategy):

   def __init__(self, tree_based_search: bool) -> None:
      super().__init__(tree_based_search)

   def _expand(self, actions: List[Action], node: Node) -> List[Node]:
      nodes: List[Node] = []
      for action in actions:
         next_state = action.apply(node.STATE)
         if next_state is not None:
            nodes.append(Node(next_state, node, action, node.PATH_COST + action.ACTION_COST))
      return nodes

   def search_with_reached(self, initial_state: State, actions: List[Action], goals: List[State]) -> Solution:
      visited = []
      node = Node(initial_state, None, None, 0.0)
      frontier = [ node ]
      reached = [ node.STATE ]
      while len(frontier):
         node = frontier.pop()
         visited.append(node.STATE)
         if node.STATE in goals:
            return Solution(node, visited)
         for child in self._expand(actions, node):
            if child.STATE not in reached:
               reached.append(child.STATE)
               frontier.append(child)
      return Solution(None)

   def search_without_reached(self, initial_state: State, actions: List[Action], goals: List[State]) -> Solution:
      visited = []
      frontier = [ Node(initial_state, None, None, 0.0) ]
      while len(frontier):
         node = frontier.pop()
         visited.append(node.STATE)
         if node.STATE in goals:
            return Solution(node, visited)
         for child in self._expand(actions, node):
            frontier.append(child)
      return Solution(None)

   def search(self, initial_state: State, actions: List[Action], _heuristic: Union[Heuristic, None], goals: List[State]) -> Solution:
      search_function = self.search_without_reached if self.TREE_BASED_SEARCH else self.search_with_reached
      return search_function(initial_state, actions, goals)
