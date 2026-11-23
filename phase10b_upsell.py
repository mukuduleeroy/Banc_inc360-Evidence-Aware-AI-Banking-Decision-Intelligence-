"""Pure synthetic upgrade demonstration. No operational engine, real customers or writes."""
from dataclasses import dataclass,replace,asdict
from types import MappingProxyType
import re,math
from evidence import state,CUSTOMER_STATES,ACCOUNT_STATES,KYC_STATES

ELIGIBLE='DEMO_ELIGIBLE_FOR_REVIEW'
MISSING='DEMO_NEEDS_MORE_EVIDENCE'
INELIGIBLE='DEMO_NOT_ELIGIBLE'
VERSION='hypothetical-package-upgrade-v1'
PROVENANCE='Independently invented student demonstration; no BancABC product specification or real customer evidence.'
NOTICE='SYNTHETIC UPSELL DEMONSTRATION ONLY — hypothetical products and evidence; not an operational six-gate decision, bank-approved suitability, offer or customer-contact authorization.'
REQUIRED=('source_ownership','target_absent','activity_history','expanded_service_requests','customer_status','account_status','kyc_status','human_review')

@dataclass(frozen=True)
class Product:
    product_id:str
    name:str
    family:str
    tier:int
    synthetic:bool=True

BASE=Product('HYP-STANDARD','Hypothetical Standard Account Package','Hypothetical account package',1)
PREMIUM=Product('HYP-PREMIUM','Hypothetical Premium Account Package','Hypothetical account package',2)
CATALOG=MappingProxyType({p.product_id:p for p in (BASE,PREMIUM)})

@dataclass(frozen=True)
class UpgradeSpec:
    source:Product=BASE
    target:Product=PREMIUM
    relationship:str='UPGRADE_WITHIN_PRODUCT_FAMILY'
    required_attributes:tuple=REQUIRED
    min_events_180d:int=4
    min_requests_180d:int=2
    human_review_required:bool=True
    version:str=VERSION
    synthetic:bool=True
    bank_approved:bool=False
    provenance:str=PROVENANCE

@dataclass(frozen=True)
class DemoCustomer:
    demo_id:str
    products:tuple
    ownership_verified:bool
    events_180d:int
    expanded_service_requests_180d:int
    customer_status:str='Active'
    account_status:str='Active'
    kyc_status:str='Verified'
    human_review_required:bool=True
    automatic_outreach:bool=False
    synthetic:bool=True
    provenance:str=PROVENANCE


def validate_relationship(spec):
    if not isinstance(spec,UpgradeSpec):raise ValueError('Only the typed illustrative product specification is supported.')
    if spec.synthetic is not True or spec.bank_approved is not False or spec.provenance!=PROVENANCE or spec.version!=VERSION:raise ValueError('Only the registered synthetic, non-bank-approved provenance/version is supported.')
    if not isinstance(spec.source,Product) or not isinstance(spec.target,Product):raise ValueError('Source and target product evidence is required.')
    s,t=spec.source,spec.target
    if any(not isinstance(p.product_id,str) or not isinstance(p.name,str) or not isinstance(p.family,str) for p in (s,t)):raise ValueError('Product identifiers, labels and families must be explicit registered strings.')
    if s.product_id==t.product_id or s.name.casefold()==t.name.casefold():raise ValueError('Source and target must be distinct tiers, not identical products.')
    if type(s.tier) is not int or type(t.tier) is not int or t.tier<=s.tier:raise ValueError('An upsell requires a strictly higher target tier; downgrades are rejected.')
    if s.family!=t.family or spec.relationship!='UPGRADE_WITHIN_PRODUCT_FAMILY':raise ValueError('An upsell must remain within the explicit product family.')
    if any(p.synthetic is not True or CATALOG.get(p.product_id)!=p for p in (s,t)):raise ValueError('Only registered hypothetical products are supported; no bank product facts may be invented.')
    if spec.required_attributes!=REQUIRED or type(spec.min_events_180d) is not int or type(spec.min_requests_180d) is not int or spec.min_events_180d!=4 or spec.min_requests_180d!=2 or spec.human_review_required is not True:raise ValueError('Unsupported eligibility assumptions or missing mandatory human review.')
    return spec


def _count(value):
    return value if type(value) is int and 0<=value<=1000000 else None


def assess_upsell(customer,spec=UpgradeSpec()):
    """Own DEMO namespace; blocked > missing > illustrative review-eligible. Never G5 approval."""
    checks=[]
    def add(code,status,reason):checks.append({'check':code,'status':status,'reason':reason})
    try:validate_relationship(spec)
    except (ValueError,AttributeError,TypeError):
        add('DEMO_RELATIONSHIP','FAIL','Source/target tier relationship, illustrative policy or provenance is invalid.')
        return _result(None,None,checks)
    add('DEMO_RELATIONSHIP','PASS','Registered hypothetical Standard tier 1 → Premium tier 2 in the same account-package family.')
    if not isinstance(customer,DemoCustomer) or not re.fullmatch(r'DEMO-UP-[0-9]{3}',customer.demo_id if isinstance(customer.demo_id,str) else '') or customer.synthetic is not True or customer.provenance!=PROVENANCE:
        add('DEMO_SYNTHETIC_SCOPE','FAIL','Real customer aliases and unverified or non-synthetic evidence are not accepted by this demonstration.')
        return _result(None,spec,checks)
    add('DEMO_SYNTHETIC_SCOPE','PASS','Customer, ownership and eligibility are independently invented synthetic evidence, not a real customer match.')
    known=isinstance(customer.products,tuple) and all(isinstance(p,str) for p in customer.products) and len(set(customer.products))==len(customer.products) and all(p in CATALOG for p in customer.products)
    ownership=known and customer.ownership_verified is True
    if not ownership:
        add('DEMO_SOURCE_OWNERSHIP','MISSING','Verified synthetic source-product ownership is unavailable; no ownership is imputed.')
        add('DEMO_TARGET_ABSENT','MISSING','Target absence cannot be established without verified known holdings.')
    else:
        add('DEMO_SOURCE_OWNERSHIP','PASS' if spec.source.product_id in customer.products else 'FAIL','Hypothetical base-tier ownership is recorded.' if spec.source.product_id in customer.products else 'Known holdings do not include the source tier.')
        held=spec.target.product_id in customer.products
        add('DEMO_TARGET_ABSENT','FAIL' if held else 'PASS','Hypothetical target tier is already held; exclude upgrade.' if held else 'Known synthetic holdings exclude the target tier.')
    for attr,minimum,code,label in (('events_180d',spec.min_events_180d,'DEMO_ACTIVITY_HISTORY','Qualifying events'),('expanded_service_requests_180d',spec.min_requests_180d,'DEMO_UPGRADE_NEED','Recorded requests for expanded package features')):
        value=_count(getattr(customer,attr))
        status='MISSING' if value is None or value<minimum else 'PASS'
        add(code,status,f'{label}: '+('unavailable; no default assumed.' if value is None else f'{value} / preceding 180 days; illustrative minimum {minimum}.'))
    for attr,allowed,required,code in (('customer_status',CUSTOMER_STATES,'Active','DEMO_CUSTOMER_STATUS'),('account_status',ACCOUNT_STATES,'Active','DEMO_ACCOUNT_STATUS'),('kyc_status',KYC_STATES,'Verified','DEMO_KYC')):
        value=state(getattr(customer,attr),allowed)
        add(code,'MISSING' if value is None else 'PASS' if value==required else 'FAIL','Synthetic '+attr+': '+(value or 'unknown')+'; illustrative requirement '+required+'.')
    if customer.human_review_required is True and customer.automatic_outreach is False:add('DEMO_HUMAN_CONTROL','PASS','Mandatory human review; no automatic communication, offer, account change or financial action.')
    else:add('DEMO_HUMAN_CONTROL','FAIL','Missing or inconsistent human-review/no-outreach controls block the illustrative opportunity.')
    return _result(customer,spec,checks)


def _result(customer,spec,checks):
    failed=[c['check'] for c in checks if c['status']=='FAIL'];missing=[c['check'] for c in checks if c['status']=='MISSING']
    status=INELIGIBLE if failed else MISSING if missing else ELIGIBLE
    owned=customer.products if customer is not None and customer.ownership_verified is True and isinstance(customer.products,tuple) and all(isinstance(p,str) and p in CATALOG for p in customer.products) and len(set(customer.products))==len(customer.products) else None
    existing=spec.source.name if spec is not None and owned is not None and spec.source.product_id in owned else 'Unavailable — required source ownership not established'
    reason=('Blocked by failed illustrative checks.' if failed else 'More verified synthetic evidence is needed; no positive upgrade recommendation.' if missing else 'Verified synthetic base-tier ownership, sufficient historical activity and recorded expanded-service requests support a hypothetical higher-tier review.')
    return {'customer':customer.demo_id if customer is not None else 'DEMO-UNVERIFIED','source_product':existing,'required_source_product':spec.source.name if spec else 'Unavailable — invalid relationship','target_product':spec.target.name if spec else 'Unavailable — invalid relationship','relationship_type':spec.relationship if spec else 'Invalid','assessment':status,'checks':checks,'passed_checks':[c['check'] for c in checks if c['status']=='PASS'],'failed_checks':failed,'missing_evidence':missing,'explanation':reason,'human_review_required':True,'synthetic':True,'bank_approved':False,'operational_authorization':False,'operational_g5_evaluated':False,'spec_version':spec.version if spec else 'Unavailable','provenance':PROVENANCE,'notice':NOTICE,'evidence':{'events_180d':_count(customer.events_180d),'expanded_service_requests_180d':_count(customer.expanded_service_requests_180d),'ownership_verified':customer.ownership_verified is True,'known_hypothetical_holdings':[CATALOG[p].name for p in owned] if owned is not None else None} if customer else {}}


def demo_scenarios():
    """Independent fixtures; no source files, accepted aliases or real customer rows read."""
    base=DemoCustomer('DEMO-UP-001',(BASE.product_id,),True,8,3)
    return (
      ('Eligible hypothetical upgrade',base,UpgradeSpec()),
      ('Already holds hypothetical target',replace(base,demo_id='DEMO-UP-002',products=(BASE.product_id,PREMIUM.product_id)),UpgradeSpec()),
      ('Missing activity evidence',replace(base,demo_id='DEMO-UP-003',events_180d=None),UpgradeSpec()),
      ('Restricted synthetic customer',replace(base,demo_id='DEMO-UP-004',customer_status='Restricted'),UpgradeSpec()),
      ('Unverified source ownership',replace(base,demo_id='DEMO-UP-005',products=None,ownership_verified=None),UpgradeSpec()),
      ('Invalid same-tier product relationship',replace(base,demo_id='DEMO-UP-006'),replace(UpgradeSpec(),target=BASE)),
      ('Insufficient historical activity',replace(base,demo_id='DEMO-UP-007',events_180d=1),UpgradeSpec()),
    )


def demo_summary():
    results=[assess_upsell(c,s) for _,c,s in demo_scenarios()]
    counts={k:sum(r['assessment']==k for r in results) for k in (ELIGIBLE,MISSING,INELIGIBLE)}
    assert sum(counts.values())==len(results)
    return {'population':'independent synthetic upsell fixtures only','customers':len(results),'counts':counts,'operational_authorization':False}
