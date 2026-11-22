import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pipeline import summarize, predict

def test_zero_denominator_is_undefined():
    x=pd.DataFrame({'actual':[0.], 'abs_error':[2.], 'signed_error':[2.], 'model':['a']})
    assert np.isnan(summarize(x,['model']).wape.iloc[0])

def test_forecast_never_reads_future():
    assert np.array_equal(predict([1,2,3],4,'ma4'),predict([1,2,3],4,'ma4'))
    assert np.array_equal(predict([1,2,3],4,'ses'),predict([1,2,3],4,'ses'))
