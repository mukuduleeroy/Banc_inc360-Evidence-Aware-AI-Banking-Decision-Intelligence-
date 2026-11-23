"""Controlled local transaction CSV ingestion. Existing transformations/decisions are reused."""
from pathlib import Path
from datetime import datetime, timezone
from contextlib import contextmanager, redirect_stdout
import csv, io, json, hashlib, math, os, re, shutil, secrets, tempfile, zipfile, fcntl
import pandas as pd
from build_data import run as build_features, KNOWN_TYPES
from data_access import load_index, alias_key, policy_fingerprint, FEATURE_COLUMNS
from evidence import identifier, state, holdings, CUSTOMER_STATES, ACCOUNT_STATES, KYC_STATES
from segment_context import BANKING_SEGMENTS
from acceptance_checks import decision_fingerprint

ROOT=Path(__file__).resolve().parent
DEFAULT_STORAGE=ROOT/'outputs/phase9/private'
SOURCE_FIELDS=('Customer ID','Account ID','account_customer_id','Transaction ID','transaction_date','Type','Amount (USD)','dr_cr_indicator','products_held','customer_status','account_status','kyc_status','service_reasons','customer_segment')
MAX_BYTES=5*1024*1024
MAX_ROWS=25000
MAX_FIELD=2048
SCHEMA='phase9-transactions-usd-v1'
DISCLAIMER='These outcomes are generated using the existing prototype decision policy. They are not bank-approved outreach, credit or product decisions.'
TOKEN=re.compile(r'[a-f0-9]{32}')

class IngestionError(ValueError):
    """Messages are fixed operator guidance, never raw uploaded data or identifiers."""
    def __init__(self,code,message):self.code=code;super().__init__(message)

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(65536),b''):h.update(chunk)
    return h.hexdigest()

def utc():return datetime.now(timezone.utc).isoformat()
def _json(value):return json.dumps(value,sort_keys=True,allow_nan=False,separators=(',',':')).encode()
def _hash(value):return hashlib.sha256(value).hexdigest()

def _atomic(path,content):
    """Same-directory atomic state replacement, including fsync; only Phase 9 paths."""
    fd,name=tempfile.mkstemp(prefix='.pending-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(content);f.flush();os.fsync(f.fileno())
        os.replace(name,path)
    finally:
        if Path(name).exists():Path(name).unlink()

def validate_csv(path,cutoff):
    """Bounded source audit. No customer values are included in validation messages."""
    issues=[];warnings=[];counts={k:0 for k in ('invalid_types','invalid_dates','missing_identifiers','duplicate_records','conflicting_transaction_ids','ownership_errors','unsupported_currencies','invalid_numbers','missing_eligibility','missing_products','unknown_segments')}
    def fail(code,message,row=None):
        if len(issues)<50:issues.append({'code':code,'message':message,'row':row})
    def warn(code,message):
        if not any(x['code']==code for x in warnings):warnings.append({'code':code,'message':message})
    date=None
    if not isinstance(cutoff,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',cutoff):fail('OBSERVATION_DATE','Choose an explicit observation date in YYYY-MM-DD format.')
    else:
        try:
            date=pd.Timestamp(cutoff)
            if pd.isna(date) or date.tz is not None:raise ValueError()
        except (ValueError,TypeError):fail('OBSERVATION_DATE','Choose a valid observation date.');date=None
    rows=0;columns=[];missing=list(SOURCE_FIELDS);customers=set();accounts={};transactions={};historical=set();future_rows=0
    def _report():
        return {'valid':not issues,'schema':SCHEMA,'detected_columns':columns,'required_fields':list(SOURCE_FIELDS),'missing_fields':missing,'source_rows':rows,'accepted_unique_rows':rows-counts['duplicate_records'] if not issues else 0,'distinct_customers':len(customers),'distinct_accounts':len(accounts),'counts':counts,'errors':issues,'warnings':warnings,'cutoff':cutoff}
    try:
        path=Path(path)
        if path.stat().st_size>MAX_BYTES:raise IngestionError('FILE_SIZE','CSV exceeds the 5 MiB local demonstration limit.')
        with path.open('r',encoding='utf-8-sig',newline='') as stream:
            reader=csv.reader(stream,strict=True);columns=next(reader,[])
            missing=[c for c in SOURCE_FIELDS if c not in columns]
            if missing:fail('MISSING_FIELDS','Required source fields are missing.')
            if len(columns)!=len(set(columns)) or set(columns)-set((*SOURCE_FIELDS,'Currency')):fail('SCHEMA','Use the required fields and optional Currency field only, with unique column names.')
            if missing or any(i['code']=='SCHEMA' for i in issues):return _report()
            for values in reader:
                rows+=1
                if rows>MAX_ROWS:fail('ROW_LIMIT','CSV exceeds the 25,000-row demonstration limit.');break
                if len(values)!=len(columns) or any(len(v)>MAX_FIELD or '\x00' in v for v in values):fail('MALFORMED_CSV','A record has an invalid field count, oversized field or binary content.',rows+1);continue
                d=dict(zip(columns,values));rn=rows+1
                cid=d['Customer ID'];aid=d['Account ID'];tid=d['Transaction ID']
                if not all(identifier(d[k]) for k in ('Customer ID','Account ID','account_customer_id','Transaction ID')):
                    counts['missing_identifiers']+=1;fail('IDENTIFIERS','A required customer, account or transaction identifier is missing or invalid.',rn)
                customers.add(cid)
                if cid!=d['account_customer_id'] or (aid in accounts and accounts[aid]!=cid):counts['ownership_errors']+=1;fail('OWNERSHIP','Account ownership is inconsistent.',rn)
                accounts[aid]=cid
                raw=tuple(values)
                if tid in transactions:
                    if transactions[tid]==raw:counts['duplicate_records']+=1
                    else:counts['conflicting_transaction_ids']+=1;fail('DUPLICATE_CONFLICT','Repeated transaction IDs have different evidence.',rn)
                else:transactions[tid]=raw
                try:
                    dt=pd.to_datetime(d['transaction_date'],format='mixed',dayfirst=True,errors='raise')
                    if pd.isna(dt) or dt.tz is not None:raise ValueError()
                    if date is not None:
                        if dt<date:historical.add(cid)
                        else:future_rows+=1
                except (ValueError,TypeError,OverflowError):counts['invalid_dates']+=1;fail('INVALID_DATE','A transaction date is invalid or timezone-aware.',rn)
                if d['Type'].upper() not in KNOWN_TYPES:counts['invalid_types']+=1;fail('TRANSACTION_TYPE','A transaction type is unsupported by the existing builder.',rn)
                if d['dr_cr_indicator'] not in ('DR','CR'):counts['invalid_types']+=1;fail('DIRECTION','Use DR or CR for the debit/credit indicator.',rn)
                try:
                    value=float(d['Amount (USD)'])
                    if not math.isfinite(value) or abs(value)>1e12:raise ValueError()
                except (ValueError,TypeError,OverflowError):counts['invalid_numbers']+=1;fail('INVALID_AMOUNT','USD amounts must be finite numeric values within the demonstration limit.',rn)
                if 'Currency' in d and d['Currency']!='USD':counts['unsupported_currencies']+=1;fail('CURRENCY','This contract accepts already-normalized USD amounts only; no currency conversion is performed.',rn)
                for key,allowed in (('customer_status',CUSTOMER_STATES),('account_status',ACCOUNT_STATES),('kyc_status',KYC_STATES)):
                    if state(d[key],allowed) is None:
                        counts['missing_eligibility']+=1;warn('ELIGIBILITY_UNKNOWN','Missing or unknown status/KYC stays unknown and must abstain under the existing engine.')
                product=d['products_held']
                if not product.strip():counts['missing_products']+=1;warn('OWNERSHIP_UNKNOWN','Blank product ownership remains unknown and blocks supported offers.')
                elif holdings([p.strip() for p in product.split('|')]) is None:fail('PRODUCT_EVIDENCE','Product holdings must be pipe-separated existing catalogue labels.',rn)
                if not d['customer_segment'].strip():counts['unknown_segments']+=1;warn('SEGMENT_UNKNOWN','Blank source segment is displayed as Unknown; it does not determine eligibility.')
                elif d['customer_segment'].strip().casefold() not in {s.casefold() for s in BANKING_SEGMENTS}:fail('SEGMENT','Use an existing source banking segment or leave unknown.',rn)
                # Prevent hostile free text/formula payloads; neither service text nor IDs are displayed.
                if any(d[k].lstrip().startswith(('=','+','@')) for k in ('service_reasons','customer_segment')):fail('UNSAFE_TEXT','Formula-like metadata is not accepted.',rn)
        if not rows:fail('EMPTY','Upload at least one transaction record.')
        if date is not None and customers-historical:fail('NO_HISTORICAL_COHORT','Every uploaded customer must have a transaction strictly before the observation date; post-cutoff-only customers cannot be evaluated.')
        if future_rows:warn('POST_CUTOFF','Post-cutoff records are excluded from historical predictors; current snapshot fields follow the unchanged builder.')
        if counts['duplicate_records']:warn('EXACT_DUPLICATES','Exact repeated transaction records are reported and deduplicated by the existing builder; repeated customer IDs alone are valid.')
    except IngestionError as exc:fail(exc.code,str(exc))
    except (UnicodeError,csv.Error,OSError,ValueError,OverflowError):fail('MALFORMED_CSV','The file is not a readable, well-formed UTF-8 CSV.')
    return _report()

class SnapshotStore:
    """Private companion-only registry. No canonical data or existing database writes."""
    def __init__(self,root=DEFAULT_STORAGE):
        self.root=Path(root).absolute()
        if self.root.is_symlink() or self.root.resolve()!=self.root or self.root in (ROOT,ROOT/'outputs') or any(self.root==p.parent for p in [ROOT/'outputs/customer_features.csv']):
            raise IngestionError('STORAGE','Choose an isolated private Phase 9 storage folder.')
        if ROOT in self.root.parents and not self.root.is_relative_to(ROOT/'outputs/phase9'):
            raise IngestionError('STORAGE','Phase 9 storage must be outside accepted application directories.')
        marker=self.root/'.phase9-storage'
        if self.root.exists() and any(self.root.iterdir()) and (not marker.is_file() or marker.is_symlink() or marker.read_text()!='phase9-private-v1'):
            raise IngestionError('STORAGE','Refusing an existing directory that is not managed Phase 9 storage.')
        self.root.mkdir(parents=True,exist_ok=True,mode=0o700)
        if not marker.exists():
            with marker.open('x') as f:f.write('phase9-private-v1')
        for name in ('.alias_key','registry.lock'):
            if (self.root/name).is_symlink():raise IngestionError('STORAGE','Unsafe private storage configuration.')
        for name in ('staging','snapshots'):
            p=self.root/name
            if p.is_symlink():raise IngestionError('STORAGE','Phase 9 storage cannot use symlinks.')
            p.mkdir(exist_ok=True,mode=0o700)
        self.key=alias_key(self.root/'.alias_key')
        with self._lock():
            if not (self.root/'registry.json').exists() and not (self.root/'registry.previous.json').exists():
                self._save({'schema':1,'generation':0,'active':'baseline','snapshots':{},'events':[]},None)
            else:self._read()

    @contextmanager
    def _lock(self):
        with (self.root/'registry.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            try:yield
            finally:fcntl.flock(lock,fcntl.LOCK_UN)

    def _envelope(self,state):return _json({'payload':state,'sha256':_hash(_json(state))})
    def _decode(self,content):
        data=json.loads(content);s=data['payload']
        if data['sha256']!=_hash(_json(s)) or s['schema']!=1 or not isinstance(s['snapshots'],dict) or (s['active']!='baseline' and s['active'] not in s['snapshots']):raise ValueError()
        return s
    def _read(self):
        for name in ('registry.json','registry.previous.json'):
            p=self.root/name
            if p.is_symlink():raise IngestionError('STORAGE','Unsafe registry storage.')
            try:
                raw=p.read_bytes();s=self._decode(raw)
                if name!='registry.json':_atomic(self.root/'registry.json',raw)
                return s
            except (OSError,ValueError,KeyError,TypeError):continue
        raise IngestionError('REGISTRY','Registry is unreadable. Existing snapshots are retained; do not activate until the local receipt is recovered.')
    def _save(self,state,previous):
        if previous is not None:_atomic(self.root/'registry.previous.json',self._envelope(previous))
        _atomic(self.root/'registry.json',self._envelope(state))
    def state(self):
        with self._lock():return self._read()
    def _path(self,token,folder,suffix=''):
        if not isinstance(token,str) or not TOKEN.fullmatch(token):raise IngestionError('IDENTIFIER','Invalid Phase 9 identifier.')
        path=self.root/folder/(token+suffix)
        if path.is_symlink() or path.resolve()!=path:raise IngestionError('STORAGE','Unsafe Phase 9 artifact path.')
        return path

    def stage(self,filename,stream):
        if not isinstance(filename,str) or len(filename)>120 or '/' in filename or '\\' in filename or filename in ('.','..') or not filename.lower().endswith('.csv') or any(ord(c)<32 for c in filename):
            raise IngestionError('FILENAME','Upload a plain .csv filename without folders.')
        token=secrets.token_hex(16);p=self._path(token,'staging','.csv');size=0
        try:
            fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
            with os.fdopen(fd,'wb') as f:
                while True:
                    block=stream.read(65536)
                    if not block:break
                    size+=len(block)
                    if size>MAX_BYTES:raise IngestionError('FILE_SIZE','CSV exceeds the 5 MiB local demonstration limit.')
                    f.write(block)
            if not size:raise IngestionError('EMPTY','The uploaded CSV is empty.')
            record={'token':token,'filename':filename,'size_bytes':size,'sha256':digest(p),'uploaded_at':utc()}
            _atomic(self._path(token,'staging','.json'),_json(record));return record
        except BaseException:
            p.unlink(missing_ok=True);raise

    def _upload(self,token):
        try:
            record=json.loads(self._path(token,'staging','.json').read_bytes());p=self._path(token,'staging','.csv')
            if record['token']!=token or record['size_bytes']!=p.stat().st_size or record['sha256']!=digest(p):raise ValueError()
            return record,p
        except (OSError,KeyError,ValueError):raise IngestionError('UPLOAD_LINEAGE','Staged upload fingerprint does not match its receipt. Upload again.') from None
    def validate(self,token,cutoff):
        _,p=self._upload(token);return validate_csv(p,cutoff)
    def cleanup(self,token):
        # Only server-generated staging tokens; immutable snapshots are never deleted.
        for suffix in ('.csv','.json'):self._path(token,'staging',suffix).unlink(missing_ok=True)

    def process(self,token,cutoff):
        upload,source=self._upload(token);validation=validate_csv(source,cutoff)
        if not validation['valid']:raise IngestionError('VALIDATION','Validation failed. Correct the source evidence before processing.')
        snapshot_id=secrets.token_hex(16);destination=self._path(snapshot_id,'snapshots')
        work=Path(tempfile.mkdtemp(prefix='.candidate-',dir=self.root/'snapshots'))
        try:
            shutil.copyfile(source,work/'source.csv')
            if digest(work/'source.csv')!=upload['sha256']:raise IngestionError('UPLOAD_LINEAGE','Source changed during processing; no snapshot created.')
            with zipfile.ZipFile(work/'source.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
                info=zipfile.ZipInfo('transactions.csv',date_time=(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,(work/'source.csv').read_bytes())
            # Unchanged builder writes only into this brand-new private directory.
            with redirect_stdout(io.StringIO()):audit=build_features(work/'source.zip',work,cutoff)
            if any(audit[k] for k in ('invalid_links','invalid_dates','invalid_amounts','invalid_identifiers','unknown_transaction_types','ownership_conflict_customers','post_cutoff_only_customers_excluded')):
                raise IngestionError('RECONCILIATION','Source processing excluded evidence; no candidate can be activated.')
            index=load_index(work/'customer_features.csv',key=self.key)
            if index.lineage_issues or index.exclusions or len(index.records)!=validation['distinct_customers'] or index.input_rows!=len(index.records) or sum(index.counts.values())!=len(index.records) or not index.records or audit['duplicate_transaction_ids']!=validation['counts']['duplicate_records']:
                raise IngestionError('RECONCILIATION','Customer decisions or duplicate accounting do not reconcile; activation is blocked.')
            with (work/'customer_features.csv').open(newline='') as f:
                if next(csv.reader(f))!=list(FEATURE_COLUMNS):raise IngestionError('FEATURE_CONTRACT','Builder output differs from the accepted 16-column contract.')
            decisions=[{'customer':r.alias,'rating':r.rating,'priority':r.priority,'reason_codes':list(r.reason_codes),'invalid_evidence':r.invalid} for r in index.records]
            (work/'decisions.json').write_bytes(_json(decisions))
            reconciliation={'source_rows':validation['source_rows'],'accepted_source_rows':validation['accepted_unique_rows'],'duplicate_source_rows':validation['counts']['duplicate_records'],'quarantined_rows':0,'distinct_customers':validation['distinct_customers'],'distinct_accounts':validation['distinct_accounts'],'evaluated_customers':len(index.records),'counts':index.counts,'decision_coverage':1.0,'invalid_evidence_decisions':index.invalid_records,'missing_evidence':validation['counts']}
            files={p.name:digest(p) for p in work.iterdir() if p.is_file()}
            meta={'snapshot_id':snapshot_id,'schema':SCHEMA,'source_sha256':upload['sha256'],'source_zip_sha256':digest(work/'source.zip'),'policy_sha256':index.policy_hash,'dataset_sha256':index.dataset_hash,'observation_date':cutoff,'created_at':utc(),'validation_status':'VALIDATED','validation':validation,'reconciliation':reconciliation,'decision_fingerprint':decision_fingerprint(index),'feature_columns':list(FEATURE_COLUMNS),'processing_provenance':{name:digest(ROOT/name) for name in ('build_data.py','data_access.py','engine.py','evidence.py','phase9_ingestion.py')},'files':files,'disclaimer':DISCLAIMER}
            (work/'snapshot.json').write_bytes(_json(meta))
            for p in work.iterdir():p.chmod(0o600)
            os.rename(work,destination)
            with self._lock():
                old=self._read();new=json.loads(json.dumps(old));new['snapshots'][snapshot_id]=digest(destination/'snapshot.json');new['generation']+=1;new['events'].append({'action':'CREATE','snapshot':snapshot_id,'at':utc()});self._save(new,old)
            self.cleanup(token)
            return meta
        except IngestionError:raise
        except (OSError,ValueError,KeyError,TypeError,OverflowError):raise IngestionError('PROCESSING','Processing could not complete safely. Prior selection is retained; inspect the controlled local source contract.') from None
        finally:
            if work.exists():shutil.rmtree(work)

    def _verify(self,snapshot_id,state):
        path=self._path(snapshot_id,'snapshots')
        try:
            meta_path=path/'snapshot.json'
            if meta_path.is_symlink() or digest(meta_path)!=state['snapshots'][snapshot_id]:raise ValueError()
            meta=json.loads(meta_path.read_bytes())
            if meta['snapshot_id']!=snapshot_id or meta['schema']!=SCHEMA or meta['validation_status']!='VALIDATED' or meta['feature_columns']!=list(FEATURE_COLUMNS) or meta['policy_sha256']!=policy_fingerprint():raise ValueError()
            required={'source.csv','source.zip','customer_features.csv','customer_features.manifest.json','data_audit.json','decisions.json'}
            if set(meta['files'])!=required:raise ValueError()
            for name,h in meta['files'].items():
                if (path/name).is_symlink() or digest(path/name)!=h:raise ValueError()
            if meta['source_sha256']!=digest(path/'source.csv') or meta['source_zip_sha256']!=digest(path/'source.zip'):raise ValueError()
            manifest=json.loads((path/'customer_features.manifest.json').read_bytes())
            if manifest['source_sha256']!=meta['source_zip_sha256'] or manifest['feature_sha256']!=meta['dataset_sha256'] or manifest['cutoff']!=meta['observation_date']:raise ValueError()
            for name,h in meta['processing_provenance'].items():
                if name not in ('build_data.py','data_access.py','engine.py','evidence.py','phase9_ingestion.py') or digest(ROOT/name)!=h:raise ValueError()
            ix=load_index(path/'customer_features.csv',key=self.key);r=meta['reconciliation']
            if ix.lineage_issues or ix.exclusions or ix.dataset_hash!=meta['dataset_sha256'] or ix.counts!=r['counts'] or sum(ix.counts.values())!=r['evaluated_customers'] or len(ix.records)!=r['distinct_customers'] or r['decision_coverage']!=1.0 or decision_fingerprint(ix)!=meta['decision_fingerprint']:raise ValueError()
            expected=[{'customer':v.alias,'rating':v.rating,'priority':v.priority,'reason_codes':list(v.reason_codes),'invalid_evidence':v.invalid} for v in ix.records]
            if json.loads((path/'decisions.json').read_bytes())!=expected:raise ValueError()
            return meta,ix
        except (OSError,ValueError,KeyError,TypeError):raise IngestionError('SNAPSHOT_INTEGRITY','Snapshot provenance, policy or reconciliation no longer verifies. Activation is blocked; return to the accepted baseline.') from None

    def inspect(self,snapshot_id):
        with self._lock():return self._verify(snapshot_id,self._read())
    def activate(self,snapshot_id):
        with self._lock():
            old=self._read();self._verify(snapshot_id,old)
            new=json.loads(json.dumps(old));new['active']=snapshot_id;new['generation']+=1;new['events'].append({'action':'ACTIVATE','snapshot':snapshot_id,'at':utc()});self._save(new,old)
    def rollback(self):
        with self._lock():
            old=self._read();new=json.loads(json.dumps(old));new['active']='baseline';new['generation']+=1;new['events'].append({'action':'ROLLBACK_BASELINE','at':utc()});self._save(new,old)
