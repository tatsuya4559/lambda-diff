import os
import subprocess
import tempfile
import zipfile

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
    dirname = os.path.dirname(filepath)
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(dirname)
    os.remove(filepath)


def get_src_code(func_name, version, dirname):
    resp = client.get_function(FunctionName=func_name, Qualifier=version)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    filepath = os.path.join(dirname, f'{func_name}.zip')
    download_file(resp['Code']['Location'], filepath)
    unzip_file(filepath)


@click.command()
@click.argument('func_name')
@click.option('-b', '--base', default='$LATEST', help='base version')
@click.option('-h', '--head', default='$LATEST', help='head version')
@click.option('-w', '--web', default=False, is_flag=True, help='show diff in browser')
@click.option('-s', '--style', default='line', help='diff style',
        type=click.Choice(['line', 'side'], case_sensitive=False))
def diff(func_name, base, head, web, style):
    '''
    Example:
        $ python main.py lambdaFunctionName --base 2 --head 3
    '''
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = os.path.join(tmpdir, 'base')
        head_dir = os.path.join(tmpdir, 'head')
        get_src_code(func_name, base, base_dir)
        get_src_code(func_name, head, head_dir)

        if web:
            p1 = subprocess.Popen(['git', 'diff', base_dir, head_dir], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(['diff2html', '-i', 'stdin', '--style', style], stdin=p1.stdout)
            p1.stdout.close()
            p2.communicate()
        else:
            subprocess.run(['git', 'diff', base_dir, head_dir])


if __name__ == '__main__':
    diff()
