import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import pandas as pd
from portfolio_intelligence import profile
from pipeline import WEEKS

def test_no_future_weeks_in_profile():
    a={'Product_Code':['P1','P2']}
    for i,w in enumerate(WEEKS): a[w]=[10 if i<32 else 999,0 if i<32 else 999]
    d=pd.DataFrame(a)
    p=profile(d,32).set_index('product')
    assert p.loc['P1','historical_units']==320
    assert p.loc['P2','historical_units']==0
    assert p.loc['P2','demand_pattern']=='all_zero'

def test_profile_deterministic_and_valid():
    a={'Product_Code':['P2','P1','P3']}
    for w in WEEKS:a[w]=[1,3,0]
    p=profile(pd.DataFrame(a),44)
    assert len(p)==3 and p['product'].is_unique
    assert set(p.abc).issubset({'A','B','C'})
    assert set(p.xyz).issubset({'X','Y','Z'})
    assert (p.zero_share.between(0,1)).all()
