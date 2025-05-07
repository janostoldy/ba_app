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
                Messung VARCHAR,
                Typ VARCHAR
            )
        """)
        self.conn.commit()

    def df_in_sqlite(self, df, table_name):
        # Hole die Spaltennamen der Zieltabelle aus der Datenbank
        db_columns = [row[1] for row in self.cur.execute(f"PRAGMA table_info({table_name})").fetchall()]

        # Behalte nur Spalten, die in der DB-Tabelle vorhanden sind
        df = df[[col for col in df.columns if col in db_columns]]

        # Optional: Leere DataFrames überspringen
        if df.empty:
            return

        for _, row in df.iterrows():
            row_dict = row.to_dict()

            # Prüfe auf vorhandenen Eintrag anhand des Hash-Schlüssels
            self.cur.execute(f"SELECT 1 FROM {table_name} WHERE hash = ?", (row_dict['hash'],))
            exists = self.cur.fetchone() is not None

            if exists:
                # UPDATE-Anweisung für alle Spalten außer 'hash'
                update_cols = [col for col in row_dict if col != 'hash']
                update_set = ", ".join([f"{col} = ?" for col in update_cols])
                update_values = [row_dict[col] for col in update_cols] + [row_dict['hash']]

                sql = f"UPDATE {table_name} SET {update_set} WHERE hash = ?"
                self.cur.execute(sql, update_values)
            else:
                # INSERT über df.to_sql (schnell & sicher)
                row.to_frame().T.to_sql(table_name, self.conn, if_exists='append', index=False)

        # Alle Änderungen speichern
        self.conn.commit()

    def close(self):
        self.conn.close()

def init_db(db_name="Eis_Analyse.db"):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Datapoints (
            id INTEGER PRIMARY KEY,
            QAh INT,
            Calc_ImA INT,
            Zyklus INT,
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
            Messung VARCHAR,
            Typ VARCHAR
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Bode
        (
            id INTEGER PRIMARY KEY,
            QAh INT,
            Calc_ImA INT,
            Zyklus INT,
            Im_Min REAL,
            Re_Min REAL,
            freq_Min REAL,
            Im_Max REAL,
            Re_Max REAL,
            feeq_Max REAL
        )
        """)
    conn.commit()
    conn.close()


def save_Datapoints(werte, db_name="auswertung.db"):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("INSERT INTO Datapoints  VALUES (?)", (werte))
    conn.commit()
    conn.close()
