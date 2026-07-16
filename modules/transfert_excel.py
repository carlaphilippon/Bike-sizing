# -*- coding: utf-8 -*-
"""
Module gérant les interactions avec le fichier Excel raw_data.xlsx.
Lecture de l'échelle et écriture sécurisée des coordonnées.
"""
import os
import shutil
from openpyxl import load_workbook
from modules.configuration import COLONNES_VELO
from modules.utils import valider_chemin

def creer_sauvegarde_securite(chemin_original, chemin_backup):
    """
    Crée une copie de sécurité de l'Excel d'origine.
    Input: chemin_original (str), chemin_backup (str)
    Output: bool (True si succès)
    """
    try:
        shutil.copy2(chemin_original, chemin_backup)
        print("[SÉCURITÉ] Copie Excel de sauvegarde créée.")
        return True
    except Exception as e:
        print(f"[ATTENTION] Échec de la sauvegarde : {e}")
        return False

def trouver_ligne_candidat(ws, candidat):
    """
    Cherche la ligne du candidat dans la colonne B.
    Input: ws (Worksheet openpyxl), candidat (str)
    Output: int (numéro de ligne) ou None
    """
    for row in range(2, ws.max_row + 1):
        cell_val = ws.cell(row=row, column=2).value
        if cell_val and str(cell_val).strip().upper() == str(candidat).strip().upper():
            return row
    return None

def recuperer_distance_roues_excel(chemin_excel, candidat):
    """
    Récupère la distance de calibration en colonne D (colonne 4).
    Input: chemin_excel (str), candidat (str)
    Output: float (distance en mm) ou None
    """
    if not valider_chemin(chemin_excel, "Fichier Excel"):
        return None
    try:
        wb = load_workbook(chemin_excel, data_only=True)
        ws = wb.active
        ligne = trouver_ligne_candidat(ws, candidat)
        if not ligne:
            return None
        
        valeur = ws.cell(row=ligne, column=4).value
        if valeur and float(valeur) > 0:
            return float(valeur)
        return None
    except Exception as e:
        print(f"[ERREUR EXCEL] Lecture de la distance : {e}")
        return None

def completer_raw_data_excel_velo(chemin_excel, chemin_backup, candidat, coords_velo_mm):
    """
    Écrit les coordonnées du vélo dans le fichier Excel.
    Input: chemin_excel (str), chemin_backup (str), candidat (str), coords_velo_mm (dict)
    Output: None
    """
    if not valider_chemin(chemin_excel, "Fichier Excel global"):
        return
    if not creer_sauvegarde_securite(chemin_excel, chemin_backup):
        return

    try:
        wb = load_workbook(chemin_excel)
        ws = wb.active
        ligne = trouver_ligne_candidat(ws, candidat)

        if not ligne:
            print(f"[ERREUR] Candidat '{candidat}' introuvable dans l'Excel.")
            return

        print("[EXCEL] Remplissage des coordonnées du vélo...")
        for composant, coords in coords_velo_mm.items():
            if composant in COLONNES_VELO:
                col_x = COLONNES_VELO[composant]["X"]
                col_y = COLONNES_VELO[composant]["Y"]
                
                ws[f"{col_x}{ligne}"].value = coords[0]
                ws[f"{col_y}{ligne}"].value = coords[1]
                ws[f"{col_x}{ligne}"].number_format = '0.00'
                ws[f"{col_y}{ligne}"].number_format = '0.00'
                
        wb.save(chemin_excel)
        print(f"[OK] Fichier Excel mis à jour pour {candidat} (Vélo).")
        
    except PermissionError:
        print("[ERREUR] Impossible d'écrire. Fermez raw_data.xlsx s'il est ouvert !")

def completer_raw_data_excel_cycliste(chemin_excel, candidat, numero_test, position_dossier, coords_cycliste_pixels, px_par_mm):
    """
    Écrit les coordonnées en mm du cycliste pour un test et une position donnés.
    
    Input:
    ------
    chemin_excel : str (Chemin du fichier)
    candidat : str (Nom du candidat, ex: "WR00")
    numero_test : int (1, 2 ou 3)
    position_dossier : str ("pos_0_deg", "pos_90_deg", etc.)
    coords_cycliste_pixels : dict (Coordonnées pixels issues du pointage)
    px_par_mm : float (L'échelle calculée lors de l'étape vélo)
    """
    from modules.configuration import COLONNES_TESTS, INDEX_POINTS_ANATOMIQUES
    from modules.utils import incrementer_colonne_excel
    
    try:
        wb = load_workbook(chemin_excel)
        ws = wb.active
        ligne = trouver_ligne_candidat(ws, candidat)

        if not ligne:
            print(f"[ERREUR] Candidat '{candidat}' introuvable pour le cycliste.")
            return

        # 1. On récupère la colonne de départ pour ce Test et cette Position (ex: 'Q' pour Test 1, pos_0_deg)
        colonne_depart = COLONNES_TESTS[numero_test][position_dossier]

        # 2. On écrit "Test 1" (ou 2, ou 3) dans la colonne juste avant la colonne de départ si c'est pos_0_deg
        if position_dossier == "pos_0_deg":
            col_label = incrementer_colonne_excel(colonne_depart, -1)
            ws[f"{col_label}{ligne}"].value = f"Test {numero_test}"

        # 3. Écriture des coordonnées en mm
        for articulation, (x_px, y_px) in coords_cycliste_pixels.items():
            if articulation in INDEX_POINTS_ANATOMIQUES:
                # Chaque point est espacé de 2 colonnes (X et Y)
                offset_colonnes = INDEX_POINTS_ANATOMIQUES[articulation] * 2
                
                # Calcul des lettres de colonnes exactes
                col_x = incrementer_colonne_excel(colonne_depart, offset_colonnes)
                col_y = incrementer_colonne_excel(colonne_depart, offset_colonnes + 1)

                # Conversion pixel -> mm (En utilisant l'échelle du vélo)
                x_mm = x_px / px_par_mm
                y_mm = y_px / px_par_mm

                # Injection dans Excel
                ws[f"{col_x}{ligne}"].value = round(x_mm, 2)
                ws[f"{col_y}{ligne}"].value = round(y_mm, 2)
                ws[f"{col_x}{ligne}"].number_format = '0.00'
                ws[f"{col_y}{ligne}"].number_format = '0.00'

        wb.save(chemin_excel)
        print(f"   [OK] Données Excel enregistrées pour {position_dossier} (Test {numero_test}).")

    except PermissionError:
        print(f"[ERREUR] Impossible d'écrire le cycliste. Fermez raw_data.xlsx !")
    except Exception as e:
        print(f"[ERREUR INCONNUE Excel Cycliste] : {e}")