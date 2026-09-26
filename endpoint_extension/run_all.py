#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
EXPECTED={
 '04_M-Ghraam2026_ORIGINAL_UNCHANGED.xlsx':'4ff48393b15d83306e9099efa30e12ee2d797cd57a0b75c44b8f99726380becb',
 'Source_Reconstructed_Master_44.csv':'e1804049d7e2819e8b1228eb55db81524caaa18cb6d4745000c20d3ce609d105',
}
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
for name,h in EXPECTED.items():
 p=ROOT/name
 if not p.exists() or sha(p)!=h: raise SystemExit(f'FAIL source hash: {name}')
subprocess.run([sys.executable,str(ROOT/'source_trace_audit.py')],check=True)
subprocess.run([sys.executable,str(ROOT/'run_extension.py')],check=True)
# Fail-closed scientific invariants used in the manuscript.
with open(ROOT/'Selector_Summary.csv',encoding='utf-8-sig') as f: ss=list(csv.DictReader(f))
with open(ROOT/'DeleteBlock_Robustness.csv',encoding='utf-8-sig') as f: rr=list(csv.DictReader(f))
def one(rows,rep,metal): return next(r for r in rows if r['Representation']==rep and r['Metal']==metal)
mn=one(ss,'FD','Mn'); cu=one(ss,'FD','Cu'); mnr=one(rr,'FD','Mn'); cur=one(rr,'FD','Cu')
assert float(mn['Mean_Delta_Recall'])>0.12 and float(cu['Mean_Delta_Recall'])<-0.09
assert int(mnr['Positive_Deletes'])==10 and int(cur['Negative_Deletes'])==10
with open(ROOT/'Reproduction_Anchor_Differences.csv',encoding='utf-8-sig') as f: aa=list(csv.DictReader(f))
assert max(float(r['Absolute_Difference']) for r in aa) < 1e-12
print('PASS run_all: source trace, reproduction gate, selector extension, representation sensitivity, and key invariants')
