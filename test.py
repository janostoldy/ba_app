import pandas as pd

df = pd.DataFrame([{
            "hash": "hash",
            "id": "SN0001",
            "Cycle": 3,
            "QMax": 3000,
            "Info": "test"
        }])

print(df.hash[0])