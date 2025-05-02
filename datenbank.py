import sqlite3

def init_db(db_name="auswertung.db"):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Datapoints (
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
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Bode
        (
            QAh INT,
            Calc_ImA INT,
            Zyklus INT,
            Im_Min REAL,
            Re_Min REAL,
            feeq_Min REAL,
            Im_Max REAL,
            Re_Max REAL,
            feeq_Max REAL,
        )
        """)
    conn.commit()
    conn.close()

def speichere_ergebnis(dateiname, mittelwert, db_name="auswertung.db"):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("INSERT INTO ergebnisse (dateiname, mittelwert) VALUES (?, ?)", (dateiname, mittelwert))
    conn.commit()
    conn.close()
