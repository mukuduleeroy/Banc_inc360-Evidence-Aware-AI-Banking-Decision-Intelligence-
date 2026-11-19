"""Portable, explicit application inputs. No download, publication or fallback to demo."""
from dataclasses import dataclass,field
from pathlib import Path
import hashlib,json,os,re
from data_access import load_index,FeatureValidationError,manifest_path,alias_key,FEATURE_COLUMNS

ROOT=Path(__file__).resolve().parent

class DeploymentError(ValueError):
    def __init__(self,code,message):super().__init__(message);self.code=code

def setting(name,default=None,secrets=None,environ=None):
    env=os.environ if environ is None else environ
    if name in env:return env[name]
    if secrets is None:
        import streamlit as st
        try:return st.secrets.get(name,default)
        except (FileNotFoundError,KeyError):return default
    return secrets.get(name,default)

def portable_path(value,root=ROOT,relative_only=False):
    p=Path(str(value)).expanduser()
    if relative_only and (p.is_absolute() or '..' in p.parts):
        raise DeploymentError('NONPORTABLE_PATH','Cloud paths must be repository-relative without parent traversal.')
    resolved=p.resolve() if p.is_absolute() else (Path(root)/p).resolve()
    if relative_only:
        try:resolved.relative_to(Path(root).resolve())
        except ValueError:raise DeploymentError('NONPORTABLE_PATH','Cloud data path escapes the repository root.') from None
    return resolved

@dataclass(frozen=True)
class DataConfig:
    mode:str
    runtime:str
    path:Path
    expected_sha256:str
    expected_version:str
    approval_reference:str
    access_scope:str
    alias_hex:str=field(repr=False)


def configuration(root=ROOT,secrets=None,environ=None):
    get=lambda k,d='':setting(k,d,secrets,environ)
    mode=str(get('DATA_MODE','LOCAL')).upper().strip()
    if mode not in {'LOCAL','DEPLOYED','DEMO'}:raise DeploymentError('INVALID_DATA_MODE','Set DATA_MODE to LOCAL, DEPLOYED or DEMO.')
    runtime=str(get('BANCINC_RUNTIME','CLOUD' if mode=='DEPLOYED' else 'LOCAL')).upper().strip()
    if runtime not in {'LOCAL','CLOUD'}:raise DeploymentError('INVALID_RUNTIME','Set BANCINC_RUNTIME to LOCAL or CLOUD.')
    if runtime=='CLOUD' and mode=='LOCAL':raise DeploymentError('CLOUD_MODE_REQUIRED','Cloud runtime requires explicit DEPLOYED or DEMO mode.')
    path=portable_path(get('BANCINC_FEATURES_PATH','outputs/customer_features.csv'),root,runtime=='CLOUD')
    c=DataConfig(mode,runtime,path,str(get('DATA_SHA256')).strip(),str(get('DATA_VERSION')).strip(),str(get('DATA_RELEASE_APPROVAL_REFERENCE')).strip(),str(get('DATA_ACCESS_SCOPE')).upper().strip(),str(get('BANCINC_ALIAS_KEY_HEX')).strip())
    if mode=='DEPLOYED':
        if not c.approval_reference or c.approval_reference.upper().startswith(('REPLACE','TODO','EXAMPLE','PENDING')):
            raise DeploymentError('DATA_RELEASE_NOT_APPROVED','Written BancABC approval for this artifact, hosting and audience must be verified before configuring DEPLOYED mode. Use DATA_MODE=DEMO meanwhile.')
        if c.access_scope not in {'PRIVATE_HOST','PUBLIC_APPROVED'}:raise DeploymentError('DATA_ACCESS_SCOPE_REQUIRED','Declare PRIVATE_HOST or PUBLIC_APPROVED only after verifying hosting and audience permission; this setting does not enforce authentication.')
        if not re.fullmatch('[a-f0-9]{64}',c.expected_sha256):raise DeploymentError('EXPECTED_FINGERPRINT_REQUIRED','Configure DATA_SHA256 from the reviewed artifact release.')
        if not c.expected_version:raise DeploymentError('EXPECTED_VERSION_REQUIRED','Configure DATA_VERSION from the approved manifest dataset_version.')
        if not re.fullmatch('[a-fA-F0-9]{64}',c.alias_hex):raise DeploymentError('ALIAS_SECRET_REQUIRED','Configure a private stable 32-byte BANCINC_ALIAS_KEY_HEX secret; do not commit it.')
    return c


def prepare_alias(c,root=ROOT):
    """Restore the stable cloud identity key, never rotate an existing local key."""
    if c.mode!='DEPLOYED':return None
    key=bytes.fromhex(c.alias_hex);path=Path(root)/'outputs/.presentation_alias_key'
    path.parent.mkdir(parents=True,exist_ok=True)
    try:fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError:pass
    else:
        with os.fdopen(fd,'wb') as f:f.write(key)
    if path.read_bytes()!=key:raise DeploymentError('ALIAS_KEY_CONFLICT','Configured key conflicts with existing presentation aliases. Retain history and inspect the configuration; do not silently rotate the key.')
    return key


def load_dataset(c,root=ROOT):
    if c.mode=='DEMO':return None
    if not c.path.is_file():raise DeploymentError('DATASET_UNAVAILABLE','Configured feature artifact is unavailable. Provision the authorized CSV and adjacent manifest at BANCINC_FEATURES_PATH, or explicitly select demo mode. No demo fallback occurred.')
    try:
        if c.mode=='DEPLOYED':
            content=c.path.read_bytes()
            if hashlib.sha256(content).hexdigest()!=c.expected_sha256:raise DeploymentError('DEPLOYED_HASH_MISMATCH','Feature fingerprint differs from the approved release. Provision the correct artifact; do not bypass validation.')
            try:
                manifest_content=manifest_path(c.path).read_bytes()
                manifest=json.loads(manifest_content)
            except (ValueError,OSError):raise DeploymentError('DEPLOYED_MANIFEST_REQUIRED','Deploy the verified adjacent .manifest.json for this release.') from None
            if not isinstance(manifest,dict) or manifest.get('dataset_version')!=c.expected_version:raise DeploymentError('DATA_VERSION_MISMATCH','Manifest dataset_version differs from configured DATA_VERSION.')
            import pandas as pd,io
            columns=pd.read_csv(io.BytesIO(content),nrows=0).columns
            if set(columns)!=set(FEATURE_COLUMNS):raise DeploymentError('DEPLOYED_SCHEMA_MISMATCH','Deployed release must contain exactly the validated customer feature schema, without raw source fields.')
        key=prepare_alias(c,root)
        index=load_index(c.path,key=key)
        if c.mode=='DEPLOYED':
            if manifest_path(c.path).read_bytes()!=manifest_content:raise DeploymentError('DEPLOYED_MANIFEST_CHANGED','Manifest changed during loading; inspect the release and retry.')
            if index.dataset_hash!=c.expected_sha256:raise DeploymentError('DEPLOYED_HASH_MISMATCH','Artifact changed during loading; retry only after inspecting the release.')
            if index.lineage_issues:raise DeploymentError('DEPLOYED_PROVENANCE_INVALID','Source manifest validation failed. Reconcile the approved release; recommendations are withheld.')
            if index.exclusions or any(r.invalid for r in index.records):raise DeploymentError('DEPLOYED_INVALID_RECORDS','Approved deployment artifact contains quarantined or invalid records; reconcile the release.')
        return index
    except (FeatureValidationError,DeploymentError):raise
    except OSError:raise DeploymentError('DATASET_UNREADABLE','Dataset or private identity configuration is unreadable. Check provisioning and filesystem permissions.') from None


def audit_configuration(root=ROOT,secrets=None,environ=None):
    get=lambda k,d='':setting(k,d,secrets,environ)
    mode=str(get('DATA_MODE','LOCAL')).upper().strip()
    runtime=str(get('BANCINC_RUNTIME','CLOUD' if mode=='DEPLOYED' else 'LOCAL')).upper().strip()
    cloud=runtime=='CLOUD'
    path=portable_path(get('BANCINC_AUDIT_DB','outputs/cloud_review.sqlite3' if cloud else 'outputs/review_audit.sqlite3'),root,cloud)
    return path,cloud
