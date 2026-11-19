"""Mandatory final local acceptance: run all tests, freeze evidence and reject source drift."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from acceptance_checks import source_snapshot,sha256
from verify_final_acceptance import verify

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out-dir',required=True);a=p.parse_args();out=Path(a.out_dir).resolve()
 if out.exists():raise FileExistsError('Choose a new run directory. Historical acceptance evidence is never overwritten.')
 out.mkdir(parents=True);before=source_snapshot();started=datetime.now(timezone.utc).isoformat();junit=out/'tests.xml'
 with (out/'test_execution.log').open('w') as log:
  completed=subprocess.run([sys.executable,'-m','pytest','-v','-ra','--junitxml='+str(junit)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 after=source_snapshot();passed=completed.returncode==0 and before==after and junit.is_file()
 report={'status':'PASS' if passed else 'FAIL','pytest_exit_code':completed.returncode,'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'before_source_hashes':before,'after_source_hashes':after,'junit_sha256':sha256(junit) if junit.exists() else None,'command':[sys.executable,'-m','pytest','-v','-ra','--junitxml='+str(junit)]};manifest=out/'run_manifest.json';manifest.write_text(json.dumps(report,indent=2))
 if not passed:print(json.dumps({'status':'FAIL','acceptance_granted':False,'reason':'Tests failed or sources changed during the run; inspect test_execution.log.'}));raise SystemExit(1)
 try:verify(junit,out/'acceptance.json',run_manifest=manifest)
 except (AssertionError,OSError,ValueError) as exc:
  print(json.dumps({'status':'FAIL','acceptance_granted':False,'reason':str(exc)}));raise SystemExit(1)
