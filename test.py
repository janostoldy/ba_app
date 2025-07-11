import pandas as pd
from sqlalchemy import create_engine

# Verbindungen definieren
mysql_engine = create_engine("mysql+pymysql://root:Schildkr0te@localhost:3306/Formierung")
postgres_engine = create_engine("postgresql://postgres:Schildkr0te@localhost:5432/Battary_DB")

# Tabellenname, die du migrieren willst
table_name = "Zellen"

# Tabelle aus MySQL lesen
df = pd.read_sql_table(table_name, con=mysql_engine)

# In PostgreSQL schreiben (append oder replace)
df.to_sql(table_name, con=postgres_engine, if_exists="replace", index=False)

print(f"✅ Tabelle '{table_name}' erfolgreich übertragen.")