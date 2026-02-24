#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
from uuid import UUID, uuid4

class State(object):

   ID: UUID
   NAME: str

   def __init__(self, name: str) -> None:
      super().__init__()
      self.ID = uuid4()
      self.NAME = name

   def __eq__(self, other: State) -> bool:
      return self.ID == other.ID

   def __hash__(self) -> int:
      return hash(self.ID)

   def __repr__(self) -> str:
      return self.NAME
