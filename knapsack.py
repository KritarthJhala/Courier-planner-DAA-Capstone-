"""Phase 2b - Box filling with 0/1 Knapsack Dynamic Programming.

dp[i][w] = best total value using the first i parcels with capacity w.
    dp[i][w] = dp[i-1][w]                                   if weight_i > w
             = max(dp[i-1][w], value_i + dp[i-1][w-weight_i]) otherwise
Time O(n*W), space O(n*W) (full table kept so the chosen set can be traced back).
"""


def knapsack(parcels, capacity):
    """Return (best_value, chosen_parcels, dp_table)."""
    n = len(parcels)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        p = parcels[i - 1]
        for w in range(capacity + 1):
            dp[i][w] = dp[i - 1][w]
            if p.weight <= w:
                dp[i][w] = max(dp[i][w], p.value + dp[i - 1][w - p.weight])
    # Trace back which parcels were taken
    chosen, w = [], capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            chosen.append(parcels[i - 1])
            w -= parcels[i - 1].weight
    chosen.reverse()
    return dp[n][capacity], chosen, dp


def knapsack_bruteforce(parcels, capacity):
    """Exponential checker used only by tests to verify the DP on small inputs."""
    best = 0
    for mask in range(1 << len(parcels)):
        wt = val = 0
        for i, p in enumerate(parcels):
            if mask >> i & 1:
                wt += p.weight; val += p.value
        if wt <= capacity:
            best = max(best, val)
    return best
