"""Leakage-aware weekly product forecasting; no calendar dates are inferred."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
WEEKS=[f"W{i}" for i in range(52)]

def load_data(path):
    df=pd.read_csv(path)
    required=["Product_Code",*WEEKS]
    if any(c not in df for c in required): raise ValueError("Missing required columns")
    if df.Product_Code.isna().any() or df.Product_Code.duplicated().any(): raise ValueError("Invalid product IDs")
    values=df[WEEKS].apply(pd.to_numeric,errors="raise")
    if values.isna().any().any() or not np.isfinite(values.to_numpy()).all(): raise ValueError("Invalid quantities")
    if (values.to_numpy()<0).any() or not np.equal(values.to_numpy(),np.floor(values.to_numpy())).all(): raise ValueError("Quantities must be nonnegative integers")
    return df.assign(**{c:values[c].astype(int) for c in WEEKS})

def predict(history, horizon, model):
    a=np.asarray(history,dtype=float)
    if len(a)<2 or horizon<1: raise ValueError("Insufficient history/horizon")
    if model=="naive": value=a[-1]
    elif model=="ma4": value=a[-min(4,len(a)):].mean()
    elif model=="ses":
        level=a[0]
        for y in a[1:]: level=.3*y+.7*level
        value=level
    elif model=="croston_sba":
        nz=np.flatnonzero(a>0)
        if not len(nz): value=0.
        else:
            alpha=.2; demand=a[nz[0]]; interval=float(nz[0]+1); previous=int(nz[0])
            for j in nz[1:]:
                demand=alpha*a[j]+(1-alpha)*demand
                interval=alpha*(int(j)-previous)+(1-alpha)*interval
                previous=int(j)
            value=(1-alpha/2)*demand/max(interval,1e-12)
    else: raise ValueError(model)
    return np.repeat(max(0.,float(value)),horizon)

def backtest(df, origins, models=("naive","ma4","ses","croston_sba")):
    records=[]
    for row in df.itertuples(index=False):
        y=np.array([getattr(row,w) for w in WEEKS],dtype=float)
        for origin in origins:
            if origin<2 or origin+4>52: raise ValueError("Origin out of range")
            for model in models:
                pred=predict(y[:origin],4,model)
                for h in range(1,5):
                    actual=y[origin+h-1]; estimate=pred[h-1]
                    records.append((row.Product_Code,origin,h,model,actual,estimate,abs(actual-estimate),estimate-actual))
    return pd.DataFrame(records,columns=['product','origin','horizon','model','actual','forecast','abs_error','signed_error'])

def summarize(df,by):
    g=df.groupby(by,dropna=False).agg(n=('actual','size'),actual_units=('actual','sum'),absolute_error=('abs_error','sum'),signed_error=('signed_error','sum')).reset_index()
    g['mae']=g.absolute_error/g.n
    g['wape']=np.where(g.actual_units>0,g.absolute_error/g.actual_units,np.nan)
    g['bias_units_per_prediction']=g.signed_error/g.n
    return g

def run(source,out):
    data=load_data(source);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    # The final holdout is never used for candidate model selection.
    selection=backtest(data,[32,36,40]); selection_metrics=summarize(selection,['model','horizon'])
    chosen=selection_metrics.groupby('model').apply(lambda x: x.absolute_error.sum()/max(x.actual_units.sum(),1),include_groups=False).idxmin()
    final=backtest(data,[44,48],models=('naive',chosen) if chosen!='naive' else ('naive',))
    metrics=summarize(final,['model','horizon']); products=summarize(final,['product','model'])
    baseline=products[products.model=='naive'].copy()
    volume=data[['Product_Code',*WEEKS[:44]]].set_index('Product_Code').sum(axis=1)
    baseline['historical_volume']=baseline['product'].map(volume)
    baseline['zero_share']=baseline['product'].map(data.set_index('Product_Code')[WEEKS[:44]].eq(0).mean(axis=1))
    baseline['priority_score_units']=baseline.absolute_error
    baseline['priority_reason']=np.where(baseline.zero_share>=.5,'Intermittent / high zero share','Observed forecast error')
    baseline=baseline.sort_values(['priority_score_units','historical_volume'],ascending=False)
    selection_metrics.to_csv(out/'selection_metrics.csv',index=False)
    final.to_csv(out/'final_predictions.csv',index=False)
    metrics.to_csv(out/'final_metrics.csv',index=False)
    baseline.to_csv(out/'exceptions.csv',index=False)
    (out/'run_summary.txt').write_text(f'Products: {len(data)}\nSelected model: {chosen}\nFinal origins: 44,48\nFinal target weeks: W44-W51\n')
    return chosen

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);parser.add_argument('--output',default='outputs');args=parser.parse_args()
    print('Selected candidate:',run(args.source,args.output))
