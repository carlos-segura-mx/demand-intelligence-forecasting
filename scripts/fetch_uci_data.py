"""Retrieve original UCI source and verify its bytes before using the dataset."""
from pathlib import Path
import hashlib
import io
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/"data"/"Sales_Transactions_Dataset_Weekly.csv"
URL="https://archive.ics.uci.edu/static/public/396/sales+transactions+dataset+weekly.zip"
EXPECTED_SHA256="6f939a928c04820bc291a6184f4f1d0be694b8de58d949e808852804f25969c3"

def main():
    with urllib.request.urlopen(URL, timeout=45) as response:
        payload=response.read()
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names=[name for name in archive.namelist() if name.endswith("Sales_Transactions_Dataset_Weekly.csv")]
        if len(names)!=1:
            raise RuntimeError(f"Expected one CSV in official UCI archive, got {names}")
        data=archive.read(names[0])
    checksum=hashlib.sha256(data).hexdigest()
    if checksum!=EXPECTED_SHA256:
        raise ValueError(f"UCI data hash changed: {checksum}. Review source before proceeding.")
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_bytes(data)
    print(f"Verified {DEST.name} from UCI. SHA-256 {checksum}")

if __name__=="__main__":
    main()
