import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pandas as pd
from decision_center import make_queue
from pipeline import predict,WEEKS

def fixture():
    return pd.DataFrame([{'Product_Code': f'P{i}', **{f'W{j}':int((i+j)%5) for j in range(52)}} for i in range(5)])

def test_queue_does_not_use_holdout():
    d=fixture();a=make_queue(d)
    for w in range(44,52):d[w]=999999
    b=make_queue(d)
    pd.testing.assert_frame_equal(a,b)

def test_queue_has_unique_products_and_nonnegative_forecasts():
    q=make_queue(fixture())
    assert q['product'].is_unique
    assert (q.forecast_next_week>=0).all()
    assert q.review_tier.isin(['High','Medium','Routine']).all()

def test_forecasts_stay_attached_to_product_after_profile_sort():
    d=pd.DataFrame([
        {'Product_Code':'P_low',**{w:1 for w in WEEKS}},
        {'Product_Code':'P_high',**{w:10 for w in WEEKS}},
    ])
    q=make_queue(d).set_index('product')
    assert np.isclose(q.loc['P_high','forecast_next_week'],10.0)
    assert np.isclose(q.loc['P_low','forecast_next_week'],1.0)
    assert q.loc['P_high','historical_units']==440
    assert q.loc['P_low','historical_units']==44
