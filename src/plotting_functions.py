import re
import xml.etree.ElementTree as ET

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

def extract_colors_from_soc(file_path):
    colors = {}
    # Namespace definieren
    namespaces = {'draw': 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0'}

    tree = ET.parse(file_path)
    root = tree.getroot()

    # Iteriere über alle `draw:color`-Elemente
    for color in root.findall('.//draw:color', namespaces):
        color_name = color.get('{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}name')  # Vollständiger Namespace
        color_value = color.get('{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}color')  # Vollständiger Namespace
        if color_name and color_value:
            colors[color_name] = color_value

    return colors

def Get_Colors():
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

