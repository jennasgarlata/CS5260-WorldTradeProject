# Discount factor for discounted reward: DR = gamma^N * (Qend - Qstart)
GAMMA: float = 0.86

# Logistic acceptance parameters: P = 1 / (1 + exp(-k*(x - x0)))
LOGISTIC_K: float = 1.2
LOGISTIC_X0: float = -0.5

# Failure cost used in expected utility: EU = P*DR + (1-P)*C
FAILURE_COST: float = -2.0