"""Central evidence validation. Unknown evidence never means eligibility."""
import ast
import math
import numbers
import re

ACCOUNT_STATES = frozenset({'Active', 'Frozen', 'Dormant', 'Closed', 'Restricted'})
KYC_STATES = frozenset({'Verified', 'Pending', 'Review Due', 'Unverified', 'Expired', 'Rejected'})
CUSTOMER_STATES = frozenset({'Active', 'Dormant', 'Restricted', 'Closed', 'Frozen'})
PRODUCT_LABELS = frozenset({'Call Deposit','Credit Card','Current Account','Digital Banking','Fixed Deposit','Foreign Currency Account','Mortgage','Personal Loan','SME Working Capital','Savings Account'})
# Only whitespace and case variants of these exact labels are normalized.
def state(value, allowed):
    if not isinstance(value, str):
        return None
    return {v.casefold(): v for v in allowed}.get(' '.join(value.split()).casefold())

def identifier(value):
    return isinstance(value, str) and bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,127}', value)) and value.casefold() not in {'nan', 'none', 'null', 'unknown'}

def number(value, integer=False, maximum=None):
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        return None
    try:
        value = float(value)
    except (ValueError, OverflowError):
        return None
    if not math.isfinite(value) or value < 0 or (integer and not value.is_integer()) or (maximum is not None and value > maximum):
        return None
    return int(value) if integer else value

def holdings(value):
    """An explicit []/() is empty; null/blank/dict/scalar/duplicate entries are unknown."""
    if isinstance(value, str):
        if not value.strip() or len(value) > 10000:
            return None
        try:
            value = ast.literal_eval(value)
        except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
            return None
    if not isinstance(value, (list, tuple)):
        return None
    if any(not isinstance(p, str) or not p.strip() or len(p) > 100 or not re.fullmatch(r'[A-Za-z][A-Za-z /&-]*', p.strip()) for p in value):
        return None
    normalized = tuple(' '.join(p.split()) for p in value)
    if any(p.casefold() in {'unknown','none','null','nan','n/a','not available','unavailable'} for p in normalized):
        return None
    if len({p.casefold() for p in normalized}) != len(normalized):
        return None
    catalog = {p.casefold(): p for p in PRODUCT_LABELS}
    if any(p.casefold() not in catalog for p in normalized):
        return None
    return tuple(catalog[p.casefold()] for p in normalized)

def issue(gate, code, message):
    return {'gate': gate, 'code': code, 'message': message}

def validate(values):
    """Return normalized values and coded issues; keep invalid originals out of arithmetic."""
    normalized = dict(values)
    issues = []
    if not identifier(values.get('customer_id')):
        issues.append(issue('G1', 'INVALID_CUSTOMER_ID', 'Customer identifier is missing or malformed.'))
    for name, allowed in [('customer_status', CUSTOMER_STATES), ('account_status', ACCOUNT_STATES), ('kyc_status', KYC_STATES)]:
        normalized[name] = state(values.get(name), allowed)
        if normalized[name] is None:
            issues.append(issue('G4', 'INVALID_' + name.upper(), name.replace('_', ' ').capitalize() + ' is missing or unrecognized.'))
    for name, integer, maximum in [('qualifying_events_180d', True, None), ('recency_days', True, None), ('relationship_activity_percentile', False, 1)]:
        normalized[name] = number(values.get(name), integer, maximum)
        if normalized[name] is None:
            issues.append(issue('G2' if name == 'qualifying_events_180d' else 'G1', 'INVALID_' + name.upper(), name.replace('_', ' ').capitalize() + ' must be a finite nonnegative ' + ('integer.' if integer else 'number in [0, 1].')))
    normalized['products_held'] = holdings(values.get('products_held'))
    if normalized['products_held'] is None:
        issues.append(issue('G5', 'INVALID_HOLDINGS', 'Product ownership evidence is unavailable or malformed; no product gap can be established.'))
    for name in ['account_link_valid', 'transaction_date_valid', 'future_snapshot_as_history', 'model_approved', 'uses_model_for_action', 'staff_verification_required', 'automatic_outreach', 'human_review_required', 'service_issue']:
        if type(values.get(name)) is not bool:
            issues.append(issue('G1', 'INVALID_' + name.upper(), 'Evidence/control flag ' + name + ' must be a boolean.'))
    if not isinstance(values.get('behavioural_reason'), str):
        issues.append(issue('G5', 'INVALID_BEHAVIOURAL_REASON', 'Behavioural evidence must be text; unavailable evidence cannot support an offer.'))
        normalized['behavioural_reason'] = ''
    return normalized, issues

def safe_original(values):
    """Only nonidentifying primitive evidence: no IDs, free text, or arbitrary holdings."""
    result = {}
    for name in ['qualifying_events_180d', 'recency_days', 'relationship_activity_percentile']:
        v = values.get(name)
        try:
            finite = isinstance(v, (int, float)) and math.isfinite(v)
        except OverflowError:
            finite = False
        result[name] = v if finite else repr(v) if isinstance(v, float) else '<unavailable or invalid type>'
    for name, allowed in [('customer_status', CUSTOMER_STATES), ('account_status', ACCOUNT_STATES), ('kyc_status', KYC_STATES)]:
        v = values.get(name)
        result[name] = v if state(v, allowed) else '<unavailable or unrecognized>'
    valid_holdings = holdings(values.get('products_held')) is not None
    result['holdings_parse_valid'] = valid_holdings
    result['products_held'] = values.get('products_held') if valid_holdings else '<unavailable or malformed>'
    for name in ('account_link_valid','transaction_date_valid','future_snapshot_as_history','uses_model_for_action','automatic_outreach','human_review_required','staff_verification_required'):
        result[name] = values.get(name) if type(values.get(name)) is bool else '<invalid flag>'
    return result
