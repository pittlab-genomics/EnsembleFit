import json
import textwrap
import os
import sys
import pandas as pd
import datetime


tool_string = {
    'SigProfilerAssignment': 'SigProfilerAssignment (0.0.13)',
    'Sigminer': 'Sigminer (2.1.7)',
    'SignatureToolsLib': 'SignatureToolsLib (2.1.2)',
    'MutationalPatterns': 'MutationalPatterns (3.4.1)',
    'MutSignatures': 'MutSignatures (2.1.1)',
}

analysis_description_string = {
    'regular': '',
    'remove': '',
    'refit': '',
}


def main(config_path, matrix_path, output_path):
    with open(config_path) as f:
        config = json.load(f)

    genome = config['reference_build']
    signature_reference = config['signature_reference']
    analysis = config['analysis']
    mat = pd.read_csv(matrix_path, sep='\t')
    nsamples = mat.shape[1] - 1
    tools = config['tools']


    res = f'{"INPUT INFO".center(50, "=")}\n'
    res += f'Job Date: {datetime.datetime.utcnow().strftime("%Y %b %d %H:%M:%S")} UTC\n'
    res += f'Number of samples: {nsamples}\n'
    res += f'Reference genome: {genome}\n'
    res += f'Signature database: {signature_reference}\n'
    res += f'{"WORKFLOW INFO".center(50, "=")}\n'
    tools_str = '\n - '.join([tool_string[tool] for tool in tools])
    res += f'Tools:\n - {tools_str}\n\n'
    res += f'Strategy: {analysis}\n'
    res += f'{"".center(50, "=")}\n\n'
    
    # For users to copy-paste if they want to cite this workflow
    res += 'If you use EnsembleFit results in your research, please include the information:\n\n'
    formatted_tools = [tool_string[tool] for tool in tools]
    tools_str = ', '.join(formatted_tools[:-1]) + ', and ' + formatted_tools[-1]
    sentence = f'EnsembleFit was ran using the "{analysis}" strategy on {tools_str} signature assignment tools.'
    #sentence += f' The Ensemble-Mean assignment is the mean estimated from a bootstrap resampling of the {len(tools)} tools at 500 iterations.\n'
    if res[-1] != '\n':
        res += '\n'
    res += textwrap.fill(sentence, 80)

    #print(res)
    with open(os.path.join(output_path, 'job_metadata.txt'), 'w') as f:
        f.write(res)


if __name__ == '__main__':
    config_path = sys.argv[1]
    matrix_path = sys.argv[2]
    output_path = sys.argv[3]
    main(config_path, matrix_path, output_path)
