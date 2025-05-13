import sqlite3

class Database:
    def __init__(self, db_name="Eis_Analyse.db", db_path=""):
        self.db_name = db_name
        self.db_path = db_path if db_path else "./"
        self.full_path = f"/{self.db_path.rstrip('/')}/{self.db_name}"
        self.conn = sqlite3.connect(self.full_path)
        self.cur = self.conn.cursor()

    def create_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Datapoints (
                hash TEXT PRIMARY KEY,
                QAh INT,
                Calc_ImA INT,
                Cycle INT,
                EcellV REAL,
                freqHz REAL,
                TemperatureC REAL,
                ZOhm REAL,
                PhaseZdeg REAL,
                calc_ReZOhm REAL,
                calc_ImZOhm REAL,      
                QchargemAh REAL,
                CapacitymAh REAL,
                QQomAh REAL,
                EnergyWh REAL,
                ImA REAL,
                times REAL,
                calc_times REAL,
                Datei VARCHAR,
                Typ VARCHAR
                Zelle VARCHAR
            )
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Niquist (
                hash TEXT PRIMARY KEY,
                QAh INT,
                Calc_ImA INT,
                Zyklus INT,
                Im_Min REAL,
                Re_Min REAL,
                freq_Min REAL,
                Im_Max REAL,
                Re_Max REAL,
                freq_Max REAL
            )
        """)
        self.conn.commit()

    def df_in_sqlite(self, df, table_name):
        # Prüfe Spalten der Datenbank
        db_columns = [row[1] for row in self.cur.execute(f"PRAGMA table_info({table_name})").fetchall()]
        df = df[[col for col in df.columns if col in db_columns]]

        if df.empty:
            return

        # Stelle sicher, dass 'hash' vorhanden ist (Pflicht für UPSERT)
        if 'hash' not in df.columns:
            raise ValueError("DataFrame muss eine 'hash'-Spalte enthalten.")

        # SQLite UPSERT-Vorbereitung
        columns = df.columns.tolist()
        placeholders = ", ".join(["?"] * len(columns))
        update_clause = ", ".join([f"{col}=excluded.{col}" for col in columns if col != 'hash'])

        sql = f"""
        INSERT INTO {table_name} ({", ".join(columns)})
        VALUES ({placeholders})
        ON CONFLICT(hash) DO UPDATE SET {update_clause}
        """

        # Daten als Liste von Tupeln vorbereiten
        daten = [tuple(row) for row in df.to_numpy()]

        # Batch einfügen (deutlich schneller als einzelne Queries)
        self.cur.executemany(sql, daten)
        self.conn.commit()

    def close(self):
        self.conn.close()
