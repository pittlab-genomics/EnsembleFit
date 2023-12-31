import os
import sys
from datetime import datetime
import math
import pandas as pd
import numpy as np
import random

from workflow_utils import as_frequency_rowwise


def ensemble_qualitative(fit, all_sigs, all_samples):
    print('Ensemble-Majority/Unanimous: Voting...')
    ens_majority = pd.DataFrame({'Samples': all_samples})
    ens_unanimous = pd.DataFrame({'Samples': all_samples})
    tools = list(fit.keys())
    for sig in all_sigs:
        vals = np.zeros(len(all_samples)).astype(int)
        for tool in tools:
            vals += fit[tool][sig].astype(bool).astype(int)
        ens_majority[sig] = (vals > math.ceil(len(tools) / 2)).astype(int)
        ens_unanimous[sig] = (vals == len(tools)).astype(int)
    return ens_majority, ens_unanimous


def ensemble_quantitative(fit, all_sigs, all_samples):
    print('Ensemble-Mean: Bootstrapping...')
    def bootstrap(arr, k, size=500):
        return np.mean([np.mean(random.choices(arr, k=k)) for _ in range(size)])

    random.seed(37)
    ens_mean = pd.DataFrame({'Samples': all_samples})
    tools = list(fit.keys())
    for sig in all_sigs:
        bootstrap_means = []
        for sample in all_samples:
            vals = [fit[tool].set_index('Samples').loc[sample, sig] for tool in tools]
            # Only bootstrap if sum is not 0
            val = 0 if sum(vals) == 0 else bootstrap(vals, len(tools), size=500)
            bootstrap_means.append(val)
        ens_mean[sig] = bootstrap_means
    return ens_mean


def main(sample_path, reference_path, output_path, strategy, tools):
    if not os.path.exists(os.path.join(output_path, 'EnsembleFit')):
        os.makedirs(os.path.join(output_path, 'EnsembleFit'))

    all_samples = pd.read_csv(sample_path, sep='\t').columns[1:].tolist()
    all_sigs = pd.read_csv(reference_path, sep='\t').columns[1:].tolist()
    fit = {}
    for tool in tools:
        df = pd.read_csv(os.path.join(output_path, tool, f'{tool}_{strategy}.txt'), sep='\t')
        df['Samples']  = all_samples
        for sig in all_sigs:
            if sig not in df.columns:
                df[sig] = 0
        fit[tool] = as_frequency_rowwise(df)

    ens_majority, ens_unanimous = ensemble_qualitative(fit, all_sigs, all_samples)
    ens_mean = ensemble_quantitative(fit, all_sigs, all_samples)
    ens_majority.to_csv(os.path.join(output_path, 'EnsembleFit', f'Ensemble-Majority_{strategy}.txt'), sep='\t', index=False)
    ens_unanimous.to_csv(os.path.join(output_path, 'EnsembleFit', f'Ensemble-Unanimous_{strategy}.txt'), sep='\t', index=False)
    ens_mean.to_csv(os.path.join(output_path, 'EnsembleFit', f'Ensemble-Mean_{strategy}.txt'), sep='\t', index=False)

    
if __name__ == '__main__':
    if len(sys.argv) < 5:
        sys.exit("Need at least 5 arguments: sample_path reference_path output_path strategy [tools]")
    sample_path = sys.argv[1]
    reference_path = sys.argv[2]
    output_path = sys.argv[3]
    strategy = sys.argv[4]
    tools = sys.argv[5:]
    
    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Start')
    print(f'    - Sample Path: {sample_path}')
    print(f'    - Reference Path: {reference_path}')
    print(f'    - Output Path: {output_path}')
    print(f'    - Strategy: {strategy}')
    print(f'    - Tools: {", ".join(tools)}')

    main(sample_path, reference_path, output_path, strategy, tools)