#!/usr/bin/env python3
"""Replay the original endpoint extension in isolation and verify its 12 CSV outputs.

Example:
  python verification/verify_reproduction.py endpoint_extension \
      --report verification/reproduction_check.json

The author directory must contain the original three Python scripts, workbook,
master CSV and saved output CSVs. If snapshots are stored separately, supply
--expected-dir. No author code is changed and the supplied directory is read-only.
"""
from __future__ import annotations
import argparse
import csv
import datetime
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time

INPUT_HASHES = {
    '04_M-Ghraam2026_ORIGINAL_UNCHANGED.xlsx':
        '4ff48393b15d83306e9099efa30e12ee2d797cd57a0b75c44b8f99726380becb',
    'Source_Reconstructed_Master_44.csv':
        'e1804049d7e2819e8b1228eb55db81524caaa18cb6d4745000c20d3ce609d105',
}
SCRIPTS = ('run_all.py', 'source_trace_audit.py', 'run_extension.py')
OUTPUTS = (
    'Source_to_Extension_Audit.csv',
    'Fixed_FD.csv', 'Fixed_logHF.csv',
    'Selector_OuterPairs.csv', 'Selector_Summary.csv',
    'DeleteBlock_ByDeletion.csv', 'DeleteBlock_Robustness.csv',
    'Selection_Counts.csv', 'Representation_Selection_Stability.csv',
    'Fixed_Representation_Sensitivity.csv', 'Representation_Conditioning.csv',
    'Reproduction_Anchor_Differences.csv',
)
ABS_TOL = REL_TOL = 1e-12


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def csv_rows(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        data = list(reader)
    if not fields or len(fields) != len(set(fields)):
        raise ValueError(f'{path.name}: missing or duplicate CSV header')
    if any(None in row or any(v is None for v in row.values()) for row in data):
        raise ValueError(f'{path.name}: inconsistent CSV row width')
    return fields, data


def compare_csv(expected: Path, actual: Path):
    columns_e, rows_e = csv_rows(expected)
    columns_a, rows_a = csv_rows(actual)
    result = {
        'file': expected.name, 'expected_rows': len(rows_e),
        'actual_rows': len(rows_a), 'columns_match': columns_e == columns_a,
        'numeric_cells': 0, 'categorical_cells': 0,
        'maximum_absolute_numeric_difference': 0.0,
        'expected_sha256': sha256(expected), 'actual_sha256': sha256(actual),
        'mismatch_count': 0, 'mismatches': [],
    }
    if columns_e != columns_a or len(rows_e) != len(rows_a):
        result['pass'] = False
        return result
    for row_number, (e, a) in enumerate(zip(rows_e, rows_a), 1):
        for key in columns_e:
            expected_value, actual_value = e[key], a[key]
            try:
                x, y = float(expected_value), float(actual_value)
            except ValueError:
                result['categorical_cells'] += 1
                same = expected_value == actual_value
                difference = None
            else:
                result['numeric_cells'] += 1
                finite = math.isfinite(x) and math.isfinite(y)
                difference = abs(x - y) if finite else None
                same = finite and math.isclose(x, y, rel_tol=REL_TOL, abs_tol=ABS_TOL)
                if finite:
                    result['maximum_absolute_numeric_difference'] = max(
                        result['maximum_absolute_numeric_difference'], difference)
            if not same:
                result['mismatch_count'] += 1
                if len(result['mismatches']) < 50:
                    result['mismatches'].append({
                        'row': row_number, 'column': key,
                        'expected': expected_value, 'actual': actual_value,
                        'absolute_difference': difference,
                    })
    result['pass'] = result['mismatch_count'] == 0
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('author_directory', type=Path)
    parser.add_argument('--expected-dir', type=Path,
                        help='Saved author CSV snapshots; defaults to author_directory')
    parser.add_argument('--report', type=Path, default=Path('reproduction_check.json'))
    args = parser.parse_args()
    author = args.author_directory.resolve()
    expected = (args.expected_dir or author).resolve()
    report = args.report.resolve()
    if report.is_relative_to(author) or report.is_relative_to(expected):
        parser.error('Write the verification report outside the input/snapshot directories.')
    needed = [author / n for n in (*SCRIPTS, *INPUT_HASHES)]
    needed += [expected / n for n in OUTPUTS]
    missing = [p.name for p in needed if not p.is_file()]
    if missing:
        parser.error('Missing required files: ' + ', '.join(missing))
    before = {p: sha256(p) for p in needed}
    for name, digest in INPUT_HASHES.items():
        if before[author / name] != digest:
            parser.error(f'Source checksum mismatch: {name}')
    result = {
        'status': 'FAIL',
        'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'environment': {
            'python': platform.python_version(), 'platform': platform.system(),
            'numpy': importlib.metadata.version('numpy'),
            'openpyxl': importlib.metadata.version('openpyxl'),
        },
        'source_hashes': dict(INPUT_HASHES),
        'script_hashes': {n: before[author / n] for n in SCRIPTS},
        'numeric_absolute_tolerance': ABS_TOL,
        'numeric_relative_tolerance': REL_TOL,
        'categorical_comparison': 'exact',
        'command': ['python', 'run_all.py'],
    }
    start = time.perf_counter()
    # Only this newly created temporary directory receives generated outputs.
    with tempfile.TemporaryDirectory(prefix='magnetic-screening-replay-') as tmp:
        work = Path(tmp).resolve()
        for name in (*SCRIPTS, *INPUT_HASHES):
            shutil.copy2(author / name, work / name)
        try:
            completed = subprocess.run(
                [sys.executable, 'run_all.py'], cwd=work,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                encoding='utf-8', errors='replace', check=False,
            )
            result['author_exit_code'] = completed.returncode
            # Avoid retaining local paths should a traceback occur.
            result['author_stdout'] = completed.stdout.replace(str(work), '<replay>')
            result['elapsed_seconds'] = time.perf_counter() - start
            result['csv_comparisons'] = []
            if completed.returncode == 0:
                for name in OUTPUTS:
                    actual = work / name
                    if not actual.is_file():
                        result['csv_comparisons'].append({'file': name, 'pass': False,
                                                         'error': 'output missing'})
                    else:
                        result['csv_comparisons'].append(compare_csv(expected / name, actual))
            result['supplied_files_unchanged'] = all(sha256(p) == h for p, h in before.items())
            comparisons = result['csv_comparisons']
            passed = (completed.returncode == 0 and len(comparisons) == len(OUTPUTS)
                      and all(c['pass'] for c in comparisons)
                      and result['supplied_files_unchanged'])
            result['status'] = 'PASS' if passed else 'FAIL'
        except Exception as error:
            result['error'] = f'{type(error).__name__}: {error}'.replace(str(work), '<replay>')
            result['elapsed_seconds'] = time.perf_counter() - start
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    numeric_cells = sum(c.get('numeric_cells', 0) for c in result.get('csv_comparisons', []))
    print(f"{result['status']}: {len(result.get('csv_comparisons', []))}/12 CSV outputs; "
          f"{numeric_cells} numerical cells compared. Report: {args.report.name}")
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
