#!/usr/bin/env python3
"""Map the hash-locked author master to the existing central script's schema.

This release utility is newly written; it is not the historical master generator.
It copies recorded values without refitting, rounding or changing chemistry.
"""
from pathlib import Path
import csv, hashlib

ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'endpoint_extension'/'Source_Reconstructed_Master_44.csv'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='e1804049d7e2819e8b1228eb55db81524caaa18cb6d4745000c20d3ce609d105'
mapping={'Sample':'Sample','Block':'StationNumber','SiteCode':'SiteCode','Side':'Side',
         'Distance_m':'Distance_numeric_m','Fine_LF':'Fine_LF_reconstructed',
         'Coarse_LF':'Coarse_LF_reconstructed','Fine_FD_pct':'Fine_FD_pct',
         'Coarse_FD_pct':'Coarse_FD_pct'}
mapping.update({f'{m}_mgkg':f'{m}_mgkg' for m in ['Fe','Zn','Cu','Cr','Co','Ni','Mn','Pb','Cd']})
with src.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
assert len(rows)==44
out=ROOT/'data'/'analysis_input.csv'
with out.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(mapping));w.writeheader()
    w.writerows({k:r[v] for k,v in mapping.items()} for r in rows)
print('Prepared 44 original rows in data/analysis_input.csv; paired exclusion is performed by the analysis.')
