import os

def highlight_status(val):
    if val == "In Datenbank":
        return "background-color: #80bd98"
    elif val == "Neu":
        return "background-color: #ffee80"
    if val == "Fehlende Daten":
        return "background-color: #e2838d"
    return ""


def status_func(f,gespeicherte_dateien,folder,):
    if f in gespeicherte_dateien:
        return "In Datenbank"
    elif round(os.path.getsize(os.path.join(folder, f)) / 1024) < 20:
        return "Fehlende Daten"
    else:
        return "Neu"