"""Human-review boundary: fresh real evidence only, explicit attribution, transactional events."""
from dataclasses import dataclass
from pathlib import Path
import hashlib,json,re,sqlite3,uuid
from audit_store import AuditStore,AuditError,utc_now
from data_access import load_index,manifest_path,policy_fingerprint,FeatureValidationError
from evidence import number,state,CUSTOMER_STATES,ACCOUNT_STATES,KYC_STATES
from evidence_trace import references

RUNTIME_POLICY_HASH=policy_fingerprint()
ACTION_STATE={'APPROVE':'APPROVED_LOCAL','DEFER':'DEFERRED','REJECT':'REJECTED'}

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)
def digest(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def file_digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def new_id(prefix):return prefix+'-'+uuid.uuid4().hex

def normalize_passport(passport,alias,dataset_hash,manifest_hash,policy_hash,source_hash,cutoff):
    if passport.get('simulated') or passport.get('action_authorized') is False:
        raise AuditError('SIMULATION_FORBIDDEN','Simulated evidence cannot create a real review case or audit approval.')
    if not re.fullmatch(r'C-[A-F0-9]{24}',alias or '') or passport.get('customer_id')!=alias:
        raise AuditError('INVALID_CASE_IDENTITY','A unique presentation-safe customer reference is required.')
    if any(not isinstance(v,str) or not re.fullmatch(r'[a-f0-9]{64}',v) for v in (dataset_hash,manifest_hash,policy_hash)) or (source_hash is not None and (not isinstance(source_hash,str) or not re.fullmatch(r'[a-f0-9]{64}',source_hash))):
        raise AuditError('INVALID_FINGERPRINT','Verified dataset, manifest and policy fingerprints are required.')
    if not isinstance(passport.get('policy_version'),str) or not passport['policy_version']:
        raise AuditError('INVALID_PASSPORT','Method policy version is unavailable.')
    gates=passport.get('gates',[])
    if len(gates)!=6 or [g.get('gate','').split()[0] for g in gates]!=['G1','G2','G3','G4','G5','G6']:
        raise AuditError('INVALID_PASSPORT','A complete six-gate passport is required.')
    clean=[]
    for gate in gates:
        codes=gate.get('reason_codes')
        if gate.get('status') not in {'PASS','CAUTION','ABSTAIN'} or not isinstance(codes,list) or not codes or any(not re.fullmatch(r'[A-Z0-9_]+',c) for c in codes):
            raise AuditError('INVALID_PASSPORT','Gate status or reason codes are invalid.')
        clean.append({'gate':gate['gate'],'status':gate['status'],'reason_codes':codes,'explanation':gate['reason']})
    expected='ABSTAIN' if any(g['status']=='ABSTAIN' for g in clean) else 'CAUTION' if any(g['status']=='CAUTION' for g in clean) else 'SUPPORTED'
    if passport.get('rating')!=expected or passport.get('human_review_required') is not True:
        raise AuditError('INVALID_PASSPORT','Passport outcome/control evidence is inconsistent.')
    evidence=passport.get('evidence',{});original=evidence.get('original_values',{})
    summary={'recency_days':number(evidence.get('recency_days'),integer=True),'events_180d':number(evidence.get('events_180d'),integer=True),'relationship_activity_percentile':number(evidence.get('relationship_activity_percentile'),maximum=1),'product_gap':evidence.get('product_gap') if type(evidence.get('product_gap')) is bool else None,'proposed_product':'Savings Account' if evidence.get('product')=='Savings Account' else None,'behavioural_rationale_recorded':isinstance(evidence.get('behavioural_reason'),str) and bool(evidence['behavioural_reason'].strip()),'customer_status':state(original.get('customer_status'),CUSTOMER_STATES),'account_status':state(original.get('account_status'),ACCOUNT_STATES),'kyc_status':state(original.get('kyc_status'),KYC_STATES),'snapshot_effective_date':None}
    return {'customer_ref':alias,'outcome':expected,'gates':clean,'evidence_summary':summary,'method':{'name':'deterministic_rules','policy_version':passport['policy_version'],'policy_sha256':policy_hash,'human_review_required':True},'dataset':{'feature_sha256':dataset_hash,'manifest_sha256':manifest_hash,'source_sha256':source_hash,'cutoff':cutoff},'traceability_level':'FEATURE_LEVEL','source_event_references':[],'simulation':False,'bank_authorization':False,'automatic_outreach':False}

@dataclass(frozen=True)
class CurrentEvidence:
    alias:str
    passport:dict
    dataset_hash:str
    manifest_hash:str
    policy_hash:str
    source_hash:str
    cutoff:str

    @property
    def policy_version(self):return self.passport['policy_version']
    @property
    def dataset_version_id(self):return digest([self.dataset_hash,self.manifest_hash])
    @property
    def payload(self):return normalize_passport(self.passport,self.alias,self.dataset_hash,self.manifest_hash,self.policy_hash,self.source_hash,self.cutoff)
    @property
    def decision_hash(self):return digest(self.payload)

class ReviewService:
    def __init__(self,store,features_path=None,provider=None):
        self.store=store
        self.features_path=Path(features_path) if features_path is not None else None
        self.provider=provider
        if provider is None and self.features_path is None:raise ValueError('Feature source is required.')

    def current(self,alias):
        if self.provider is not None:
            context=self.provider(alias)
            if context.alias!=alias:raise AuditError('IDENTITY_MISMATCH','Current evidence does not match the requested presentation reference.')
            context.payload # Validate even injected trusted test adapters.
            return context
        if policy_fingerprint()!=RUNTIME_POLICY_HASH:
            raise AuditError('POLICY_RELOAD_REQUIRED','Policy files changed; reload the application before refreshing or reviewing cases.')
        try:
            index=load_index(self.features_path)
            if index.lineage_issues:raise AuditError('UNVERIFIED_CURRENT_EVIDENCE','Current source provenance is invalid. Refresh the source before recording reviews.')
            p=index.passport(alias)
            raw=manifest_path(self.features_path).read_bytes();manifest=json.loads(raw)
            context=CurrentEvidence(alias,p,index.dataset_hash,hashlib.sha256(raw).hexdigest(),index.policy_hash,manifest.get('source_sha256'),index.cutoff)
            if file_digest(self.features_path)!=index.dataset_hash:raise AuditError('EVIDENCE_CHANGED_DURING_READ','Dataset changed during validation; reload and inspect again.')
            context.payload
            return context
        except (OSError,ValueError,StopIteration) as exc:
            if isinstance(exc,AuditError):raise
            raise AuditError('CURRENT_EVIDENCE_UNAVAILABLE','Current customer evidence cannot be verified; no review action was recorded.') from None

    def _assert_still_current(self,context):
        if self.provider:
            fresh=self.current(context.alias)
            same=(fresh.dataset_hash,fresh.manifest_hash,fresh.policy_hash,fresh.policy_version,fresh.decision_hash)==(context.dataset_hash,context.manifest_hash,context.policy_hash,context.policy_version,context.decision_hash)
        else:
            try:same=file_digest(self.features_path)==context.dataset_hash and file_digest(manifest_path(self.features_path))==context.manifest_hash and policy_fingerprint()==context.policy_hash
            except OSError:same=False
        if not same:raise AuditError('STALE_EVIDENCE','Evidence changed before commit. No review was saved; refresh and inspect again.')

    def _fresh_case(self,case,context):
        if (case['customer_ref'],case['dataset_hash'],case['manifest_hash'],case['policy_hash'],case['policy_version'],case['decision_hash'])!=(context.alias,context.dataset_hash,context.manifest_hash,context.policy_hash,context.policy_version,context.decision_hash):
            raise AuditError('STALE_EVIDENCE','Case evidence is stale or mismatched. Refresh the case and inspect the new passport before reviewing.')

    def _reviewer(self,con,reviewer_id):
        if not reviewer_id or not con.execute('SELECT 1 FROM reviewers WHERE reviewer_id=?',(reviewer_id,)).fetchone():
            raise AuditError('REVIEWER_REQUIRED','Select an explicit unverified demonstration reviewer; credentials are not requested.')

    def _reason(self,reason):
        if not isinstance(reason,str) or not 1<=len(reason.strip())<=2000:
            raise AuditError('REASON_REQUIRED','A review reason of 1–2000 characters is required. Avoid personal data or credentials.')
        return reason.strip()

    def _request(self,request_id):
        if not isinstance(request_id,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}',request_id):
            raise AuditError('INVALID_REQUEST_ID','A valid idempotency token is required.')

    def _run_write(self,operation):
        try:
            with self.store.transaction() as con:return operation(con)
        except sqlite3.Error:
            raise AuditError('AUDIT_WRITE_FAILED','Audit transaction failed and was rolled back; no success is recorded. Retry after checking storage.') from None

    def _snapshot(self,con,context,now):
        con.execute('INSERT OR IGNORE INTO datasets VALUES(?,?,?,?,?,?)',(context.dataset_version_id,context.dataset_hash,context.manifest_hash,context.source_hash,context.cutoff,now))
        con.execute('INSERT OR IGNORE INTO policies VALUES(?,?,?,?)',(context.policy_hash,context.policy_version,'deterministic_rules',now))
        policy=con.execute('SELECT policy_version FROM policies WHERE policy_hash=?',(context.policy_hash,)).fetchone()
        dataset=con.execute('SELECT source_hash,cutoff FROM datasets WHERE dataset_version_id=?',(context.dataset_version_id,)).fetchone()
        if policy['policy_version']!=context.policy_version or (dataset['source_hash'],dataset['cutoff'])!=(context.source_hash,context.cutoff):
            raise AuditError('PROVENANCE_CONFLICT','Registered provenance conflicts with current metadata; review storage before continuing.')
        snapshot_id=new_id('PP');payload={**context.payload,'snapshot_utc':now};encoded=canonical(payload)
        con.execute('INSERT INTO passport_snapshots VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',(snapshot_id,context.alias,context.dataset_version_id,context.dataset_hash,context.manifest_hash,context.policy_hash,context.policy_version,payload['outcome'],'REAL',encoded,hashlib.sha256(encoded.encode()).hexdigest(),context.decision_hash,now))
        for ref in references(context.alias,context.dataset_hash,context.source_hash,context.cutoff):
            con.execute('INSERT INTO evidence_references VALUES(?,?,?,?,?,?,?,?,?,?,?)',(new_id('REF'),snapshot_id,'FEATURE_LEVEL',ref['feature'],context.alias,context.dataset_hash,context.source_hash,ref['cutoff'],ref['temporal_kind'],ref['derivation'],None))
        return snapshot_id

    def _insert_event(self,con,case,context,action,reason,reviewer_id,request_id,request_hash,snapshot_id,now,state):
        event_id=new_id('EV');revision=case['revision']+1
        con.execute('INSERT INTO review_events(event_id,case_id,case_revision,customer_ref,action,reason,reviewer_id,event_utc,dataset_hash,manifest_hash,policy_hash,policy_version,snapshot_id,request_id,request_hash) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(event_id,case['case_id'],revision,context.alias,action,reason,reviewer_id,now,context.dataset_hash,context.manifest_hash,context.policy_hash,context.policy_version,snapshot_id,request_id,request_hash))
        con.execute('UPDATE review_cases SET state=?,revision=?,current_snapshot_id=?,dataset_version_id=?,dataset_hash=?,manifest_hash=?,policy_hash=?,policy_version=?,decision_hash=?,last_action=?,last_reviewer_id=?,latest_event_id=?,updated_utc=? WHERE case_id=? AND revision=?',(state,revision,snapshot_id,context.dataset_version_id,context.dataset_hash,context.manifest_hash,context.policy_hash,context.policy_version,context.decision_hash,action,reviewer_id,event_id,now,case['case_id'],case['revision']))
        self._assert_still_current(context)
        return {'event_id':event_id,'case_id':case['case_id'],'snapshot_id':snapshot_id,'state':state,'revision':revision,'idempotent':False}

    def open_case(self,alias,reviewer_id,request_id):
        self._request(request_id);context=self.current(alias)
        def write(con):
            self._reviewer(con,reviewer_id)
            existing=con.execute('SELECT * FROM review_cases WHERE customer_ref=?',(alias,)).fetchone()
            if existing:return dict(existing)
            self._assert_still_current(context);now=utc_now();snapshot=self._snapshot(con,context,now);case_id=new_id('CASE')
            state='OPEN' if context.passport['rating']=='SUPPORTED' else 'INVESTIGATION_REQUIRED'
            con.execute('INSERT INTO review_cases VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(case_id,alias,state,0,snapshot,context.dataset_version_id,context.dataset_hash,context.manifest_hash,context.policy_hash,context.policy_version,context.decision_hash,None,None,None,now,now))
            case=dict(con.execute('SELECT * FROM review_cases WHERE case_id=?',(case_id,)).fetchone())
            self._insert_event(con,case,context,'OPEN','Opened the current passport for local prototype review.',reviewer_id,request_id,digest(['OPEN',alias,reviewer_id]),snapshot,now,state)
            return dict(con.execute('SELECT * FROM review_cases WHERE case_id=?',(case_id,)).fetchone())
        return self._run_write(write)

    def refresh_case(self,case_id,reviewer_id,reason,expected_revision,request_id):
        self._request(request_id);reason=self._reason(reason);case=self.store.case(case_id)
        if not case:raise AuditError('CASE_NOT_FOUND','Review case is unavailable.')
        context=self.current(case['customer_ref'])
        def write(con):
            self._reviewer(con,reviewer_id)
            case=dict(con.execute('SELECT * FROM review_cases WHERE case_id=?',(case_id,)).fetchone())
            if case['revision']!=expected_revision:raise AuditError('REVIEW_CONFLICT','Case changed in another session; reload before refreshing.')
            self._assert_still_current(context);now=utc_now();snapshot=self._snapshot(con,context,now)
            state='OPEN' if context.passport['rating']=='SUPPORTED' else 'INVESTIGATION_REQUIRED'
            return self._insert_event(con,case,context,'REFRESH',reason,reviewer_id,request_id,digest(['REFRESH',case_id,reviewer_id,reason,expected_revision]),snapshot,now,state)
        return self._run_write(write)

    def record_review(self,case_id,reviewer_id,action,reason,expected_revision,viewed_snapshot_id,request_id,passport_reviewed):
        self._request(request_id);reason=self._reason(reason)
        if action not in ACTION_STATE:raise AuditError('INVALID_REVIEW_ACTION','Choose Approve, Defer or Reject; no banking action is supported.')
        if passport_reviewed is not True:raise AuditError('PASSPORT_INSPECTION_REQUIRED','Inspect and explicitly acknowledge the current six-gate passport before saving.')
        case=self.store.case(case_id)
        if not case:raise AuditError('CASE_NOT_FOUND','Review case is unavailable.')
        context=self.current(case['customer_ref'])
        request_hash=digest([case_id,reviewer_id,action,reason,expected_revision,viewed_snapshot_id])
        def write(con):
            self._reviewer(con,reviewer_id)
            case=dict(con.execute('SELECT * FROM review_cases WHERE case_id=?',(case_id,)).fetchone());self._fresh_case(case,context);self._assert_still_current(context)
            if action=='APPROVE' and context.passport['rating']!='SUPPORTED':raise AuditError('APPROVAL_REQUIRES_SUPPORTED','Only a currently SUPPORTED real case may receive local prototype approval. CAUTION/ABSTAIN require investigation.')
            duplicate=con.execute('SELECT * FROM review_events WHERE request_id=?',(request_id,)).fetchone()
            if duplicate:
                if duplicate['request_hash']!=request_hash:raise AuditError('IDEMPOTENCY_CONFLICT','Request token was used for different review content; reload the case.')
                return {'event_id':duplicate['event_id'],'case_id':case_id,'snapshot_id':duplicate['snapshot_id'],'state':case['state'],'revision':case['revision'],'idempotent':True}
            if case['revision']!=expected_revision or case['current_snapshot_id']!=viewed_snapshot_id:raise AuditError('REVIEW_CONFLICT','Case or inspected snapshot changed; reload and inspect again.')
            now=utc_now();snapshot=self._snapshot(con,context,now)
            return self._insert_event(con,case,context,action,reason,reviewer_id,request_id,request_hash,snapshot,now,ACTION_STATE[action])
        return self._run_write(write)

    def status(self,case,context):
        if not case:return 'NOT_OPENED'
        try:self._fresh_case(case,context);return case['state']
        except AuditError:return 'STALE'
