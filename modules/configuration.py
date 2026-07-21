# -*- coding: utf-8 -*-
"""
Module de configuration générale du projet Bike Sizing.
Contient les chemins d'accès, les listes de points et les cartographies Excel.
"""

# --- CHEMINS GENERAUX ---
RACINE_DRIVE = r"H:\Mon Drive\Project\data\images_video"

# --- CONFIGURATION DU VELO ---
POINTS_VELO = ["Pedale", "Centre_Pedalier", "Selle", "Guidon"]

# Cartographie Excel des coordonnées du vélo (colonnes KI à KT)
COLONNES_VELO = {
    "Selle":           {"X": "KI", "Y": "KJ"},
    "Guidon":          {"X": "KK", "Y": "KL"},  
    "Roue arrière":    {"X": "KM", "Y": "KN"},  
    "Roue avant":      {"X": "KO", "Y": "KP"}, 
    "Pedale":          {"X": "KQ", "Y": "KR"}, 
    "Centre_Pedalier": {"X": "KS", "Y": "KT"} 
}

# --- CONFIGURATION DU CYCLISTE ---
POINTS_ANATOMIQUES = ["Pied", "Cheville", "Genou", "Hanche", "Epaule", "Coude", "Poignet"]

# Dossiers d'analyses des positions
POSITIONS_DOSSIERS = ["pos_0_deg", "pos_90_deg", "pos_180_deg", "pos_270_deg"]

# Décalages de colonnes de base pour chaque position anatomique
# Q=colonne 17 (Pied X), R=colonne 18 (Pied Y) etc.
# L'écart entre chaque articulation est de 2 colonnes (X et Y)
INDEX_POINTS_ANATOMIQUES = {
    "Pied": 0,       # X en Q, Y en R
    "Cheville": 1,   # X en S, Y en T
    "Genou": 2,      # X en U, Y en V
    "Hanche": 3,     # X en W, Y en X
    "Epaule": 4,     # X en Y, Y en Z
    "Coude": 5,      # X en AA, Y en AB
    "Poignet": 6     # X en AC, Y en AD
}

# Racines de début de colonnes pour les 3 tests (1er point de pos_0_deg)
# Test 1 : pos_0_deg commence en Q (colonne 17).
# On définit l'index de départ pour chaque position et chaque test dans l'Excel
COLONNES_TESTS = {
    1: {  # Test 1 (P à DB)
        "pos_0_deg": "Q",    # Pied X en Q, Y en R
        "pos_90_deg": "AN",  # Pied X en AM, Y en AN
        "pos_180_deg": "BK", # Pied X en BI, Y en BJ
        "pos_270_deg": "CH"  # Pied X en CF, Y en CG
    },
    2: {  # Test 2 (DE à GQ)
        "pos_0_deg": "DH",   # Pied X en DF, Y en DG
        "pos_90_deg": "EE",
        "pos_180_deg": "FB",
        "pos_270_deg": "FY"
    },
    3: {  # Test 3 (GU à KG)
        "pos_0_deg": "GZ",   # Pied X en GV, Y en GW
        "pos_90_deg": "HW",
        "pos_180_deg": "IT",
        "pos_270_deg": "JR"
    }
}