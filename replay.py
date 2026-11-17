"""Controlled counterfactuals: copies only, engine authority, no writes or actions."""
from dataclasses import asdict
from data_access import row_case
from engine import evaluate
from evidence import holdings

ALLOWED_FIELDS=frozenset({'kyc_status','account_status','qualifying_events_180d','products_held'})

def simulate(index,alias,overrides=None):
    overrides=overrides or {}
    if set(overrides)-ALLOWED_FIELDS:
        raise ValueError('UNSUPPORTED_SIMULATION_FIELD: Only permitted evidence fields can be simulated.')
    values=dict(index.customer_values(alias))
    baseline=index.passport(alias)
    values.update(overrides)
    if 'products_held' in overrides:
        products=holdings(overrides['products_held'])
        values['product_gap']=None if products is None else 'Savings Account' not in products
    result=evaluate(row_case(values,index.lineage_issues))
    result['customer_id']=alias
    result['simulated']=True
    result['action_authorized']=False
    result['lineage']=dict(baseline['lineage'])
    changed=[]
    for old,new in zip(baseline['gates'],result['gates']):
        if (old['status'],old['reason_codes'],old['reason'])!=(new['status'],new['reason_codes'],new['reason']):
            changed.append({'Gate':new['gate'],'Baseline':old['status'],'SIMULATED':new['status'],'Reason codes':', '.join(new['reason_codes']),'Explanation':new['reason']})
    return {'baseline':baseline,'simulated':result,'changed_gates':changed,'modified_fields':tuple(sorted(overrides))}
