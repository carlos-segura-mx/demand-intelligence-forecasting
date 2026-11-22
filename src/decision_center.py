"""Prospective review queue built exclusively from W0 to W43."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from pipeline import load_data, WEEKS, predict
from portfolio_intelligence import profile

def make_queue(data, history_end=44):
    if history_end < 8 or history_end > 52:
        raise ValueError('Invalid history boundary')
    p = profile(data, history_end).copy()
    a = data[WEEKS[:history_end]].to_numpy(dtype=float)
    p['forecast_next_week'] = [float(predict(row, 1, 'ses')[0]) for row in a]
    p['forecast_four_week_total'] = p.forecast_next_week * 4
    p['last_four_week_units'] = a[:, -4:].sum(axis=1)
    p['previous_four_week_units'] = a[:, -8:-4].sum(axis=1)
    p['recent_shift_units'] = p.last_four_week_units - p.previous_four_week_units
    p['recent_shift_ratio'] = p.recent_shift_units / np.maximum(p.previous_four_week_units, 1)
    p['high_variability'] = p.xyz.eq('Z')
    p['sparse_history'] = p.zero_share.ge(.5)
    p['large_recent_shift'] = p.recent_shift_ratio.abs().ge(.5) & p.recent_shift_units.abs().ge(4)
    p['review_score'] = (p.abc.map({'A':3,'B':2,'C':1}).astype(int)
                         + p.high_variability.astype(int)*2
                         + p.sparse_history.astype(int)
                         + p.large_recent_shift.astype(int)*2)
    p['review_tier'] = np.select([p.review_score>=6,p.review_score>=4],['High','Medium'],default='Routine')
    p['review_reason'] = p.apply(lambda r: '; '.join(x for ok,x in [
        (r.abc=='A','high historical volume'),
        (r.high_variability,'volatile observed quantities'),
        (r.sparse_history,'many zero weeks'),
        (r.large_recent_shift,'recent four-week shift')
    ] if ok) or 'routine review',axis=1)
    p['recommended_review'] = np.select([
        p.large_recent_shift,p.sparse_history,p.high_variability
    ],[
        'Investigate recent quantity shift and commercial context',
        'Confirm purchasing cadence and whether zeros reflect availability',
        'Check volatile purchasing history before manual forecast override'
    ],default='Monitor SES forecast against incoming observations')
    p['history_end_exclusive'] = history_end
    return p.sort_values(['review_score','historical_units','product'],ascending=[False,False,True]).reset_index(drop=True)

def build(source, output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    queue=make_queue(load_data(source),44)
    queue.to_csv(out/'prospective_review_queue.csv',index=False)
    counts=queue.review_tier.value_counts().reindex(['High','Medium','Routine'],fill_value=0)
    (out/'decision_center_findings.md').write_text(
        '# Decision Center: prospective review queue\n\n'
        'The review queue uses W0 to W43 only. It excludes final holdout outcomes.\n\n'
        f'Products: {len(queue)}. High: {counts["High"]}; Medium: {counts["Medium"]}; Routine: {counts["Routine"]}.\n\n'
        'Review scores are analyst-defined heuristics, not calibrated risk, stockout probabilities, '
        'monetary exposures or purchase orders. Forecasts use fixed SES alpha=0.3.\n'
    )
    return queue

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--source',required=True);a.add_argument('--output',default='outputs');args=a.parse_args()
    q=build(args.source,args.output)
    print(q.review_tier.value_counts().to_string())
