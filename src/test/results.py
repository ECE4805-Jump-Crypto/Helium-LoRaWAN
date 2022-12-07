import numpy as np
import json

def relative_error(predicted: float, actual: float) -> float:
    """Compute the relative error between e and t."""

    return np.abs(actual-predicted) / actual


test_file = 'src/test/results/test_results_12-07-2022-07-41-09.json'
with open(test_file, 'r') as f:
    data = json.load(f)['data']

avg_error = []
knn_error = []
link_earnings_error = []
in_bounds = []
bound_size = []

for h in data:
    if h['weekly_actual'] < 0.05: continue
    avg_error.append(relative_error(h['avg_pred'], h['weekly_actual']))
    knn_error.append(relative_error(h['knn_pred'], h['weekly_actual']))
    link_earnings_error.append(relative_error(h['link_pred'], h['weekly_actual']))
    print(h['n'], h['weekly_actual'], h['avg_pred'], h['knn_pred'], h['link_pred'])
    in_bounds.append(1 if h['interval'][0] <= h['weekly_actual'] <= h['interval'][1] else 0)
    bound_size.append(h['interval'][1] - h['interval'][0])

print('Ensemble error:', np.mean(avg_error))
print('knn error:', np.mean(knn_error))
print('link-earnings error:', np.mean(link_earnings_error))
print('Percent in bounds:', np.mean(in_bounds))
print('Avg. bound size:', np.mean(bound_size))

