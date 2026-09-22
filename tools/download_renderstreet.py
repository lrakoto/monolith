"""Download a finished RenderStreet job over verified FTPS directly to Hitch.

One-time credential setup, run interactively in Terminal (password stays out of shell history):
  security add-generic-password -a lova@threeohfivestudios.com -s monolith-renderstreet-ftps -w
Then list remote jobs:
  python3 tools/download_renderstreet.py --list
Download one job:
  python3 tools/download_renderstreet.py --job 2856378
"""
import argparse
import ftplib
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import ssl
import subprocess

HOST='us3.render.st'
PORT=51225
ACCOUNT='lova@threeohfivestudios.com'
SERVICE='monolith-renderstreet-ftps'
ROOT=Path('/Volumes/Hitch_07/Blender/Data/cloud-renders/renderstreet')


def keychain_password():
    result=subprocess.run(['security','find-generic-password','-a',ACCOUNT,'-s',SERVICE,'-w'],capture_output=True,text=True)
    if result.returncode:
        raise RuntimeError('RenderStreet credential is not available in macOS Keychain. Complete the one-time setup in this script docstring.')
    return result.stdout.rstrip('\n')


def safe_name(name):
    if name in ('','.','..') or '/' in name or '\\' in name:
        raise ValueError('Unsafe remote filename')
    return name


def download_tree(ftp, remote, local, records):
    local.mkdir(parents=True,exist_ok=True)
    for name,facts in ftp.mlsd(remote):
        if facts.get('type') in ('cdir','pdir'):continue
        safe_name(name)
        path=str(PurePosixPath(remote)/name)
        target=local/name
        if target.is_symlink():raise RuntimeError('Refusing local symlink')
        if facts.get('type')=='dir':
            download_tree(ftp,path,target,records);continue
        if facts.get('type')!='file':continue
        expected=int(facts['size']) if 'size' in facts else ftp.size(path)
        if target.exists():
            raise RuntimeError(f'Output already exists; leaving it unchanged: {target}')
        partial=target.with_name(target.name+'.partial')
        with partial.open('xb') as output:
            ftp.retrbinary('RETR '+path,output.write)
        if expected is not None and partial.stat().st_size!=expected:
            raise RuntimeError(f'Incomplete download retained at {partial}')
        partial.rename(target)
        records.append({'file':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
        print('Saved',target,flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list',action='store_true')
    group.add_argument('--job',type=int)
    args=parser.parse_args()
    if not ROOT.is_dir():raise RuntimeError('Hitch render directory is unavailable; mount the drive first.')
    password=keychain_password()
    ftp=ftplib.FTP_TLS(context=ssl.create_default_context(),timeout=45)
    try:
        ftp.connect(HOST,PORT);ftp.login(ACCOUNT,password);password=None
        ftp.prot_p();ftp.voidcmd('TYPE I')
        jobs=[(name,facts) for name,facts in ftp.mlsd('/output-renders') if facts.get('type')=='dir']
        if args.list:
            for name,_ in jobs:print(name)
            return
        matches=[name for name,_ in jobs if re.search(r'(?<!\d)'+str(args.job)+r'(?!\d)',name)]
        if len(matches)!=1:raise RuntimeError(f'Expected exactly one folder matching job {args.job}; found {len(matches)}. Use --list to inspect.')
        target=ROOT/str(args.job)
        if target.is_symlink():raise RuntimeError('Refusing local symlink')
        records=[]
        download_tree(ftp,'/output-renders/'+safe_name(matches[0]),target,records)
        if not records:raise RuntimeError('No output files were downloaded.')
        manifest=target/'download-manifest.json'
        with manifest.open('x') as output:json.dump({'job':args.job,'transport':'FTPS','host':HOST,'files':records},output,indent=2)
    finally:
        ftp.close()


if __name__=='__main__':main()
