import os
import shutil
import subprocess
import zipfile
from glob import glob

import boto3
import click
import requests

client = boto3.client('lambda')

def download_file(url, filepath):
    '''
    download file from {url} and save as {filepath}
    '''
    resp = requests.get(url)
    with open(filepath, 'wb') as fp:
        fp.write(resp.content)

def unzip_file(filepath):
    '''
    Args:
        filepath: filepath of zipfile to extract
    Returns:
        path list of extracted files
    '''
    dirname, _ = os.path.splitext(filepath)
    if not os.path.exists(dirname):
        os.mkdir(dirname)

    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(dirname)
    os.remove(filepath)
    # return glob(os.path.join(dirname, '*'))
    return dirname

def get_src_code(func_name, version, base_or_head):
    resp = client.get_function(FunctionName=func_name, Qualifier=version)
    filepath = f'/tmp/{base_or_head}.zip'
    download_file(resp['Code']['Location'], filepath)
    src_dir = unzip_file(filepath)
    print(src_dir)
    return src_dir

@click.command()
@click.option('--base', default='$LATEST', help='base version')
@click.option('--head', default='$LATEST', help='head version')
@click.argument('func_name')
def diff(base, head, func_name):
    '''
    Example:
        $ python main.py execBBTOReportBatch --base 2 --head 3
    '''
    base_dir = get_src_code(func_name, base, 'base')
    head_dir = get_src_code(func_name, head, 'head')
    subprocess.run(['git', 'diff', base_dir, head_dir])
    shutil.rmtree(base_dir)
    shutil.rmtree(head_dir)


if __name__ == '__main__':
    diff()