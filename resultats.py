# -*- coding: utf-8 -*-
"""
Script principal du projet Bike Sizing.
Gère le traitement complet : Vélo puis les 3 Tests Cyclistes sous les 4 angles.
"""
import os
from modules.configuration import RACINE_DRIVE, POSITIONS_DOSSIERS
from modules.image_loader import (preparer_photo_velo, adapter_image_a_ecran, 
                                  lister_photos_cycliste_par_dossier, charger_image_heic_ou_standard)
from modules.zoom_manager import ZoomManager
from modules.pointage import lancer_pointage_velo, lancer_pointage_cycliste
from modules.utils import convertir_pixels_en_mm
from modules.transfert_excel import (recuperer_distance_roues_excel, 
                                     completer_raw_data_excel_velo, completer_raw_data_excel_cycliste)

def main():
    print("="*60)
    print(" 🚲 BIKE SIZING - PROTOCOLE COMPLET (VELO & CYCLISTE)")
    print("="*60)
    
    candidat = input("Entrez le numéro du candidat (ex: WR00) : ").strip().upper()
    
    chemin_excel = os.path.join(RACINE_DRIVE, "..", "raw_data.xlsx")
    chemin_backup = os.path.join(RACINE_DRIVE, "..", "raw_data_BACKUP.xlsx")

    # 1. Récupération de la distance de calibration
    distance_mm = recuperer_distance_roues_excel(chemin_excel, candidat)
    if not distance_mm:
        distance_mm = float(input(f"[FAILBACK] Distance non trouvée dans Excel. Entrez-la (mm) : "))

    # ==========================================================================
    # ETAPE A : POINTAGE DU VELO SEUL
    # ==========================================================================
    print("\n--- ETAPE 1 : POINTAGE DU VELO ---")
    img_velo_hd = preparer_photo_velo(RACINE_DRIVE, candidat)
    if img_velo_hd is None:
        print("[STOP] Impossible de charger la photo du vélo.")
        return

    img_ecran_velo, facteur_zoom_v = adapter_image_a_ecran(img_velo_hd)
    zoom_mgr_velo = ZoomManager(img_velo_hd, img_ecran_velo, facteur_zoom_v)

    coords_velo_pixels, px_par_mm = lancer_pointage_velo(img_ecran_velo, zoom_mgr_velo, distance_mm)
    
    if not coords_velo_pixels or not px_par_mm:
        print("[STOP] Étape vélo annulée ou incomplète. Arrêt.")
        return
        
    # Conversion et écriture Excel Vélo
    coords_velo_mm = convertir_pixels_en_mm(coords_velo_pixels, facteur_zoom=1.0, pixel_par_mm=px_par_mm)
    completer_raw_data_excel_velo(chemin_excel, chemin_backup, candidat, coords_velo_mm)

    # ==========================================================================
    # ETAPE B : POINTAGE DU CYCLISTE (4 ANGLES x 3 PHOTOS)
    # ==========================================================================
    print("\n--- ETAPE 2 : POINTAGE ANATOMIQUE DU CYCLISTE ---")
    
    # On boucle ordonnément sur les 4 dossiers de position
    for position in POSITIONS_DOSSIERS:
        print(f"\n[DOSSIER] Traitement de la position : {position}...")
        
        # Récupère les 3 fichiers images du dossier (triés par nom)
        liste_photos = lister_photos_cycliste_par_dossier(RACINE_DRIVE, candidat, position)
        
        if len(liste_photos) < 3:
            print(f" [ATTENTION] Il doit y avoir exactement 3 photos dans {position}. Trouvé: {len(liste_photos)}")
            print(" Passage à la position suivante.")
            continue

        # On boucle sur les 3 photos (chacune correspond à un numéro de Test: 1, 2 ou 3)
        for index, chemin_photo in enumerate(liste_photos):
            numero_test = index + 1  # index 0 -> Test 1, index 1 -> Test 2, index 2 -> Test 3
            
            print(f"  -> Pointage Photo {index+1}/3 (Dédié au Test {numero_test})...")
            img_cycliste_hd = charger_image_heic_ou_standard(chemin_photo)
            
            if img_cycliste_hd is None:
                print(f"   [ERREUR] Impossible de lire le fichier {chemin_photo}. Photo sautée.")
                continue

            # Préparation de l'affichage et du zoom pour cette photo spécifique
            img_ecran_cyc, facteur_zoom_c = adapter_image_a_ecran(img_cycliste_hd)
            zoom_mgr_cyc = ZoomManager(img_cycliste_hd, img_ecran_cyc, facteur_zoom_c)

            # Lancement de l'interface graphique pour le cycliste
            coords_cycliste_pixels = lancer_pointage_cycliste(img_ecran_cyc, zoom_mgr_cyc, position, numero_test)

            if coords_cycliste_pixels:
                # Injection immédiate dans la bonne section de l'Excel
                completer_raw_data_excel_cycliste(
                    chemin_excel, candidat, numero_test, position, coords_cycliste_pixels, px_par_mm
                )
            else:
                print(f"   [ATTENTION] Pointage de la photo {numero_test} annulé par l'utilisateur.")

    print("\n" + "="*60)
    print(" 🎉 FIN DU PROTOCOLE GÉNÉRAL. TOUTES LES DONNÉES SONT DANS L'EXCEL !")
    print("="*60)

if __name__ == "__main__":
    main()