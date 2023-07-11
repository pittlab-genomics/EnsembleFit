import os
import parsl
from parsl.app.app import bash_app

from src.common.workflow_common import (
    CONDA_SOURCE_PATH,
    ENSEMBLEFIT_CONDA_ENV
)

REALPATH = os.path.dirname(os.path.realpath(__file__))
TOOLS_PATHS = {
    'generate_matrix': os.path.join(REALPATH, 'generate_matrix.py'),
    'SigProfilerAssignment': os.path.join(REALPATH, 'SigProfiler.py'),
    'Sigminer': os.path.join(REALPATH, 'Sigminer.r'),
    'SignatureToolsLib': os.path.join(REALPATH, 'SignatureToolsLib.r'),
    'MutationalPatterns': os.path.join(REALPATH, 'MutationalPatterns.r'),
    'MutSignatures': os.path.join(REALPATH, 'MutSignatures.r'),
    'SigFit': os.path.join(REALPATH, 'SigFit.r'),
    'postprocess': os.path.join(REALPATH, 'postprocess.py'),
    'generate_job_metadata': os.path.join(REALPATH, 'generate_job_metadata.py')
}


@bash_app
def generate_matrix(vcf_path,
                    reference_build,
                    scratch_path,
                    outputs=None,
                    stdout=parsl.AUTO_LOGNAME,
                    stderr=parsl.AUTO_LOGNAME):
    tool_path = TOOLS_PATHS['generate_matrix']
    cmd = """
    export MPLCONFIGDIR={scratch_path}
    python {tool_path} {vcf_path} {reference_build}
    """.format(
        conda_source_path=CONDA_SOURCE_PATH,
        conda_env_name=ENSEMBLEFIT_CONDA_ENV,
        tool_path=tool_path,
        vcf_path=vcf_path,
        reference_build=reference_build,
        scratch_path=scratch_path
    )
    return cmd


@bash_app
def SigProfilerAssignment(sample_path,
                          reference_path,
                          output_path,
                          strategy,
                          stdout=parsl.AUTO_LOGNAME,
                          stderr=parsl.AUTO_LOGNAME):
    tool_path = TOOLS_PATHS['SigProfilerAssignment']
    tool_output_path = os.path.join(output_path, 'SigProfilerAssignment')
    cmd = """
    source {conda_source_path}
    conda activate {conda_env_name}
    python {tool_path} {sample_path} {reference_path} {tool_output_path} {strategy}
    """.format(
        conda_source_path=CONDA_SOURCE_PATH,
        conda_env_name=ENSEMBLEFIT_CONDA_ENV,
        tool_path=tool_path,
        sample_path=sample_path,
        reference_path=reference_path,
        tool_output_path=tool_output_path,
        strategy=strategy
    )
    return cmd


@bash_app
def Sigminer(sample_path,
             reference_path,
             output_path,
             strategy,
             stdout=parsl.AUTO_LOGNAME,
             stderr=parsl.AUTO_LOGNAME):
    tool_path = TOOLS_PATHS['Sigminer']
    tool_output_path = os.path.join(output_path, 'Sigminer')
    cmd = """
    source {conda_source_path}
    conda activate {conda_env_name}
    Rscript {tool_path} {sample_path} {reference_path} {tool_output_path} {strategy}
    """.format(
        conda_source_path=CONDA_SOURCE_PATH,
        conda_env_name=ENSEMBLEFIT_CONDA_ENV,
        tool_path=tool_path,
        sample_path=sample_path,
        reference_path=reference_path,
        tool_output_path=tool_output_path,
        strategy=strategy
    )
    return cmd


@bash_app
def SignatureToolsLib(sample_path,
                      reference_path,
                      output_path,
                      strategy,
                      stdout=parsl.AUTO_LOGNAME,
                      stderr=parsl.AUTO_LOGNAME):
    tool_path = TOOLS_PATHS['SignatureToolsLib']
    tool_output_path = os.path.join(output_path, 'SignatureToolsLib')
    cmd = """
    source {conda_source_path}
    conda activate {conda_env_name}
    Rscript {tool_path} {sample_path} {reference_path} {tool_output_path} {strategy}
    """.format(
        conda_source_path=CONDA_SOURCE_PATH,
        conda_env_name=ENSEMBLEFIT_CONDA_ENV,
        tool_path=tool_path,
        sample_path=sample_path,
        reference_path=reference_path,
        tool_output_path=tool_output_path,
        strategy=strategy
    )
    return cmd


@bash_app
def MutationalPatterns(sample_path,
                       reference_path,
                       output_path,
                       strategy,
                       stdout=parsl.AUTO_LOGNAME,
                       stderr=parsl.AUTO_LOGNAME):
    tool_path = TOOLS_PATHS['MutationalPatterns']
    tool_output_path = os.path.join(output_path, 'MutationalPatterns')
    cmd = """
    source {conda_source_path}
    conda activate {conda_env_name}
    Rscript {tool_path} {sample_path} {reference_path} {tool_output_path} {strategy}
    """.format(
        conda_source_path=CONDA_SOURCE_PATH,
        conda_env_name=ENSEMBLEFIT_CONDA_ENV,
        tool_path=tool_path,
        sample_path=sample_path,
        reference_path=reference_path,
        tool_output_path=tool_output_path,
        strategy=strategy
    )
    return cmd


@bash_app
def MutSignatures(sample_path,
                  reference_path,
                  output_path,
                  strategy,
                  stdout=parsl.AUTO_LOGNAME,
                  stderr=parsl.AUTO_LOGNAME):
    tool_path = TOOLS_PATHS['MutSignatures']
    tool_output_path = os.path.join(output_path, 'MutSignatures')
    cmd = """
    source {conda_source_path}
    conda activate {conda_env_name}
    Rscript {tool_path} {sample_path} {reference_path} {tool_output_path} {strategy}
    """.format(
        conda_source_path=CONDA_SOURCE_PATH,
        conda_env_name=ENSEMBLEFIT_CONDA_ENV,
        tool_path=tool_path,
        sample_path=sample_path,
        reference_path=reference_path,
        tool_output_path=tool_output_path,
        strategy=strategy
    )
    return cmd


@bash_app
def SigFit(sample_path,
           reference_path,
           output_path,
           strategy,
           stdout=parsl.AUTO_LOGNAME,
           stderr=parsl.AUTO_LOGNAME):
    tool_path = TOOLS_PATHS['SigFit']
    tool_output_path = os.path.join(output_path, 'SigFit')
    cmd = """
    source {conda_source_path}
    conda activate {conda_env_name}
    Rscript {tool_path} {sample_path} {reference_path} {tool_output_path} {strategy}
    """.format(
        conda_source_path=CONDA_SOURCE_PATH,
        conda_env_name=ENSEMBLEFIT_CONDA_ENV,
        tool_path=tool_path,
        sample_path=sample_path,
        reference_path=reference_path,
        tool_output_path=tool_output_path,
        strategy=strategy
    )
    return cmd


@bash_app
def postprocess(sample_path,
                reference_path,
                output_path,
                strategy,
                tools,
                stdout=parsl.AUTO_LOGNAME,
                stderr=parsl.AUTO_LOGNAME):
    tool_path = TOOLS_PATHS['postprocess']
    tools_str = " ".join(tools)
    cmd = """
    source {conda_source_path}
    conda activate {conda_env_name}
    python {tool_path} {sample_path} {reference_path} {output_path} {strategy} {tools_str}
    """.format(
        conda_source_path=CONDA_SOURCE_PATH,
        conda_env_name=ENSEMBLEFIT_CONDA_ENV,
        tool_path=tool_path,
        sample_path=sample_path,
        reference_path=reference_path,
        output_path=output_path,
        tools_str=tools_str,
        strategy=strategy
    )
    return cmd


@bash_app
def generate_job_metadata(config_path,
                          sample_path,
                          output_path,
                          stdout=parsl.AUTO_LOGNAME,
                          stderr=parsl.AUTO_LOGNAME):
    tool_path = TOOLS_PATHS['generate_job_metadata']
    cmd = """
    source {conda_source_path}
    conda activate {conda_env_name}
    python {tool_path} {config_path} {sample_path} {output_path}
    """.format(
        conda_source_path=CONDA_SOURCE_PATH,
        conda_env_name=ENSEMBLEFIT_CONDA_ENV,
        tool_path=tool_path,
        config_path=config_path,
        sample_path=sample_path,
        output_path=output_path
    )
    return cmd


@bash_app
def finalize_workflow(*futures,
                      outputs=None,
                      stdout=parsl.AUTO_LOGNAME,
                      stderr=parsl.AUTO_LOGNAME):
    futures_str = ' '.join(['"{}"'.format(x) for x in futures])
    cmd = """
    printf "`date` futures: {futures_str} \\n"
    printf `date` > {complete_filepath}
    printf "`date` complete file created: {complete_filepath} \\n"
    """.format(
        futures_str=futures_str,
        complete_filepath=outputs[0]
    )
    return cmd


TOOLS_APPS = {
    'SigProfilerAssignment': SigProfilerAssignment,
    'Sigminer': Sigminer,
    'SignatureToolsLib': SignatureToolsLib,
    'MutationalPatterns': MutationalPatterns,
    'MutSignatures': MutSignatures,
    'SigFit': SigFit,
    'generate_matrix': generate_matrix,
    'postprocess': postprocess,
    'generate_job_metadata': generate_job_metadata
}
