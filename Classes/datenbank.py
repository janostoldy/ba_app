import mysql.connector
import pandas as pd
from dotenv import load_dotenv
import os

from app_pages import kapa


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
            CREATE TABLE IF NOT EXISTS EIS (
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
            CREATE TABLE IF NOT EXISTS EIS_Points (
                SoC INT,
                Calc_ImA INT,
                Im_Min REAL,
                Re_Min REAL,
                freq_Min REAL,
                Im_Max REAL,
                Re_Max REAL,
                freq_Max REAL,
                Datei VARCHAR(255)
            )
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Kapa (
                QMax REAL,
                Info VARCHAR(255),
                Datei VARCHAR(255) PRIMARY KEY
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
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS DVA (              
                Datei VARCHAR(255),
´               TemperatureC DOUBLE,
                QchargemAh DOUBLE,
                CapacitymAh DOUBLE,
                QQomAh DOUBLE,
                EnergyWh DOUBLE,
                ImA DOUBLE,
                times DOUBLE,
                EcellV DOUBLE,
                QQomAh_smoove DOUBLE,
                EcellV_smoove DOUBLE,
                calc_dV_dQ DOUBLE,
                PRIMARY KEY (Datei, times)
            );
        """)
        self.cur.execute("""
             CREATE TABLE IF NOT EXISTS DVA_Points (
                 Datei         VARCHAR(255),
                 Point         VARCHAR(10),
                 Value         DOUBLE,
                 X_Start       DOUBLE,
                 X_END         DOUBLE,
                 PRIMARY KEY (Datei, Point)
             );
             """)
        self.cur.execute("""
             CREATE TABLE IF NOT EXISTS Zellen
             (
                 id   VARCHAR(20) PRIMARY KEY,
                 Typ   VARCHAR(20),
                 Cycle INT,
                 Info VARCHAR(255)
             );
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

        # SQL UPSERT-Vorbereitung
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

    def insert_file(self, file, cycle, Info="", Zelle="", Typ=""):
        sql = """
            INSERT INTO Files (name, Datum, Info, Cycle, Zelle, Typ)
            VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            Info = VALUES(Info), Datum = CURRENT_TIMESTAMP, Cycle = VALUES(Cycle), Zelle = VALUES(Zelle), Typ = VALUES(Typ)
        """
        values = (file, Info, cycle, Zelle, Typ)
        try:
            self.cur.execute(sql, values)
            self.conn.commit()
            return None
        except Exception as e:
            return e

    def delete_file(self, file):
        tables = ["EIS", "Files", "Kapa", "EIS_Points", "DVA", "DVA_Points"]
        for table in tables:
            if table == "EIS":
                sql = f"DELETE FROM {table} WHERE Datei=%s"
                self.cur.execute(sql, (file,))
            elif table == "Files":
                sql = f"DELETE FROM {table} WHERE name=%s"
                self.cur.execute(sql, (file,))
            elif table == "Kapa":
                sql = f"DELETE FROM {table} WHERE Datei=%s"
                self.cur.execute(sql, (file,))
            elif table == "EIS_Points":
                sql = f"DELETE FROM {table} WHERE Datei=%s"
                self.cur.execute(sql, (file,))
            elif table == "DVA":
                sql = f"DELETE FROM {table} WHERE Datei=%s"
                self.cur.execute(sql, (file,))
            elif table == "DVA_Points":
                sql = f"DELETE FROM {table} WHERE Datei=%s"
                self.cur.execute(sql, (file,))
        self.conn.commit()

    def get_all_files(self):
        return self.query("SELECT * FROM Files")

    def get_all_eingang(self):
        sql = "SELECT * FROM Files WHERE Typ!='Ageing'"
        return self.query(sql)

    def get_file(self, cycle, zelle, typ):
        if typ == "*":
            sql = f"""SELECT * FROM Files WHERE Cycle=%s AND Zelle=%s"""
            values = (cycle, zelle)
        else:
            sql = f"""SELECT * FROM Files WHERE Cycle=%s AND Zelle=%s AND Typ=%s"""
            values = (cycle, zelle, typ)
        return self.query(sql, values)

    def get_file_typs(self):
        sql = f"""SELECT DISTINCT Typ FROM Files """
        return self.query(sql)

    def get_all_zells(self):
        return self.query("SELECT * FROM Zellen")

    def update_zelle(self, Zelle, cycle):
        sql = f"""UPDATE Zellen SET Cycle=%s WHERE id=%s"""
        params = (cycle, Zelle)
        self.cur.execute(sql, params)
        self.conn.commit()

    def get_kapa_cycles(self):
        return self.query("SELECT DISTINCT Cycle FROM Files WHERE Typ='Kapa'")

    def get_zell_cycle(self, zelle, Max=True):
        return self.query("SELECT Cycle FROM Zellen WHERE id = %s", (zelle,))

    def delete_zell(self, id):
        """
            Lösche eine Zelle aus der Tabelle Zellen.

            :param hash: Hash Wert der Zelle, die geupdated wird.
        """
        sql = """
        DELETE FROM Zelle
        WHERE id = %s
        """
        values = (id,)
        try:
            self.cur.execute(sql, values)
            self.conn.commit()
            return None
        except Exception as e:
            return e

    def get_all_kapa(self):
        sql = "SELECT * FROM Files WHERE Typ = 'Kapa'"
        return self.query(sql)

    def get_kapa(self, Datei):
        sql = """SELECT Kapa.Datei, Kapa.Kapa, Kapa.Info, Files.Datum, Files.Cycle, Files.Zelle 
                 FROM Kapa INNER JOIN Files ON Kapa.Datei=Files.name 
                 WHERE Datei=%s"""
        params = (Datei,)
        return self.query(sql, params=params)

    def get_all_dva(self):
        sql = "SELECT * FROM Files WHERE Typ = 'DVA'"
        return self.query(sql)

    def get_dva(self, Datei):
        params = (Datei,)
        sql = "SELECT * FROM DVA WHERE Datei = %s"
        data = self.query(sql, params=params)
        sql = "SELECT * FROM DVA_Points WHERE Datei = %s"
        points = self.query(sql, params=params)
        return data, points

    def get_all_eis(self):
        sql = "SELECT * FROM Files WHERE Typ = 'EIS'"
        return self.query(sql)

    def get_all_eis_soc(self):
        sql = ("SELECT DISTINCT SoC FROM Eis_Points ")
        return self.query(sql)

    def get_eis_points(self, Datei, soc):
        params = (Datei,soc)
        sql = """SELECT EIS_Points.*, Files.Datum, Files.Cycle, Files.Zelle
                 FROM EIS_Points INNER JOIN Files ON EIS_Points.Datei=Files.name 
                 WHERE EIS_Points.Datei = %s AND EIS_Points.SoC = %s"""
        return self.query(sql, params=params)

    def get_eis_plots(self, Datei, soc):
        params = (Datei,soc)
        sql = """SELECT EIS.*, Files.Datum, Files.Cycle, Files.Zelle
                 FROM EIS INNER JOIN Files ON EIS.Datei = Files.name
                 WHERE EIS.Datei = %s AND EIS.SoC = %s"""
        return self.query(sql, params=params)


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
