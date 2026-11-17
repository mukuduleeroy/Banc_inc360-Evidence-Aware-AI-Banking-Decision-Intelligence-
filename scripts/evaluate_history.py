"""Reproduce offline evaluation without changing application data or approvals."""
from pathlib import Path
import sys,argparse,os
# Explicit single-worker discovery avoids sandbox-blocked physical CPU probes.
os.environ.setdefault("LOKY_MAX_CPU_COUNT","1")
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from historical_evaluation import run
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--zip',required=True);p.add_argument('--out',required=True);p.add_argument('--audit-only',action='store_true');p.add_argument('--bootstrap-repeats',type=int,default=200);a=p.parse_args()
 if a.bootstrap_repeats<0:p.error('bootstrap repeats must be nonnegative')
 run(a.zip,a.out,a.audit_only,a.bootstrap_repeats)
