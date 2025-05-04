import sqlite3

class Database:
    def __init__(self, db_name="Eis_Analyse.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()

    def create_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Datapoints (
                id INTEGER PRIMARY KEY,
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
        # Filtere die Spalten des DataFrames, die in der Datenbank existieren
        db_columns = [row[1] for row in self.cur.execute(f"PRAGMA table_info({table_name})").fetchall()]
        df = df[[col for col in df.columns if col in db_columns]]

        for _, row in df.iterrows():
            # Überprüfe, ob ein Eintrag mit derselben Messung existiert
            self.cur.execute(f"SELECT id FROM {table_name} WHERE Messung = ? AND freqHz = ?", (row['Messung'],row['freqHz'],))
            existing_row = self.cur.fetchone()

            if existing_row:
                # Aktualisiere den vorhandenen Eintrag
                update_query = f"UPDATE {table_name} SET " + ", ".join([f"{col} = ?" for col in row.index if col != 'Messung']) + " WHERE Messung = ? AND freqHz = ?"
                self.cur.execute(update_query, (*[row[col] for col in row.index if col != 'Messung'], row['Messung'],row['freqHz']))
            else:
                # Füge einen neuen Eintrag hinzu
                row.to_frame().T.to_sql(table_name, self.conn, if_exists='append', index=False)

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
