import sys
import os
import shutil
import pandas as pd
import numpy as np
from datetime import datetime

from workflow_utils import as_frequency_rowwise

def main(sample_path,
        reference_path,
        output_path,
        result_path,
        strategy,
        tools):

    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Reading results...')
    all_samples = pd.read_csv(sample_path, sep='\t').columns[1:].tolist()
    all_sigs = pd.read_csv(reference_path, sep='\t').columns[1:].tolist()
    fit = {}
    for tool in tools:
        tooldir = 'EnsembleFit' if tool.startswith('Ensemble') else tool
        df = pd.read_csv(os.path.join(output_path, tooldir, f'{tool}_{strategy}.txt'), sep='\t')
        df['Samples']  = all_samples
        for sig in all_sigs:
            if sig not in df.columns:
                df[sig] = 0
        # Qualitative Ensemble no need to convert to frequency
        if tool in ['Ensemble-Majority', 'Ensemble-Unanimous']:
            fit[tool] = df
        else:
            fit[tool] = as_frequency_rowwise(df)

    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Generating results directory...')
    os.makedirs(result_path, exist_ok=True)
    for tool in tools:
        tooldir = 'EnsembleFit' if tool.startswith('Ensemble') else tool
        os.makedirs(os.path.join(result_path, tooldir), exist_ok=True)
        fit[tool].to_csv(os.path.join(result_path, tooldir, f'{tool}_{strategy}.txt'), sep='\t', index=False)

    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Completed')


if __name__ == '__main__':
    sample_path = sys.argv[1]
    reference_path = sys.argv[2]
    output_path = sys.argv[3]
    result_path = sys.argv[4]
    strategy = sys.argv[5]
    tools = sys.argv[6:]

    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Start')
    print(f'    - Sample Path: {sample_path}')
    print(f'    - Reference Path: {reference_path}')
    print(f'    - Output Path: {output_path}')
    print(f'    - Strategy: {strategy}')
    print(f'    - Tools: {", ".join(tools)}')

    main(sample_path, reference_path, output_path, result_path, strategy, tools)
