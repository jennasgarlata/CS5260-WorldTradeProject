#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import List, Optional, Union
from ..DataTypes import Action, State, Heuristic, Solution
from ..SearchStrategies import SearchStrategy

class Problem(object):

   STATES: List[State]
   ACTIONS: List[Action]
   HEURISTIC: Union[Heuristic, None]

   def __init__(self, states: List[State], actions: List[Action], heuristic: Optional[Heuristic] = None) -> None:
      super().__init__()
      self.STATES = states
      self.ACTIONS = actions
      self.HEURISTIC = heuristic

   def search(self, initial_state: State, goal_states: List[State], strategy: SearchStrategy) -> Solution:
      return strategy.search(initial_state, self.ACTIONS, self.HEURISTIC, goal_states)
