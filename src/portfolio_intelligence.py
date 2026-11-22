"""Portfolio segmentation and out-of-sample segment forecasting policy."""
from pathlib import Path
import numpy as np
import pandas as pd
from pipeline import load_data, WEEKS, backtest

MODELS=('naive','ma4','ses','croston_sba')

def profile(data, end):
    """Only uses W0 to W(end-1); end is exclusive."""
    a=data[WEEKS[:end]].to_numpy(dtype=float)
    volume=a.sum(axis=1); mean=a.mean(axis=1); std=a.std(axis=1,ddof=0)
    cv=np.divide(std,mean,out=np.full(len(a),np.nan),where=mean>0)
    nonzero=(a>0).sum(axis=1)
    adi=np.divide(end,nonzero,out=np.full(len(a),np.inf),where=nonzero>0)
    pos_mean=np.divide(volume,nonzero,out=np.zeros(len(a)),where=nonzero>0)
    pos_var=np.array([row[row>0].var() if (row>0).any() else 0 for row in a])
    cv2=np.divide(pos_var,pos_mean**2,out=np.full(len(a),np.nan),where=pos_mean>0)
    out=pd.DataFrame({'product':data.Product_Code,'historical_units':volume,'mean_units':mean,'cv':cv,'zero_share':1-nonzero/end,'adi':adi,'cv2_positive':cv2})
    out=out.sort_values(['historical_units','product'],ascending=[False,True],kind='stable').reset_index(drop=True)
    total=volume.sum(); prior=(out.historical_units.cumsum()-out.historical_units)/total if total else 0
    out['abc']=np.select([prior<.8,prior<.95],['A','B'],default='C') if total else 'C'
    out.loc[out.historical_units==0,'abc']='C'
    out['xyz']=np.select([out.cv<=.5,out.cv<=1.],['X','Y'],default='Z')
    out['demand_pattern']=np.select([out.adi<1.32,out.adi>=1.32],['smooth_or_erratic','intermittent_or_lumpy'],default='unknown')
    out.loc[(out.adi<1.32)&(out.cv2_positive>=.49),'demand_pattern']='erratic'
    out.loc[(out.adi<1.32)&(out.cv2_positive<.49),'demand_pattern']='smooth'
    out.loc[(out.adi>=1.32)&(out.cv2_positive>=.49),'demand_pattern']='lumpy'
    out.loc[(out.adi>=1.32)&(out.cv2_positive<.49),'demand_pattern']='intermittent'
    out.loc[out.historical_units==0,'demand_pattern']='all_zero'
    return out

def metrics(frame,group):
    t=frame.groupby(group,as_index=False).agg(n=('actual','size'),actual_units=('actual','sum'),absolute_error=('abs_error','sum'),signed_error=('signed_error','sum'))
    t['wape']=np.where(t.actual_units>0,t.absolute_error/t.actual_units,np.nan)
    t['bias_pct']=np.where(t.actual_units>0,t.signed_error/t.actual_units,np.nan)
    return t

def build(source, output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    d=load_data(source)
    train_profile=profile(d,32)
    final_profile=profile(d,44)
    train_profile.to_csv(out/'portfolio_selection_profile.csv',index=False)
    final_profile.to_csv(out/'portfolio_profile.csv',index=False)
    validation=backtest(d,[32,36,40],MODELS).merge(train_profile[['product','abc','xyz','demand_pattern']],on='product',validate='many_to_one')
    scores=metrics(validation,['abc','xyz','model'])
    scores['sort_wape']=scores.wape.fillna(np.inf)
    rules=scores.sort_values(['abc','xyz','sort_wape','model']).drop_duplicates(['abc','xyz'])[['abc','xyz','model']].rename(columns={'model':'chosen_model'})
    rules.to_csv(out/'segment_policy.csv',index=False)
    scores.drop(columns='sort_wape').to_csv(out/'segment_selection_metrics.csv',index=False)
    hold=backtest(d,[44,48],MODELS).merge(final_profile[['product','abc','xyz','demand_pattern','historical_units']],on='product',validate='many_to_one')
    hold=hold.merge(rules,on=['abc','xyz'],how='left',validate='many_to_one')
    if hold.chosen_model.isna().any(): raise AssertionError('Unseen segment in holdout; define fallback before evaluation')
    policy=hold[hold.model==hold.chosen_model].copy();policy['strategy']='segmented_policy'
    naive=hold[hold.model=='naive'].copy();naive['strategy']='naive'
    ses=hold[hold.model=='ses'].copy();ses['strategy']='ses'
    comparison=pd.concat([naive,ses,policy],ignore_index=True)
    assert len(policy)==len(d)*8 and not policy.duplicated(['product','origin','horizon']).any()
    metrics(comparison,['strategy','horizon']).to_csv(out/'policy_horizon_metrics.csv',index=False)
    metrics(comparison,['strategy']).to_csv(out/'policy_overall_metrics.csv',index=False)
    metrics(comparison,['strategy','abc','xyz']).to_csv(out/'policy_segment_metrics.csv',index=False)
    exceptions=metrics(policy,['product']).merge(final_profile,on='product',validate='one_to_one')
    exceptions['priority_units']=exceptions.absolute_error
    exceptions['action']=np.select([(exceptions.abc=='A')&(exceptions.absolute_error>=exceptions.absolute_error.quantile(.75)),exceptions.zero_share>=.5,exceptions.bias_pct.abs()>=.2],['Review high-volume forecast discrepancy','Review sparse purchasing pattern','Review directional forecast bias'],default='Routine monitoring')
    exceptions=exceptions.sort_values(['priority_units','historical_units'],ascending=False)
    exceptions.to_csv(out/'policy_exceptions.csv',index=False)
    summary=metrics(comparison,['strategy'])
    best=summary.set_index('strategy')
    report=f'''# Portfolio intelligence and segment forecasting

All figures use observed weekly purchase quantities, not unconstrained demand.

- Dataset: {len(d)} products, 52 indexed weeks.
- Segment selection profiles: historical W0 to W31.
- Validation targets: W32 to W43.
- Final historical profiles: W0 to W43.
- Final untouched test targets: W44 to W51.
- ABC: concentration of observed units, not sales value.
- XYZ: coefficient of variation, with X <= 0.5, Y <= 1, Z > 1.

## Final holdout comparison

{summary.to_markdown(index=False,floatfmt='.4f')}

## Interpretation

Segment policy relative reduction in absolute error versus naive: **{1-best.loc['segmented_policy','absolute_error']/best.loc['naive','absolute_error']:.1%}**.
Segment policy relative reduction versus global SES: **{1-best.loc['segmented_policy','absolute_error']/best.loc['ses','absolute_error']:.1%}** (negative indicates poorer performance).

Segmenting products may help planning reviews even when it does not improve overall forecast accuracy. These results do not support causal claims, monetary effects, or inventory service levels.
'''
    (out/'portfolio_findings.md').write_text(report)
    return summary,rules,final_profile

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--output',default='outputs');a=p.parse_args()
    print(build(a.source,a.output)[0].to_string(index=False))
