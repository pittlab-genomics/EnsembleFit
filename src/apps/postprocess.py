import sys
import os
import pandas as pd
import numpy as np
import json
from scipy.spatial.distance import cosine


def as_frequency_colwise(df, skipfirst=True):
    df = df.copy()
    cols = df.columns[1:] if skipfirst else df.columns
    for c in cols:
        if df[c].sum() == 0:
            continue
        df[c] = df[c] / df[c].sum()
    return df


def as_frequency_rowwise(df, skipfirst=True):
    df = df.copy()
    if skipfirst:
        df = df.set_index(df.columns[0])
        df = df.div(df.sum(axis=1), axis=0).reset_index()
    else:
        df = df.div(df.sum(axis=1), axis=0)
    return df


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
        strategy,
        tools):

    print(f'POST-PROCESSING')

    ##########################
    # Format sample profiles
    ##########################
    print('Formatting sample profiles...')
    generate_sbs96_json(sample_path, output_path)
    

    ##########################
    # Load all results
    ##########################
    print('Reading results...')
    sample = list(pd.read_csv(sample_path, sep='\t').columns[1:])
    strats = ['regular', 'remove', 'refit'] if strategy == 'all' else [strategy]
    fit_abs = {strat: {} for strat in strats}
    fit_rel = {strat: {} for strat in strats}
    for tool in tools:
        for strat in strats:
            df = pd.read_csv(os.path.join(output_path, tool, f'{tool}_{strat}.txt'), sep='\t')
            df['Samples']  = sample
            fit_abs[strat][tool] = df
            fit_rel[strat][tool] = as_frequency_rowwise(df)

    ##########################
    # Technical metrics
    ##########################
    print('Generating technical metrics...')
    strategy_name = []
    tool_name = []
    num_cosmic = []
    num_cosmic_mean = []
    prop_mean_assign = []
    mean_assign_val = []
    mean_reconstruct_cossim = []
    
    cat = pd.read_csv(sample_path, sep='\t')
    sample = list(cat.columns[1:])
    total_mutations = np.array(cat.iloc[:, 1:].sum())
    cosmic = pd.read_csv(reference_path, sep='\t')
    cosmic_sig = list(cosmic.columns[1:])

    # REQUIRE absolute value
    for strat in strats:
        for name, fit in fit_abs[strat].items():
            strategy_name.append(strat.capitalize())
            tool_name.append(name)
            
            # drop zeros
            drop_zero_sigs = [s for s in fit.columns[1:] if fit[s].sum() > 0]
            nozero_fit = fit[[fit.columns[0]] + drop_zero_sigs]
            
            # Amount of COSMIC used in assignment
            sigs = list(filter(lambda x: x != 'unassigned', nozero_fit.columns[1:]))
            num_cosmic.append(len(sigs))
            
            # Mean number of COSMIC used per sample
            nums_samples = nozero_fit.iloc[:, 1:].astype(bool).astype(int).sum(axis=1)
            num_cosmic_mean.append(np.mean(nums_samples))
            
            # Amount of mutations assigned with signatures
            drop_zero_sigs = list(filter(lambda x: x != 'unassigned', drop_zero_sigs))
            nozero_noun_fit = fit[[fit.columns[0]] + drop_zero_sigs]
            assigned = np.array(nozero_noun_fit.iloc[:, 1:].sum(axis=1))
            freq_assigned = list(assigned / total_mutations)
            prop_mean_assign.append(np.mean(freq_assigned))
            
            # Reconstruction cosine similarity
            cossims = []
            samples = nozero_fit['Samples']
            #reconstruct = {'MutationType': cosmic['Type']}
            for i, entry in nozero_fit.iterrows():
                sbs96 = np.zeros(96)
                for sig in entry[1:].index:
                    if sig == 'unassigned':
                        continue
                    sbs96 += entry[sig] * cosmic[sig]
                #reconstruct[entry['Samples']] = sbs96
                original = cat.iloc[:, i+1]
                cossims.append(1 - cosine(original, sbs96))
            mean_reconstruct_cossim.append(np.mean(cossims))
            
    prop_mean_assign = list(map(lambda x: 1.0 if x > 1.0 else x, prop_mean_assign))

    metrics = pd.DataFrame({
        'Tool': tool_name,
        'Strategy': strategy_name,
        'Num. COSMIC': num_cosmic,
        'Mean Num. COSMIC per Sample': num_cosmic_mean,
        'Mean Prop. Assigned': prop_mean_assign,
        'Mean Reconstruct Cossim': mean_reconstruct_cossim
    })
    metrics.to_csv(os.path.join(output_path, 'assignment_metrics.txt'), sep='\t', index=False)

    ##########################
    # Assignment summary
    ##########################
    print('Generating assignment summary...')
    sdf = pd.DataFrame()
    strat = 'refit' if strategy == 'all' else strategy
    for tool in tools:
        df = fit_rel[strat][tool].copy()
        for c in cosmic_sig:
            if c not in df.columns:
                df[c] = 0
        df = df.set_index('Samples')
        df.columns = list(map(lambda x: f'{tool}:{x}', df.columns))
        df = df.transpose()
        sdf = pd.concat([sdf, df])

    sdf = sdf.reset_index().rename({'index': 'Signatures'}, axis=1)
    sdf = sdf.rename_axis(None, axis=1)
    sdf.to_csv(os.path.join(output_path, 'assignment_summary.txt'), sep='\t', index=False)

    # Remove signatures that are 0 across all tools and samples
    valid_sigs = []

    for sig in cosmic_sig:
        tmp = sdf[sdf['Signatures'].str.endswith(sig)]
        if tmp.iloc[:, 1:].sum().sum() > 0:
            valid_sigs.append(sig)


    sdf = sdf[sdf['Signatures'].apply(lambda x: x.split(':')[1] in valid_sigs)]

    # Create json
    j = []
    samples = sdf.columns[1:].tolist()
    for i, entry in sdf.iterrows():
        tool, sig = entry['Signatures'].split(':')
        jo = {'tool': tool, 'signature': sig}
        for s in samples:
            jo[s] = entry[s]
        j.append(jo)
        
    # Write json
    with open(os.path.join(output_path, 'assignment_summary.json'), 'w') as f:
        json.dump(j, f, indent=4)

    print('Completed')


if __name__ == '__main__':
    sample_path = sys.argv[1]
    reference_path = sys.argv[2]
    output_path = sys.argv[3]
    strategy = sys.argv[4]
    tools = sys.argv[5:]
    main(sample_path, reference_path, output_path, strategy, tools)