"""Original student-prototype design tokens and escaped visual components only."""
from html import escape
import streamlit as st

COLORS={
 'primary':'#1D3B6E','navy':'#10283F','accent':'#A85959','background':'#F4F7FB','surface':'#FFFFFF',
 'text':'#182B3B','muted':'#526676','border':'#DFE6ED','sidebar_muted':'#BDCDDD',
 'supported':'#16877C','caution':'#D39B35','abstain':'#8292A3','error':'#C64747',
 'supported_text':'#0D635B','supported_bg':'#E9F5F2','caution_text':'#78500B','caution_bg':'#FFF5DF',
 'abstain_text':'#43566A','abstain_bg':'#EDF1F5','error_text':'#9C2929','error_bg':'#FCEEEE',
}
FONT='Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif'
STATUS_COLORS={k:COLORS[k.lower()] for k in ('SUPPORTED','CAUTION','ABSTAIN')}
SPACING=(4,8,12,16,24,32,48)
TYPE_SCALE={'page':'2.125rem','section':'1.35rem','kpi':'2rem','body':'1rem','caption':'.875rem','status':'.8125rem'}
GATE_LABELS={'PASS':'PASS','CAUTION':'CAUTION','ABSTAIN':'BLOCK · ABSTAIN','PENDING':'PENDING'}

def stylesheet():
 c=COLORS;t=TYPE_SCALE
 return f'''<style>
 :root {{ {''.join('--banc-'+k.replace('_','-')+':'+v+';' for k,v in c.items())} {''.join('--banc-space-'+str(v)+':'+str(v)+'px;' for v in SPACING)} }}
 html,body,[data-testid="stAppViewContainer"],button,input,textarea,select,p,label,h1,h2,h3,h4,[data-testid="stMetricValue"],[data-testid="stSidebarNavLink"] span {{font-family:{FONT}!important;font-variant-numeric:tabular-nums;}}
 [data-testid="stMainBlockContainer"] {{padding-top:5rem;padding-bottom:3rem;max-width:1600px;}}
 h1,h2,h3 {{color:var(--banc-primary);letter-spacing:-.025em;overflow-wrap:anywhere;}}
 [data-testid="stMain"] h1 {{color:var(--banc-primary)!important;font-size:clamp(1.75rem,3vw,{t['page']})!important;line-height:1.2!important;font-weight:750!important;}}
 h2,h3 {{font-size:{t['section']}!important;line-height:1.35!important;}}
 [data-testid="stMain"] [data-testid="stCaptionContainer"] p {{color:var(--banc-muted)!important;}}
 [data-testid="stCaptionContainer"] {{color:var(--banc-muted);font-size:{t['caption']};line-height:1.5;}}
 [data-testid="stSidebar"] {{border-right:1px solid var(--banc-border);}}
 [data-testid="stSidebar"] [data-testid="stCaptionContainer"], [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{color:var(--banc-sidebar-muted)!important;}}
 [data-testid="stSidebarNav"] a {{border-radius:8px;min-height:36px;}}
 [data-testid="stNavSectionHeader"] {{height:auto!important;min-height:2rem;}}
 [data-testid="stNavSectionHeader"] > span {{white-space:normal!important;overflow:visible!important;text-overflow:clip!important;overflow-wrap:anywhere;line-height:1.4;}}
 [data-testid="stSidebarNav"] a[aria-current="page"] {{background:var(--banc-primary);border-left:3px solid var(--banc-accent);}}
 [data-testid="stSidebarNav"] a span {{white-space:normal!important;overflow-wrap:anywhere;overflow:visible!important;text-overflow:clip!important;line-height:1.4;}}
 [class*="st-key-kpi_"] {{background:var(--banc-surface);border:1px solid var(--banc-border);border-radius:12px;border-top:3px solid var(--banc-primary);padding:14px 16px;box-shadow:0 3px 12px rgba(16,40,63,.035);}}
 [class*="st-key-kpi_"] [data-testid="stMetricValue"] {{font-size:{t['kpi']};font-weight:700;color:var(--banc-primary);font-variant-numeric:tabular-nums;}}
 [class*="st-key-kpi_total_evaluated"] {{background:var(--banc-primary);}}
 [class*="st-key-kpi_total_evaluated"] [data-testid="stMetricValue"], [class*="st-key-kpi_total_evaluated"] [data-testid="stCaptionContainer"] p {{color:var(--banc-surface)!important;}}
 [class*="st-key-kpi_supported"] {{border-top-color:var(--banc-supported);}}
 [class*="st-key-kpi_caution"] {{border-top-color:var(--banc-caution);}}
 [class*="st-key-kpi_abstain"] {{border-top-color:var(--banc-abstain);}}
 [data-testid="stMetricValue"] {{font-variant-numeric:tabular-nums;}}
 [data-testid="stDataFrame"] {{border:1px solid var(--banc-border);border-radius:10px;}}
 [data-testid="stExpander"] {{background:var(--banc-surface);border-color:var(--banc-border);border-radius:10px;}}
 [data-testid="stSidebar"] [data-testid="stExpander"] {{background:var(--banc-navy);border-color:var(--banc-sidebar-muted);}}
 [data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button {{min-height:44px;border-radius:8px;max-width:100%;}}
 [data-testid="stButton"] button p,[data-testid="stFormSubmitButton"] button p {{white-space:normal!important;overflow-wrap:anywhere;}}
 button:focus-visible,a:focus-visible,input:not([role="combobox"]):focus-visible,textarea:focus-visible,[data-baseweb="select"]:focus-within {{outline:3px solid var(--banc-accent)!important;outline-offset:3px;}}
 .banc-identity {{display:flex;flex-wrap:wrap;gap:8px 18px;align-items:center;border-bottom:1px solid var(--banc-border);padding-bottom:16px;margin-bottom:6px;}}
 .banc-wordmark {{color:var(--banc-primary);font-size:1rem;font-weight:750;letter-spacing:.08em;}}
 .banc-student {{color:var(--banc-muted);font-size:.875rem;}}
 .banc-mode {{display:inline-block;padding:5px 10px;border-radius:6px;background:var(--banc-abstain-bg);color:var(--banc-primary);font-size:{t['status']};font-weight:700;letter-spacing:.06em;}}
 .banc-gates {{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--banc-space-12);margin:var(--banc-space-12) 0 20px;}}
 .banc-gate {{background:var(--banc-surface);border:1px solid var(--banc-border);border-left:4px solid var(--banc-primary);border-radius:10px;padding:16px;min-width:0;}}
 .banc-gate-head {{display:flex;align-items:start;justify-content:space-between;flex-wrap:wrap;gap:8px;}}
 .banc-gate h4 {{font-size:1rem;line-height:1.4;color:var(--banc-primary);margin:0;}}
 .banc-gate p {{font-size:.9375rem;line-height:1.5;margin:10px 0;color:var(--banc-text);}}
 .banc-gate code {{font-size:.75rem;color:var(--banc-muted);background:transparent;overflow-wrap:anywhere;white-space:normal;}}
 .banc-status {{font-size:{t['status']};font-weight:700;line-height:1.5;display:inline-block;border-radius:5px;padding:3px 8px;}}
 .banc-pass {{color:var(--banc-supported-text);background:var(--banc-supported-bg);}}
 .banc-caution {{color:var(--banc-caution-text);background:var(--banc-caution-bg);}}
 .banc-abstain,.banc-pending {{color:var(--banc-abstain-text);background:var(--banc-abstain-bg);}}
 .banc-transition {{padding:14px 18px;background:var(--banc-surface);border:1px solid var(--banc-border);border-left:4px solid var(--banc-accent);border-radius:10px;margin:12px 0;color:var(--banc-primary);font-weight:650;overflow-wrap:anywhere;}}
 .banc-transition small {{display:block;font-size:.875rem;font-weight:400;color:var(--banc-muted);margin-top:4px;}}
 .banc-comparison {{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--banc-border);border-radius:10px;overflow:hidden;margin:12px 0;}}
 .banc-comparison div {{padding:14px;background:var(--banc-surface);min-width:0;overflow-wrap:anywhere;}}
 .banc-comparison div:last-child {{background:var(--banc-caution-bg);}}
 .banc-comparison p {{font-size:.875rem;margin:8px 0;}}
 @media(max-width:900px) {{.banc-gates{{grid-template-columns:1fr;}}}}
 @media(max-width:600px) {{[data-testid="stMainBlockContainer"]{{padding:4.75rem 1rem 2rem;}} .banc-comparison{{grid-template-columns:1fr;}} .banc-identity{{gap:6px;}} [data-testid="stMetricValue"]{{font-size:1.7rem;}}}}
 @media(prefers-reduced-motion:reduce) {{*,*::before,*::after{{scroll-behavior:auto!important;transition:none!important;}}}}
 </style>'''

def apply_design():st.html(stylesheet())

def identity(mode=None):
 st.html('<div class="banc-identity"><span class="banc-wordmark">Banc-Inc360</span><span class="banc-student">Customer Intelligence &amp; Decision Support</span></div>')

def gate_cards(gates):
 cards=[]
 for g in gates:
  status=g['status'];kind={'PASS':'pass','CAUTION':'caution','ABSTAIN':'abstain'}.get(status,'pending')
  codes=', '.join(g.get('reason_codes',[])) or g.get('reason_code','Evidence unavailable')
  cards.append('<article class="banc-gate"><div class="banc-gate-head"><h4>'+escape(g['gate'])+'</h4><span class="banc-status banc-'+kind+'">'+escape(GATE_LABELS.get(status,status))+'</span></div><p>'+escape(g['reason'])+'</p><code>'+escape(codes)+'</code></article>')
 st.html('<section class="banc-gates" aria-label="Six-gate decision evidence">'+''.join(cards)+'</section>')

def replay_highlight(result):
 before=result['baseline']['rating'];after=result['simulated']['rating'];fields=result['modified_fields']
 st.html('<div class="banc-transition">'+escape(before)+' → '+escape(after)+' · SIMULATED comparison<small>'+escape('Changed fields: '+', '.join(fields) if fields else 'No overrides · simulation matches the unmodified baseline')+'</small></div>')
 if fields:
  allowed={'kyc_status':'KYC status','account_status':'Account status','qualifying_events_180d':'Qualifying events / 180d','products_held':'Recorded holdings'}
  baseline=result['baseline']['evidence']['original_values'];simulated=result['simulated']['evidence']['original_values']
  def column(values,title):
   rows=''.join('<p><strong>'+escape(allowed[f])+':</strong> '+escape(str(values.get(f,'Unavailable')))+'</p>' for f in fields if f in allowed)
   return '<div><strong>'+title+'</strong>'+rows+'</div>'
  st.html('<section class="banc-comparison" aria-label="Changed evidence comparison">'+column(baseline,'Baseline · source evidence')+column(simulated,'SIMULATED · counterfactual')+'</section>')


def system_information():
 with st.expander('About / System Information'):
  st.write('Banc-Inc360 is an independent demonstration system, not operated by BancABC and not a production banking service.')
  st.write('Source-derived analysis uses the supplied historical competition extract. Customer identifiers are masked; display and distribution still require permission. Current snapshot effective dates are unknown.')
  st.write('SUPPORTED means eligible for staff review under the implemented prototype rules, not bank approval. Six-gate checks remain authoritative. Reviewer identities are demonstration labels, not authenticated bank staff.')
  st.write('Historical machine learning evaluates future recorded inactivity, not confirmed churn. No approved live inference or calibrated customer churn probabilities are available. Activity percentiles are not profitability or lifetime value.')
  st.write('Illustrative upgrade scenarios use entirely synthetic customers and hypothetical Standard-to-Premium tiers, not BancABC-approved products or eligibility policies. Simulations change copies only.')
  st.write('Data Management uses a separate dataset registry; activation never updates the original dashboards. Business Opportunities does not write operational reviews. No customer outreach or financial action is connected.')
