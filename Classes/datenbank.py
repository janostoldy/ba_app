import pandas as pd
import streamlit as st
from sqlalchemy import text

class Database:
    def __init__(self, db_name="Formierung"):
        self.name = db_name

    def create_table(self):
        conn = st.connection("sql", type="sql")
        with conn.session as s:
            s.execute("""
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
            s.execute("""
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
            s.execute("""
                CREATE TABLE IF NOT EXISTS Kapa (
                    QMax REAL,
                    Info VARCHAR(255),
                    Datei VARCHAR(255) PRIMARY KEY
                )
            """)
            s.execute("""
                CREATE TABLE IF NOT EXISTS Files (
                    name  VARCHAR(255) PRIMARY KEY,
                    Datum Date,
                    Info  VARCHAR(255),
                    Cycle INT,
                    Zelle VARCHAR(255)
                )
            """)
            s.execute("""
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
            s.execute("""
                 CREATE TABLE IF NOT EXISTS DVA_Points (
                     Datei         VARCHAR(255),
                     Point         VARCHAR(10),
                     Value         DOUBLE,
                     X_Start       DOUBLE,
                     X_END         DOUBLE,
                     PRIMARY KEY (Datei, Point)
                 );
                 """)
            s.execute("""
                 CREATE TABLE IF NOT EXISTS Zellen
                 (
                     id   VARCHAR(20) PRIMARY KEY,
                     Typ   VARCHAR(20),
                     Cycle INT,
                     Info VARCHAR(255)
                 );
                 """)
            s.commit()

    def df_in_DB(self, df, table_name):
        """
        Fügt einen DataFrame in die angegebene Tabelle der Datenbank ein (mit UPSERT-Logik für MySQL).

        - Prüft, ob die Spalten des DataFrames mit denen der Tabelle übereinstimmen.
        - Erwartet eine Spalte 'hash' als eindeutigen Schlüssel.
        - Nutzt Batch-Insert für Effizienz.
        - Bei Konflikt (gleicher 'hash') werden die Werte aktualisiert.
        """

        # Hol Spaltennamen aus der Datenbank (als Liste)
        conn = st.connection("sql", type="sql")
        result = conn.query(
            """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = :table
              AND TABLE_SCHEMA = 'Formierung'
            """,
            params={"table": table_name}
        )
        db_columns = [row["COLUMN_NAME"] for row in result]

        # Nur Spalten einfügen, die in der Tabelle existieren
        df = df[[col for col in df.columns if col in db_columns]]

        if df.empty:
            return

        columns = df.columns.tolist()
        placeholders = ", ".join([f":{col}" for col in columns])
        update_clause = ", ".join([f"{col} = VALUES({col})" for col in columns if col != 'hash'])

        sql = f"""
        INSERT INTO {table_name} ({", ".join(columns)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
        """

        # Daten als Liste von Dictionaries vorbereiten
        data_dicts = df.to_dict(orient="records")

        with conn.session as s:
            s.execute(sql, data_dicts)
            s.commit()

    def insert_file(self, file, cycle, Info="", Zelle="", Typ=""):
        conn = st.connection("sql", type="sql")
        sql = """
            INSERT INTO Files (name, Datum, Info, Cycle, Zelle, Typ)
            VALUES (:name, CURRENT_TIMESTAMP, :info, :cycle, :zelle, :typ)
            ON DUPLICATE KEY UPDATE 
            Info = VALUES(Info), Datum = CURRENT_TIMESTAMP, Cycle = VALUES(Cycle), Zelle = VALUES(Zelle), Typ = VALUES(Typ)"""
        values = {"name": file, "info": Info, "cycle": cycle, "zelle": Zelle, "typ": Typ}
        with conn.session as s:
            s.execute(sql, values)
            s.commit()


    def delete_file(self, file):
        conn = st.connection("sql", type="sql")
        tables = ["EIS", "Files", "Kapa", "EIS_Points", "DVA", "DVA_Points"]
        with conn.session as s:
            for table in tables:
                if table == "EIS":
                    sql = f"DELETE FROM {table} WHERE Datei = :file"
                    s.execute(sql, {"file": file})
                elif table == "Files":
                    sql = f"DELETE FROM {table} WHERE name = :file"
                    s.execute(sql, {"file": file})
                elif table == "Kapa":
                    sql = f"DELETE FROM {table} WHERE Datei = :file"
                    s.execute(sql, {"file": file})
                elif table == "EIS_Points":
                    sql = f"DELETE FROM {table} WHERE Datei = :file"
                    s.execute(sql, {"file": file})
                elif table == "DVA":
                    sql = f"DELETE FROM {table} WHERE Datei = :file"
                    s.execute(sql, {"file": file})
                elif table == "DVA_Points":
                    sql = f"DELETE FROM {table} WHERE Datei = :file"
                    s.execute(sql, {"file": file})
            s.commit()

    def get_all_files(self):
        conn = st.connection("sql", type="sql")
        return conn.query("SELECT * FROM Files")

    def get_all_eingang(self):
        conn = st.connection("sql", type="sql")
        sql = "SELECT * FROM Files WHERE Typ!='Ageing'"
        return conn.query(sql)

    def get_file(self, cycle, zelle, typ):
        conn = st.connection("sql", type="sql")
        if typ == "*":
            sql = "SELECT * FROM Files WHERE Cycle=:cycle AND Zelle=:zelle"
            values = {"cycle": cycle, "zelle": zelle}
        else:
            sql = "SELECT * FROM Files WHERE Cycle=:cycle AND Zelle=:zelle AND Typ=:typ"
            values = {"cycle": cycle, "zelle": zelle, "typ": typ}
        with conn.session as s:
            file = s.execute(text(sql), params=values).fetchall()
            return pd.DataFrame(file)

    def get_file_typs(self):
        conn = st.connection("sql", type="sql")
        sql = f"""SELECT DISTINCT Typ FROM Files """
        return conn.query(sql)

    def get_all_zells(self):
        conn = st.connection("sql", type="sql")
        return conn.query("SELECT * FROM Zellen")

    def update_zelle(self, Zelle, cycle):
        conn = st.connection("sql", type="sql")
        sql = "UPDATE Zellen SET Cycle = :cycle WHERE id = :zelle"
        params = {"cycle": cycle, "zelle": Zelle}
        with conn.session as s:
            s.execute(sql, params)
            s.commit()

    def get_kapa_cycles(self):
        conn = st.connection("sql", type="sql")
        return conn.query("SELECT DISTINCT Cycle FROM Files WHERE Typ='Kapa'")

    def get_zell_cycle(self, zelle, Max=True):
        conn = st.connection("sql", type="sql")
        sql = "SELECT Cycle FROM Zellen WHERE id = :zelle"
        params = {"zelle": zelle}
        return conn.query(sql, params=params)

    def delete_zell(self, id):
        """
            Lösche eine Zelle aus der Tabelle Zellen.

            :param hash: Hash Wert der Zelle, die geupdated wird.
        """
        conn = st.connection("sql", type="sql")
        sql = "DELETE FROM Zellen WHERE id = :id"
        params = {"id": id}
        with conn.session as s:
            s.execute(sql, params)
            s.commit()

    def get_all_kapa(self):
        conn = st.connection("sql", type="sql")
        sql = "SELECT * FROM Files WHERE Typ = 'Kapa'"
        return conn.query(sql)

    def get_kapa(self, Datei):
        conn = st.connection("sql", type="sql")
        sql = """SELECT Kapa.Datei, Kapa.Kapa, Kapa.Info, Files.Datum, Files.Cycle, Files.Zelle
                     FROM Kapa INNER JOIN Files ON Kapa.Datei=Files.name
                     WHERE Kapa.Datei = :datei"""
        params = {"datei": Datei}
        with conn.session as s:
           result = s.execute(text(sql), params).fetchall()
        return result

    def get_all_dva(self):
        conn = st.connection("sql", type="sql")
        sql = "SELECT * FROM Files WHERE Typ = 'DVA'"
        return conn.query(sql)
    def get_dva(self, Datei):
        conn = st.connection("sql", type="sql")
        sql1 = "SELECT * FROM DVA WHERE Datei = :datei"
        sql2 = "SELECT * FROM DVA_Points WHERE Datei = :datei"
        params = {"datei": Datei}
        with conn.session as s:
            data = s.execute(text(sql1), params).fetchall()
            points = s.execute(text(sql2), params).fetchall()
        return data, points

    def get_all_eis(self):
        conn = st.connection("sql", type="sql")
        sql = "SELECT * FROM Files WHERE Typ = 'EIS'"
        return conn.query(sql)

    def get_all_eis_soc(self):
        conn = st.connection("sql", type="sql")
        sql = ("SELECT DISTINCT SoC FROM Eis_Points ")
        return conn.query(sql)

    def get_eis_points(self, Datei, soc):
        conn = st.connection("sql", type="sql")
        sql = """SELECT EIS_Points.*, Files.Datum, Files.Cycle, Files.Zelle
                      FROM EIS_Points INNER JOIN Files ON EIS_Points.Datei=Files.name 
                      WHERE EIS_Points.Datei = :datei AND EIS_Points.SoC = :soc"""
        params = {"datei": Datei, "soc": soc}
        with conn.session as s:
            result = s.execute(text(sql), params).fetchall()
        return result

    def get_eis_plots(self, Datei, soc):
        conn = st.connection("sql", type="sql")
        sql = """SELECT EIS.*, Files.Datum, Files.Cycle, Files.Zelle
                      FROM EIS INNER JOIN Files ON EIS.Datei = Files.name
                      WHERE EIS.Datei = :datei AND EIS.SoC = :soc"""
        params = {"datei": Datei, "soc": soc}
        with conn.session as s:
            result = s.execute(text(sql), params).fetchall()
        return result
