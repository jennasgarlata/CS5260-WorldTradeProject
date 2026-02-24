def compute_state_quality(country, weights):
    score = 0
    for resource, weight in weights.items():
        score += weight * country.get(resource)
    return score
