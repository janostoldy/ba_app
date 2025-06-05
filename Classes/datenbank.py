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
                Datei VARCHAR(255)
            )
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Zellen (
                hash VARCHAR(255) PRIMARY KEY,
                id VARCHAR(20),
                Cycle INT,
                QMax REAL,
                Info VARCHAR(255),
                Art VARCHAR(20),
                Datei VARCHAR(255)
            )
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Files (
                name  VARCHAR(255) PRIMARY KEY,
                Datum Date,
                Info  VARCHAR(255),
                Cycle INT,
                Zelle VARCHAR(255)
            )
        """)
        self.conn.commit()

    def df_in_DB(self, df, table_name):
        """
        Fügt einen DataFrame in die angegebene Tabelle der Datenbank ein (mit UPSERT-Logik).

        - Prüft, ob die Spalten des DataFrames mit denen der Tabelle übereinstimmen.
        - Erwartet eine Spalte 'hash' als eindeutigen Schlüssel.
        - Nutzt Batch-Insert für Effizienz.
        - Bei Konflikt (gleicher 'hash') werden die Werte aktualisiert.

        :param df: DataFrame mit den einzufügenden Daten.
        :param table_name: Name der Zieltabelle als String.
        """
        # Prüfe Spalten der Datenbank
        self.cur.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
        db_columns = [row[0] for row in self.cur.fetchall()]
        df = df[[col for col in df.columns if col in db_columns]]

        if df.empty:
            return

        # Stelle sicher, dass 'hash' vorhanden ist (Pflicht für UPSERT)
        if 'hash' not in df.columns:
            raise ValueError("DataFrame muss eine 'hash'-Spalte enthalten.")

        # SQLite UPSERT-Vorbereitung
        columns = df.columns.tolist()
        placeholders = ", ".join(["%s"] * len(columns))
        update_clause = ", ".join([f"{col}=VALUES({col})" for col in columns if col != 'hash'])

        sql = f"""
        INSERT INTO {table_name} ({", ".join(columns)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE 
        {update_clause}
        """

        # Daten als Liste von Tupeln vorbereiten
        daten = [tuple(row) for row in df.to_numpy()]

        # Batch einfügen (deutlich schneller als einzelne Queries)
        self.cur.executemany(sql, daten)
        self.conn.commit()

    def insert_file(self, file, cycle, Info="", Zelle=""):
        sql = """
            INSERT INTO Files (name, Datum, Info, Cycle, Zelle)
            VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            Info = VALUES(Info), Datum = CURRENT_TIMESTAMP, Cycle = VALUES(Cycle), Zelle = VALUES(Zelle)
        """
        values = (file, Info, cycle, Zelle)
        try:
            self.cur.execute(sql, values)
            self.conn.commit()
            return None
        except Exception as e:
            return e

    def delete_file(self, file):
        tables = ["Datapoints", "Files", "Zellen", "Niquist"]
        for table in tables:
            if table == "Datapoints":
                sql = f"DELETE FROM {table} WHERE Datei=%s"
                self.cur.execute(sql, (file,))
            elif table == "Files":
                sql = f"DELETE FROM {table} WHERE name=%s"
                self.cur.execute(sql, (file,))
            elif table == "Zellen":
                sql = f"DELETE FROM {table} WHERE Datei=%s"
                self.cur.execute(sql, (file,))
            elif table == "Niquist":
                sql = f"DELETE FROM {table} WHERE Datei=%s"
                self.cur.execute(sql, (file,))
        self.conn.commit()

    def get_all_files(self):
        return self.query("SELECT * FROM Files")

    def get_file(self, cycle, zelle):
        sql = f"""SELECT * FROM Files WHERE Cycle=%s AND Zelle=%s """
        values = (cycle, zelle)
        return self.query(sql, values)

    def get_all_zells(self):
        return self.query("SELECT DISTINCT id FROM Zellen")

    def get_zell_cycle(self, zelle, Max=True):
        if Max:
            return self.query("SELECT MAX(Cycle) FROM Zellen WHERE id = %s", (zelle,))
        else:
            return self.query("SELECT Cycle FROM Zellen WHERE id = %s", (zelle,))

    def insert_zell(self, dic):
        """
            Füge eine Dataframe zu der Tabelle Zellen hinzu

            :param dic: Die zu hinzufügenden Daten als Dictonary.
        """
        sql = """
        INSERT INTO Zellen (hash, id, Cycle, QMax, Info, Art, Datei)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        Info = VALUES(Info)
        """
        values = (dic["hash"], dic["id"], dic["Cycle"], dic["QMax"], dic["Info"], dic["Art"], dic["Datei"])
        try:
            self.cur.execute(sql, values)
            self.conn.commit()
            return None
        except Exception as e:
            return e

    def update_zell(self, dic, hash):
        """
            Update die Werte einer Zelle in der Tabelle Zellen.

            :param dic: Die zu hinzufügenden Daten als Dictonary.
            :param hash: Hash Wert der Zelle, die geupdated wird.
        """
        sql = """
        UPDATE Zellen
        SET hash = %s, id = %s, Cycle = %s, QMax = %s, Info = %s, Art = %s
        WHERE hash = %s
        """
        values = (dic["hash"], dic["id"], dic["Cycle"], dic["QMax"], dic["Info"], dic["Art"], hash)
        try:
            self.cur.execute(sql, values)
            self.conn.commit()
            return None
        except Exception as e:
            return e

    def delete_zell(self, hash):
        """
            Lösche eine Zelle aus der Tabelle Zellen.

            :param hash: Hash Wert der Zelle, die geupdated wird.
        """
        sql = """
        DELETE FROM Zellen
        WHERE hash = %s
        """
        values = (hash,)
        try:
            self.cur.execute(sql, values)
            self.conn.commit()
            return None
        except Exception as e:
            return e

    def get_zellen(self, zellen_id,zellen_cycle):
        sql = "SELECT * FROM Zellen WHERE 1=1"
        params = []
        if zellen_id is not None:
            sql += " AND id = %s"
            params.append(zellen_id)

        if zellen_cycle is not None:
            sql += " AND Cycle = %s"
            params.append(zellen_cycle)

        zellen = self.query(sql, params=params)
        return zellen

    def get_all_niquist(self):
        sql = "SELECT * FROM Niquist"
        return self.query(sql)

    def query(self, sql_query, params=None):
        """
        Führt eine SQL-Abfrage aus und gibt die Ergebnisse zurück.

        :param sql_query: Die SQL-Abfrage als String.
        :param params: Parameter für die Abfrage, optional.
        :return: Ergebnisse der Abfrage als Liste von Tupeln.
        """
        self.cur.execute(sql_query, params)
        data = self.cur.fetchall()
        try:
            columns = [desc[0] for desc in self.cur.description]
            df = pd.DataFrame(data, columns=columns)
            return df
        except Exception:
            return data

    def close(self):
        self.conn.close()
