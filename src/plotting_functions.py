import re
import xml.etree.ElementTree as ET

colors = {
        'TUM:Extended:Violet': '#69085a',  # Violett
        'TUM:Extended:Navy': '#0f1a5f',  # Dunkelblau / Indigo
        'TUM:Primary:Blue': '#0073cf',  # Blau
        'TUM:Extended:Teal': '#00778a',  # Türkis / Cyan
        'TUM:Extended:Forest': '#007c30',  # Grün
        'TUM:Extended:Lime': '#679a1d',  # Gelbgrün
        'TUM:Extended:Goldenrod': '#f9ba00',  # Dunkelgelb
        'TUM:Extended:Pumpkin': '#d64c13',  # Rötliches Orange
        'TUM:Extended:Maroon': '#9c0d16',  # Dunkelrot, noch unter Rot
        'TUM:Extended:Red': '#c4071b'  # Rot
    }

def extract_sort_keys(name):  #TODO: Muss geändert werden
    # Suche nach den relevanten Zahlen
    cycle_match = re.search(r'Cycle_(\d+)', name)
    qcell_match = re.search(r'Qcell_(\d+)', name)
    ima_match = re.search(r'ImA_(\d+)', name)

    # Wandle zu int um, wenn gefunden – sonst fallback auf eine große Zahl
    cycle = int(cycle_match.group(1)) if cycle_match else float('inf')
    qcell = int(qcell_match.group(1)) if qcell_match else float('inf')
    ima = int(ima_match.group(1)) if ima_match else float('inf')

    return (cycle, qcell, ima)

def get_linestyles():
    color_list = list(colors.values())
    line_styles = ['solid', 'dash', 'dot', 'dashdot']
    dot_styles = ['circle', 'square', 'diamond', 'cross']
    combination_line = []
    combimation_dot = []
    for style in line_styles:
        for name, hex_value in colors.items():
            combination_line.append({
                'color': hex_value,
                'line_style': style
            })
    for marker in dot_styles:
        for name, hex_value in colors.items():
            combimation_dot.append({
                'color': hex_value,
                'marker_type': marker
            })
    return combination_line, combimation_dot

