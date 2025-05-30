import mysql.connector
import pandas as pd
from dotenv import load_dotenv
import os

class Database:
    def __init__(self, db_name="Formierung"):
        load_dotenv()
        self.conn = mysql.connector.connect(
            host=os.getenv("DB_HOST") ,
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=db_name
        )
        self.cur = self.conn.cursor()

    def create_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Datapoints (
                hash VARCHAR(255) PRIMARY KEY,
                QAh INT,
                SOC INT,
                Calc_ImA INT,
                Cycle INT,
                EcellV DOUBLE,
                freqHz DOUBLE,
                TemperatureC DOUBLE,
                ZOhm DOUBLE,
                PhaseZdeg DOUBLE,
                calc_ReZOhm DOUBLE,
                calc_ImZOhm DOUBLE,      
                QchargemAh DOUBLE,
                CapacitymAh DOUBLE,
                QQomAh DOUBLE,
                EnergyWh DOUBLE,
                ImA DOUBLE,
                times DOUBLE,
                calc_times DOUBLE,
                Datei VARCHAR(255),
                Typ VARCHAR(255),
                Zelle VARCHAR(255)
            )
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Niquist (
                hash VARCHAR(255) PRIMARY KEY,
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
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Zellen (
                hash VARCHAR(255) PRIMARY KEY,
                id INTEGER PRIMARY KEY,
                Cycle INT,
                QMax REAL,
                Info VARCHAR(255)
            )
        """)
        self.conn.commit()

    def df_in_DB(self, df, table_name):
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

    def query(self, sql_query):
        """
        Führt eine SQL-Abfrage aus und gibt die Ergebnisse zurück.

        :param sql_query: Die SQL-Abfrage als String.
        :return: Ergebnisse der Abfrage als Liste von Tupeln.
        """
        self.cur.execute(sql_query)
        data = self.cur.fetchall()
        try:
            columns = [desc[0] for desc in self.cur.description]
            df = pd.DataFrame(data, columns=columns)
            return df
        except Exception:
            return data

    def close(self):
        self.conn.close()
