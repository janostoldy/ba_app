import sqlite3

Spalten = [
    'QAh',
    'Calc_ImA',
    'Zyklus',
    'EcellV',
    'freqHz',
    'PhaseZdeg',
    'TemperatureC',
    'ImZOhm',
    'ReZOhm',
    'ReYOhm1',
    'ImYOhm1',
    'YOhm1',
    'PhaseYdeg',
    'QdischargemAh',
    'QchargemAh',
    'CapacitymAh',
    'QQomAh',
    'ImA',
    'Times',
    'Messung'
]

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
            PhaseZdeg REAL,
            TemperatureC REAL,
            ImZOhm REAL,
            ReZOhm REAL,
            ReYOhm1 REAL,
            ImYOhm1 REAL,
            YOhm1 REAL,
            PhaseYdeg REAL,
            QdischargemAh REAL,
            QchargemAh REAL,
            CapacitymAh REAL,
            QQomAh REAL,
            ImA REAL,
            Times REAL,
            Messung Char
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
            feeq_Min REAL,
            Im_Max REAL,
            Re_Max REAL,
            feeq_Max REAL
        )
        """)
    conn.commit()
    conn.close()


def df_in_sqlite(df, db_path, table_name):
    # Verbindung zur SQLite-Datenbank
    conn = sqlite3.connect(db_path)

    # Schreibe den DataFrame in die Datenbank
    df.to_sql(table_name, conn, if_exists='append', index=False)

    # Verbindung schließen
    conn.close()


def save_Datapoints(werte, db_name="auswertung.db"):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("INSERT INTO Datapoints  VALUES (?)", (werte))
    conn.commit()
    conn.close()
