import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pipeline import summarize, predict, backtest, WEEKS

def test_zero_denominator_is_undefined():
    x=pd.DataFrame({'actual':[0.], 'abs_error':[2.], 'signed_error':[2.], 'model':['a']})
    assert np.isnan(summarize(x,['model']).wape.iloc[0])

def test_future_purchase_values_do_not_change_past_predictions():
    frame=pd.DataFrame([
        {"Product_Code":"P1",**{w:i%7 for i,w in enumerate(WEEKS)}}
    ])
    shifted=frame.copy()
    for i in range(48,52):
        shifted[f"W{i}"]=800+i
    for model in ("naive","ma4","ses","croston_sba"):
        original=backtest(frame,[48],models=(model,))
        changed=backtest(shifted,[48],models=(model,))
        np.testing.assert_array_equal(original.forecast.to_numpy(),changed.forecast.to_numpy())
        assert not np.array_equal(original.actual.to_numpy(),changed.actual.to_numpy())
