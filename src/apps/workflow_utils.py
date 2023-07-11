import pandas as pd
import os


def is_valid_matrix(matrix_path):
    """Check if the matrix is a valid SBS96 catalogue/matrix"""
    matrix = pd.read_csv(matrix_path, sep='\t')
    # Check if matrix is 96xN where N is the number of samples + 1
    if matrix.shape[0] != 96 or matrix.shape[1] < 2:
        return False
    sbs96_features = [f'{b3}[{sub}]{b5}' \
                        for b3 in 'ACGT' \
                        for sub in ['C>A', 'C>G', 'C>T', 'T>A', 'T>C', 'T>G'] \
                        for b5 in 'ACGT']
    # Check if all 96 features are present
    if set(matrix.iloc[:, 0]) != set(sbs96_features):
        return False
    # Check if all values are integers
    if all(matrix.iloc[:, 1:].dtypes != int):
        return False
    # Check if all values are non-negative
    if any(matrix.iloc[:, 1:].min(axis=0) < 0):
        return False
    # Check if all samples have more than 0 mutations
    if any(matrix.iloc[:, 1:].sum(axis=0) == 0):
        return False
    return True
    

def throw_invalid_matrix_error(matrix_path):
    """Throws the relevant error message for an INVALID matrix"""
    matrix = pd.read_csv(matrix_path, sep='\t')
    if matrix.shape[0] != 96 or matrix.shape[1] < 2:
        raise ValueError(f'Matrix shape {matrix.shape} is invalid. Must be (96, N+1) where N is the number of samples.')
    sbs96_features = [f'{b3}[{sub}]{b5}' \
                        for b3 in 'ACGT' \
                        for sub in ['C>A', 'C>G', 'C>T', 'T>A', 'T>C', 'T>G'] \
                        for b5 in 'ACGT']
    if set(matrix.iloc[:, 0]) != set(sbs96_features):
        raise ValueError('Matrix does not contain all 96 SBS96 features.')
    
    invalid_samples = []
    for sample in matrix.columns[1:]:
        if matrix[sample].dtypes != int or matrix[sample].min() < 0 or matrix[sample].sum() == 0:
            invalid_samples.append(sample)
    if invalid_samples:
        invalid_samples_string = ', '.join(invalid_samples)
        raise ValueError(f'Invalid sample(s): {invalid_samples_string}. All samples must have non-negative integers and sum to greater than 0.')



def format_matrix(matrix_path):
    """Formats a VALID matrix to standardized SBS96 for the workflow"""
    matrix = pd.read_csv(matrix_path, sep='\t')
    sbs96_features = [f'{b3}[{sub}]{b5}' \
                        for b3 in 'ACGT' \
                        for sub in ['C>A', 'C>G', 'C>T', 'T>A', 'T>C', 'T>G'] \
                        for b5 in 'ACGT']
    matrix.columns = ['MutationType'] + list(matrix.columns[1:])
    matrix = matrix.set_index('MutationType').reindex(sbs96_features).reset_index()
    matrix.to_csv(matrix_path, sep='\t', index=False)
