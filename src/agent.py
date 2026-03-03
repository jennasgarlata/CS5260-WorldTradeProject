# src/agent.py

from ProblemFormulations.TradeScheduleProblem import TradeScheduleProblem
from SearchStrategies.GreedyBestFirstSearch import GreedyBestFirstSearch

class TradeAgent:
    def __init__(self, self_country: str, max_depth: int = 4):
        self.self_country = self_country
        self.max_depth = max_depth

    def plan(self, initial_world):
        problem = TradeScheduleProblem(
            initial_world=initial_world,
            self_country=self.self_country,
            max_depth=self.max_depth
        )

        search = GreedyBestFirstSearch(

        )

        solution = search.solve(problem)  

        return solution