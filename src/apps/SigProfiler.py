import sys
import os
import pandas as pd
import numpy as np
import shutil
from SigProfilerAssignment import Analyzer as Analyze


def sigprofiler_regular(sample_path, reference_path, output_path):
    run_output_path = os.path.join(output_path, 'regular')
    Analyze.cosmic_fit(sample_path, 
                   run_output_path,
                   signature_database=reference_path,
                   make_plots=False,
                   initial_remove_penalty=0.0001,
                   )
    shutil.copy(
        os.path.join(run_output_path, 'Assignment_Solution/Activities/Assignment_Solution_Activities.txt'),
        os.path.join(output_path, 'SigProfilerAssignment_regular.txt')
        )


def sigprofiler_remove(sample_path, reference_path, output_path):
    if not os.path.isfile(os.path.join(output_path, 'SigProfilerAssignment_regular.txt')):
        sigprofiler_regular(sample_path, reference_path, output_path)

    cat = pd.read_csv(sample_path, sep='\t')
    samples = cat.columns[1:].tolist()
    specimens = list(map(lambda x: x.split('::')[-1], samples))
    total_mutations = np.array(cat.iloc[:, 1:].sum())
    spa = pd.read_csv(os.path.join(output_path, 'SigProfilerAssignment_regular.txt'), sep='\t')
    unassigned = []
    for i, entry in spa.iterrows():
        assignment = entry.iloc[1:].tolist()
        sample_total = total_mutations[i]
        strict_assignment = list(map(lambda x: x if x/sample_total > 0.05 else 0, assignment))
        spa.iloc[i, 1:] = strict_assignment
        unassigned.append(sample_total - spa.iloc[i, 1:].sum())
    spa['unassigned'] = unassigned
    spa.to_csv(os.path.join(output_path, 'SigProfilerAssignment_remove.txt'), sep='\t', index=False)


def sigprofiler_refit(sample_path, reference_path, output_path):
    run_output_path = os.path.join(output_path, 'refit')
    Analyze.cosmic_fit(sample_path, 
                   run_output_path,
                   signature_database=reference_path,
                   make_plots=False,
                   )
    shutil.copy(
        os.path.join(run_output_path, 'Assignment_Solution/Activities/Assignment_Solution_Activities.txt'),
        os.path.join(output_path, 'SigProfilerAssignment_refit.txt')
        )


def main(sample_path, reference_path, output_path, strategy):
    strategy_map = {
        'regular': sigprofiler_regular,
        'remove': sigprofiler_remove,
        'refit': sigprofiler_refit,
        # STUB
        'refit_general': sigprofiler_refit
    }
    if strategy == 'all':
        for strat in strategy_map.values():
            strat(sample_path, reference_path, output_path)
    else:
        strategy_map[strategy](sample_path, reference_path, output_path)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        sys.exit("Need 4 arguments: sample_path reference_path output_path strategy")
    sample_path = sys.argv[1]
    reference_path = sys.argv[2]
    output_path = sys.argv[3]
    strategy = sys.argv[4]
    main(sample_path, reference_path, output_path, strategy)
