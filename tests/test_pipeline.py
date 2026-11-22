import numpy as np
import pandas as pd
import pytest
from src.pipeline import predict,backtest,summarize,WEEKS,load_data

def test_naive_and_ma():
    assert predict([1,2,3,4],4,'naive').tolist()==[4]*4
    assert predict([1,2,3,4],4,'ma4').tolist()==[2.5]*4

def test_backtest_origin_and_denominator():
    df=pd.DataFrame([{'Product_Code':'P1',**{w:i for i,w in enumerate(WEEKS)}}])
    z=backtest(df,[44],models=('naive',))
    assert z.actual.tolist()==[44,45,46,47]
    assert z.forecast.tolist()==[43]*4
    m=summarize(z,['model']);assert m.iloc[0].absolute_error==10
    assert m.iloc[0].actual_units==182

def test_zero_wape_undefined():
    z=pd.DataFrame({'model':['a'],'actual':[0.],'abs_error':[1.],'signed_error':[1.]})
    assert np.isnan(summarize(z,['model']).iloc[0].wape)

def test_reject_negative(tmp_path):
    d={'Product_Code':['P1'],**{w:[0] for w in WEEKS}};d['W1']=[-1]
    path=tmp_path/'bad.csv';pd.DataFrame(d).to_csv(path,index=False)
    with pytest.raises(ValueError):load_data(path)

def test_backtest_forecasts_do_not_use_future_target_values():
    """Changing future targets must not alter forecasts made at an earlier origin."""
    rows=[]
    for p in ("P1","P2"):
        rows.append({"Product_Code":p,**{
            w:((i*3+2)%13 if p=="P1" else (i%5)*2)
            for i,w in enumerate(WEEKS)}})
    original=pd.DataFrame(rows)
    for origin in (44,48):
        changed=original.copy()
        for j in range(origin,52):
            changed[f"W{j}"]=10000+j
        for model in ("naive","ma4","ses","croston_sba"):
            a=backtest(original,[origin],models=(model,))
            b=backtest(changed,[origin],models=(model,))
            assert not np.array_equal(a.actual.to_numpy(),b.actual.to_numpy())
            np.testing.assert_allclose(a.forecast.to_numpy(),b.forecast.to_numpy())
