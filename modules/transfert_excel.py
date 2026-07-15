# -*- coding: utf-8 -*-
import os
import shutil
from openpyxl import load_workbook




def completer_raw_data_excel(racine_drive, candidat, coords_velo_mm):
    """
    Ouvre le fichier global raw_data.xlsx, cherche la ligne correspondant au candidat
    dans la colonne B, et remplit dynamiquement les cases spécifiques du vélo.
    """
    # 1. Configuration des chemins
    dossier_data = os.path.join(racine_drive, "data")
    chemin_raw_data = os.path.join(dossier_data, "raw_data.xlsx")
    chemin_backup = os.path.join(dossier_data, "raw_data_BACKUP_SECURITE.xlsx")

    if not os.path.exists(chemin_raw_data):
        print(f"[ERREUR] Impossible de trouver le fichier : {chemin_raw_data}")
        return

    # 2. SÉCURITÉ : Copie de sauvegarde automatique
    try:
        shutil.copy2(chemin_raw_data, chemin_backup)
        print("[SÉCURITÉ] Copie de sauvegarde créée avec succès.")
    except Exception as e:
        print(f"[ATTENTION] Impossible de créer la sauvegarde : {e}. Annulation par sécurité.")
        return

    # 3. Chargement du classeur Excel
    try:
        wb = load_workbook(chemin_raw_data)
        ws = wb.active  # Ou wb["Nom_De_La_Feuille"] si besoin

        # 4. RECHERCHE DYNAMIQUE DE LA LIGNE DU CANDIDAT (Colonne B)
        ligne_candidat = None
        # On parcourt la colonne B de la ligne 2 jusqu'à la dernière ligne remplie
        for row in range(2, ws.max_row + 1):
            valeur_cellule = ws.cell(row=row, column=2).value  # Column 2 = Colonne B
            
            # On nettoie le texte (espaces, majuscules) pour éviter les erreurs de frappe
            if valeur_cellule and str(valeur_cellule).strip().upper() == str(candidat).strip().upper():
                ligne_candidat = row
                break  # On a trouvé la ligne, on arrête la recherche

        if ligne_candidat is None:
            print(f"\n[ERREUR Excel] Impossible de trouver le candidat '{candidat}' dans la colonne B.")
            print("Vérifiez que le code du candidat est bien pré-écrit dans le tableau Excel.")
            return
            
        print(f"[EXCEL] Candidat '{candidat}' détecté avec succès à la ligne {ligne_candidat}.")

        # 5. CARTOGRAPHIE DES COLONNES (Plus de numéros de lignes ici !)
        # On définit uniquement les LETTRES des colonnes pour chaque variable
        cartographie_colonnes = {
            "Selle":           {"X": "KI", "Y": "KJ"},
            "Guidon":          {"X": "KK", "Y": "KL"},  
            "Roue arrière":    {"X": "KM", "Y": "KN"},  
            "Roue avant":      {"X": "KO", "Y": "KP"}, 
            "Pedale":          {"X": "KQ", "Y": "KR"}, # Lettres changées pour éviter les doublons
            "Centre pedalier": {"X": "KS", "Y": "KT"}  # Lettres changées pour éviter les doublons
        }

        # 6. ÉCRITURE DES DONNÉES SUR LA BONNE LIGNE
        print("[EXCEL] Remplissage des coordonnées...")
        for composant, coordonnees in coords_velo_mm.items():
            if composant in cartographie_colonnes:
                
                # 1. On récupère proprement les lettres des colonnes
                lettre_x = cartographie_colonnes[composant]["X"]
                lettre_y = cartographie_colonnes[composant]["Y"]
                
                # 2. On cible les cellules en associant la lettre et le numéro de ligne (ex: "KI" + 5 -> "KI5")
                cell_x = ws[f"{lettre_x}{ligne_candidat}"]
                cell_y = ws[f"{lettre_y}{ligne_candidat}"]
                
                # 3. Injection des valeurs numériques
                cell_x.value = coordonnees[0]  # X
                cell_y.value = coordonnees[1]  # Y
                
                # 4. Application du format à deux décimales
                cell_x.number_format = '0.00'
                cell_y.number_format = '0.00'
                
                print(f"-> {composant} inséré en {lettre_x}{ligne_candidat} (X) et {lettre_y}{ligne_candidat} (Y)")
        # 7. Sauvegarde finale
        wb.save(chemin_raw_data)
        print(f"\n[OK] Le fichier 'raw_data.xlsx' a été mis à jour pour le candidat {candidat}.")

    except PermissionError:
        print("\n[ERREUR SCRIPT] Impossible d'écrire dans le fichier !")
        print("Vérifiez que le fichier 'raw_data.xlsx' est bien FERMÉ sur votre ordinateur.")
    except Exception as e:
        print(f"\n[ERREUR INCONNUE] Le transfert a échoué : {e}")