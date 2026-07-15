# -*- coding: utf-8 -*-
from transfert_excel import completer_raw_data_excel

# On crée de fausses coordonnées pour tester le candidat WR00
fausses_coords = {
    "Selle":          (380.10, 710.85),
    "Guidon":        (120.45, 340.12),  
    "Roue arrière":    (450.00, 342.50),  
    "Roue avant":     (380.10, 710.85), 
    "Pedale":         (120.45, 340.12), # Lettres changées pour éviter les doublons
    "Centre pedalier": (450.00, 342.50)  # Lettres changées pour éviter les doublons
}

print("[TEST] Lancement du transfert test pour WR00...")
# On lance la fonction située dans modules/excel.py
completer_raw_data_excel(r"H:\Mon Drive\Project", "WR00", fausses_coords)