import numpy as np
import json

def relative_error(predicted: float, actual: float) -> float:
    """Compute the relative error between e and t."""

    return np.abs(actual-predicted) / actual


test_file = [
    'src/test/results/test_results_12-09-2022-07-43-33.json',
    'src/test/results/test_results_12-09-2022-11-27-47.json',
    'src/test/results/test_results_12-09-2022-19-14-51.json'
]

data = []
for test in test_file:
    with open(test, 'r') as f:
        samples = json.load(f)['data']
        data.extend(samples)

abs_error = []
avg_error = []
knn_error = []
link_earnings_error = []
in_bounds = []
bound_size = []

print('High Error Results:')
for h in data:
    e = np.abs(h['avg_pred'] - h['weekly_actual']) / h['weekly_actual']
    if h['weekly_actual'] < 0.1: continue
    if e > 0.9:
        print('hotspot', h['id'], 'actual earnings (HNT)', h['weekly_actual'], 'predicted (HNT)', h['avg_pred'])
    abs_error.append(np.abs(h['avg_pred'] - h['weekly_actual']))
    avg_error.append(relative_error(h['avg_pred'], h['weekly_actual']))
    knn_error.append(relative_error(h['knn_pred'], h['weekly_actual']))
    link_earnings_error.append(relative_error(h['link_pred'], h['weekly_actual']))
    in_bounds.append(1 if h['interval'][0] <= h['weekly_actual'] <= h['interval'][1] else 0)
    bound_size.append(h['interval'][1] - h['interval'][0])

print('\nNumber of hotspots tested:', len(abs_error))
print('Average error (HNT):', np.mean(abs_error))
print('Median error (HNT):', np.median(abs_error))
print('Min error (HNT):', np.min(abs_error))
print('Max error (HNT):', np.max(abs_error))

print('\nAverage ensemble error (%):', np.mean(avg_error))
print('Average knn model error (%):', np.mean(knn_error))
print('Average link-earnings error: (%)', np.mean(link_earnings_error))
print('Percentage of hotspots in bounds (%):', np.mean(in_bounds))
print('Avgerage bound size: (HNT)', np.mean(bound_size))

