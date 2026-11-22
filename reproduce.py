"""Rebuild original portfolio analytics outputs from the verified UCI CSV."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from pipeline import run
from decision_analysis import build as decision
from portfolio_intelligence import build as portfolio
from decision_center import build as center

def main():
    source=ROOT/'data'/'Sales_Transactions_Dataset_Weekly.csv'
    out=ROOT/'outputs'
    if not source.exists():
        raise FileNotFoundError(
            f'Data file missing: {source}. Read docs/DATA.en.md / docs/DATA.es.md.'
        )
    chosen=run(source,out)
    decision(source,out)
    portfolio(source,out)
    queue=center(source,out)
    print(f'Reproduced: global model={chosen}, review queue={len(queue)} products')

if __name__=='__main__':
    main()
