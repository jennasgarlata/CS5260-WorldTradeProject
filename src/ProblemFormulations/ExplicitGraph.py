#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import List, Optional
from ..DataTypes import Action, State, Heuristic
from .Problem import Problem

class ExplicitGraph(Problem):

   def __init__(self, states: List[State], actions: List[Action], heuristic: Optional[Heuristic] = None) -> None:
      super().__init__(states, actions, heuristic)
