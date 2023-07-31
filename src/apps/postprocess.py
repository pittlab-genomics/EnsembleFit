import sys
import os
import shutil
import pandas as pd
import numpy as np
from datetime import datetime
import json

from workflow_utils import as_frequency_rowwise


def generate_sbs96_json(sample_path, output_path):
    cat = pd.read_csv(sample_path, sep='\t')
    res = []
    mut = cat['MutationType']
    cat = cat.set_index('MutationType')
    for sample in cat.columns:
        obj = {'sample': sample}
        for m in mut:
            obj[m] = int(cat[sample][m])
        res.append(obj)
    with open(os.path.join(output_path, 'sbs96_profiles.json'), 'w') as f:
        json.dump(res, f, indent=4)
    return


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

    ###################################
    # FOR WEB PORTAL 
    ###################################

    # Drop the Ensemble
    tools = [t for t in tools if not t.startswith('Ensemble')]

    reference = pd.read_csv(reference_path, sep='\t')
    reference_sig = list(reference.columns[1:])
    sdf = pd.DataFrame()
    for tool in tools:
        df = fit[tool].copy()
        for r in reference_sig:
            if r not in df.columns:
                df[r] = 0
        df = df.set_index('Samples')
        df.columns = list(map(lambda x: f'{tool}:{x}', df.columns))
        df = df.transpose()
        sdf = pd.concat([sdf, df])
    sdf = sdf.reset_index().rename({'index': 'Signatures'}, axis=1)
    sdf = sdf.rename_axis(None, axis=1)
    #print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Generating assignment summary in TXT...')
    #sdf.to_csv(os.path.join(result_path, 'assignment_summary.txt'), sep='\t', index=False)

    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Generating assignment summary in JSON...')
    # Remove signatures that are 0 across all tools and samples
    valid_sigs = []
    for r in reference_sig:
        tmp = sdf[sdf['Signatures'].str.endswith(r)]
        if tmp.iloc[:, 1:].sum().sum() > 0:
            valid_sigs.append(r)
    sdf = sdf[sdf['Signatures'].apply(lambda x: x.split(':')[1] in valid_sigs)]

    # Write JSON for web portal
    j = []
    samples = sdf.columns[1:]
    for i, entry in sdf.iterrows():
        tool, sig = entry['Signatures'].split(':')
        jo = {'tool': tool, 'signature': sig}
        for s in samples:
            jo[s] = entry[s]
        j.append(jo)
    with open(os.path.join(result_path, 'assignment_summary.json'), 'w') as f:
        json.dump(j, f, indent=4)

    # Format SBS96 profiles in JSON for web portal
    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Generating SBS96 profiles in JSON...')
    generate_sbs96_json(sample_path, result_path)

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
