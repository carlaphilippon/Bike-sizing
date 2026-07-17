# -*- coding: utf-8 -*-
import os
import shutil
from openpyxl import load_workbook
from modules.configuration import COLONNES_VELO, COLONNES_TESTS, INDEX_POINTS_ANATOMIQUES
from modules.utils import valider_chemin, incrementer_colonne_excel

def creer_sauvegarde_securite(chemin_original, chemin_backup):
    try:
        shutil.copy2(chemin_original, chemin_backup)
        print("[SÉCURITÉ] Copie Excel de sauvegarde créée.")
        return True
    except Exception as e:
        print(f"[ATTENTION] Échec de la sauvegarde : {e}")
        return False

def trouver_ligne_candidat(ws, candidat):
    for row in range(2, ws.max_row + 1):
        cell_val = ws.cell(row=row, column=2).value
        if cell_val and str(cell_val).strip().upper() == str(candidat).strip().upper():
            return row
    return None

def recuperer_distance_roues_excel(chemin_excel, candidat):
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
    if not valider_chemin(chemin_excel, "Fichier Excel global"): return
    if not creer_sauvegarde_securite(chemin_excel, chemin_backup): return

    try:
        wb = load_workbook(chemin_excel)
        ws = wb.active
        ligne = trouver_ligne_candidat(ws, candidat)
        if not ligne: return

        for composant, coords in coords_velo_mm.items():
            if composant in COLONNES_VELO:
                col_x, col_y = COLONNES_VELO[composant]["X"], COLONNES_VELO[composant]["Y"]
                ws[f"{col_x}{ligne}"].value = coords[0]
                ws[f"{col_y}{ligne}"].value = coords[1]
                ws[f"{col_x}{ligne}"].number_format = '0.00'
                ws[f"{col_y}{ligne}"].number_format = '0.00'
                
        wb.save(chemin_excel)
        print(f"[OK] Fichier Excel mis à jour pour {candidat} (Vélo).")
    except PermissionError:
        print("[ERREUR] Impossible d'écrire. Fermez raw_data.xlsx s'il est ouvert !")

def completer_raw_data_excel_cycliste(chemin_excel, candidat, numero_test, position_dossier, coords_cycliste_mm):
    try:
        wb = load_workbook(chemin_excel)
        ws = wb.active
        ligne = trouver_ligne_candidat(ws, candidat)
        if not ligne: return

        colonne_depart = COLONNES_TESTS[numero_test][position_dossier]

        if position_dossier == "pos_0_deg":
            col_label = incrementer_colonne_excel(colonne_depart, -1)
            ws[f"{col_label}{ligne}"].value = f"Test {numero_test}"

        for articulation, (x_mm, y_mm) in coords_cycliste_mm.items():
            if articulation in INDEX_POINTS_ANATOMIQUES:
                offset = INDEX_POINTS_ANATOMIQUES[articulation] * 2
                col_x = incrementer_colonne_excel(colonne_depart, offset)
                col_y = incrementer_colonne_excel(colonne_depart, offset + 1)

                ws[f"{col_x}{ligne}"].value = x_mm
                ws[f"{col_y}{ligne}"].value = y_mm
                ws[f"{col_x}{ligne}"].number_format = '0.00'
                ws[f"{col_y}{ligne}"].number_format = '0.00'

        wb.save(chemin_excel)
        print(f"   [OK] Données Excel enregistrées pour {position_dossier} (Test {numero_test}).")
    except PermissionError:
        print(f"[ERREUR] Impossible d'écrire le cycliste. Fermez raw_data.xlsx !")