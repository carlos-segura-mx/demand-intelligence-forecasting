"""Auditable holdout exception ranking. Historical quantities are the only business weights."""
from pathlib import Path
import numpy as np
import pandas as pd
from pipeline import WEEKS,load_data

def build(source, outputs):
    out=Path(outputs); d=load_data(source); p=pd.read_csv(out/'final_predictions.csv')
    assert set(p['origin'])=={44,48} and p['horizon'].between(1,4).all()
    assert (p['origin']+p['horizon']-1<=51).all()
    m=p.groupby('model',as_index=False).agg(actual=('actual','sum'),abs_error=('abs_error','sum'),signed_error=('signed_error','sum'),n=('actual','size'))
    m['wape']=m.abs_error/m.actual;m['bias_pct']=m.signed_error/m.actual
    m.to_csv(out/'model_summary.csv',index=False)
    hist=d.set_index('Product_Code')[WEEKS[:44]]
    stats=pd.DataFrame({'product':hist.index,'historical_units':hist.sum(axis=1).values,'zero_share':hist.eq(0).mean(axis=1).values,'historical_mean':hist.mean(axis=1).values})
    hold=p.groupby(['product','model'],as_index=False).agg(actual_units=('actual','sum'),abs_error=('abs_error','sum'),signed_error=('signed_error','sum'),n=('actual','size'))
    wide=hold.pivot(index='product',columns='model',values=['abs_error','signed_error','actual_units'])
    chosen=[v for v in p.model.unique() if v!='naive'][0]
    e=stats.set_index('product')
    e['test_actual_units']=wide['actual_units']['naive'];e['baseline_abs_error']=wide['abs_error']['naive'];e['selected_abs_error']=wide['abs_error'][chosen]
    e['selected_signed_error']=wide['signed_error'][chosen]
    e['improvement_units']=e.baseline_abs_error-e.selected_abs_error
    e['selected_wape']=np.where(e.test_actual_units>0,e.selected_abs_error/e.test_actual_units,np.nan)
    e['persistent_bias']=False
    pp=p[p.model==chosen].groupby(['product','origin']).signed_error.sum().unstack()
    e['persistent_bias']=(pp[44]*pp[48]>0)&(pp.abs().min(axis=1)>=2)
    e['high_volume']=e.historical_units>=e.historical_units.quantile(.75)
    e['underperforming_baseline']=e.improvement_units<0
    e['intermittent_proxy']=e.zero_share>=.5
    e['priority_units']=e.selected_abs_error
    e['exception_reason']=np.select([e.high_volume & (e.selected_abs_error>=e.selected_abs_error.quantile(.75)),e.underperforming_baseline,e.persistent_bias,e.intermittent_proxy],['High volume and high absolute error','Selected model worse than naive','Same-sign bias at both origins','High share of zero weeks'],default='Routine monitoring')
    e=e.sort_values(['priority_units','historical_units'],ascending=False).reset_index()
    e.to_csv(out/'decision_exceptions.csv',index=False)
    assert np.isclose(e.selected_abs_error.sum(),m.loc[m.model==chosen,'abs_error'].iloc[0])
    assert np.isclose(e.baseline_abs_error.sum(),m.loc[m.model=='naive','abs_error'].iloc[0])
    report=f'''# Executive findings for observed weekly quantities

Source: UCI Sales Transactions Weekly; 811 products and 52 indexed weeks. No calendar dates, inventory, prices, or unconstrained demand are available.

Selection uses forecast origins 32, 36 and 40; final evaluation uses origins 44 and 48. Selected model: {chosen}.

## Final holdout metrics

{m.to_markdown(index=False,floatfmt='.4f')}

Relative reduction in pooled absolute error versus naive: **{1-m.loc[m.model==chosen,'abs_error'].iloc[0]/m.loc[m.model=='naive','abs_error'].iloc[0]:.1%}**.

The selected model has greater absolute error than naive for **{int(e.underperforming_baseline.sum())}** individual products. **{int(e.intermittent_proxy.sum())}** products have at least 50% zero weeks in the historical window.

## Interpretation

Retrospective quantity errors can guide a review, but are not monetary exposure or inventory recommendations. There are no calendar dates, stockouts, costs or promotions. Two holdout origins cannot establish stable product-level superiority.
'''
    (out/'executive_findings.md').write_text(report)
    return m,e

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--source',required=True);a.add_argument('--output',default='outputs');v=a.parse_args();m,e=build(v.source,v.output);print(m.to_string(index=False))
