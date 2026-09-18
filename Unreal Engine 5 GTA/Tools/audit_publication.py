"""Scan a publication tree without printing matched secret values.
Complements gitleaks; checks filenames, common credentials and personal path metadata.
"""
from pathlib import Path
import argparse, re, sys, json
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('directory', type=Path)
args=parser.parse_args()
patterns={
 'github_token':rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})',
 'private_key':rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
 'service_token':rb'(?im)^SecurityToken\s*=\s*[^\s#;]+',
 'openai_key':rb'sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{40,}',
 'aws_access_key':rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
 'home_path':rb'(?i)(?:[A-Z]:[/\\]Users[/\\](?!Public(?:[/\\]|$)|Shared(?:[/\\]|$)|<)[A-Za-z0-9_.-]+|/Users/(?!Shared/)[A-Za-z0-9_.-]+/)',
 'private_session':rb'(?i)\.codex[/\\]sessions[/\\]'
}
# Source is itself a scanner: patterns are regex expressions, never real credentials.
forbidden_dirs={'.astra-run','.codex','.vs','.idea','.vscode','Saved','Intermediate','DerivedDataCache'}
forbidden_ext={'.pdb','.p12','.pfx','.pem','.key','.log'}
findings=[];files=0
for path in args.directory.rglob('*'):
 rel=path.relative_to(args.directory)
 if '.git' in rel.parts or not path.is_file(): continue
 files+=1
 if any(part in forbidden_dirs for part in rel.parts) or path.suffix.lower() in forbidden_ext or path.name=='.env':
  findings.append({'file':rel.as_posix(),'rule':'private_artifact'})
 data=path.read_bytes().replace(b'\x00',b'')
 for rule,pattern in patterns.items():
  if re.search(pattern,data):findings.append({'file':rel.as_posix(),'rule':rule})
print(json.dumps({'files_checked':files,'findings':findings},indent=2))
sys.exit(bool(findings))
