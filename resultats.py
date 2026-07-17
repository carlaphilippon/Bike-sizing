# -*- coding: utf-8 -*-
import os
from modules.configuration import RACINE_DRIVE, POSITIONS_DOSSIERS
from modules.image_loader import preparer_photo_velo, adapter_image_a_ecran, lister_photos_cycliste_par_dossier, charger_image_heic_ou_standard
from modules.zoom_manager import ZoomManager
from modules.pointage import lancer_pointage_velo, lancer_pointage_cycliste
from modules.utils import convertir_pixels_en_mm
from modules.transfert_excel import recuperer_distance_roues_excel, completer_raw_data_excel_velo, completer_raw_data_excel_cycliste

def main():
    print("="*60)
    print(" 🚲 BIKE SIZING - PROTOCOLE COMPLET (VELO & CYCLISTE)")
    print("="*60)
    
    candidat = input("Entrez le numéro du candidat (ex: WR00) : ").strip().upper()
    
    chemin_excel = os.path.join(RACINE_DRIVE, "..", "raw_data.xlsx")
    chemin_backup = os.path.join(RACINE_DRIVE, "..", "raw_data_BACKUP.xlsx")

    distance_mm = recuperer_distance_roues_excel(chemin_excel, candidat)
    if not distance_mm:
        distance_mm = float(input(f"[FAILBACK] Distance non trouvée dans Excel. Entrez-la (mm) : "))

    # ==========================================================================
    # ETAPE A : POINTAGE DU VELO
    # ==========================================================================
    print("\n--- ETAPE 1 : POINTAGE DU VELO ---")
    img_velo_hd = preparer_photo_velo(RACINE_DRIVE, candidat)
    if img_velo_hd is None: return

    img_ecran_velo, facteur_zoom_v = adapter_image_a_ecran(img_velo_hd)
    zoom_mgr_velo = ZoomManager(img_velo_hd, img_ecran_velo, facteur_zoom_v)

    coords_velo_pixels, px_par_mm = lancer_pointage_velo(img_ecran_velo, zoom_mgr_velo, distance_mm)
    
    if coords_velo_pixels == "QUIT" or not coords_velo_pixels:
        print("[STOP] Étape vélo annulée ou incomplète. Arrêt.")
        return
        
    # NOUVEAU : On isole le point "Centre_Pedalier" en pixels pour s'en servir comme Origine (0,0)
    origine_pedalier_px = coords_velo_pixels.get("Centre_Pedalier")
    
    # On convertit le Vélo en mm avec la nouvelle origine
    coords_velo_mm = convertir_pixels_en_mm(coords_velo_pixels, 1.0, px_par_mm, origine_pedalier_px)
    completer_raw_data_excel_velo(chemin_excel, chemin_backup, candidat, coords_velo_mm)

    # ==========================================================================
    # ETAPE B : POINTAGE DU CYCLISTE
    # ==========================================================================
    print("\n--- ETAPE 2 : POINTAGE ANATOMIQUE DU CYCLISTE ---")
    
    for position in POSITIONS_DOSSIERS:
        print(f"\n[DOSSIER] Traitement de la position : {position}...")
        liste_photos = lister_photos_cycliste_par_dossier(RACINE_DRIVE, candidat, position)
        
        if len(liste_photos) < 3:
            print(f" [ATTENTION] Il doit y avoir 3 photos dans {position}. Suivant...")
            continue

        for index, chemin_photo in enumerate(liste_photos):
            numero_test = index + 1
            
            print(f"  -> Pointage Photo {index+1}/3 (Dédié au Test {numero_test})...")
            img_cycliste_hd = charger_image_heic_ou_standard(chemin_photo)
            if img_cycliste_hd is None: continue

            img_ecran_cyc, facteur_zoom_c = adapter_image_a_ecran(img_cycliste_hd)
            zoom_mgr_cyc = ZoomManager(img_cycliste_hd, img_ecran_cyc, facteur_zoom_c)

            coords_cycliste_pixels = lancer_pointage_cycliste(img_ecran_cyc, zoom_mgr_cyc, position, numero_test)

            if coords_cycliste_pixels == "QUIT":
                print("\n[ARRÊT] Fermeture forcée par l'utilisateur.")
                return

            elif coords_cycliste_pixels:
                # NOUVEAU : On convertit le Cycliste en mm en utilisant l'Origine Pédalier du Vélo !
                coords_cycliste_mm = convertir_pixels_en_mm(coords_cycliste_pixels, 1.0, px_par_mm, origine_pedalier_px)
                
                completer_raw_data_excel_cycliste(chemin_excel, candidat, numero_test, position, coords_cycliste_mm)

    print("\n" + "="*60)
    print(" 🎉 FIN DU PROTOCOLE. TOUTES LES DONNÉES SONT DANS L'EXCEL !")
    print("="*60)

if __name__ == "__main__":
    main()