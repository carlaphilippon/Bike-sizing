# -*- coding: utf-8 -*-
"""
Module gérant l'interface graphique OpenCV pour le pointage des gommettes.
Intègre le système de zoom sur clic et le bouton d'arrêt (Echap).
"""
import cv2
from modules.configuration import POINTS_VELO, POINTS_ANATOMIQUES
from modules.utils import calculer_distance_pixels

def lancer_pointage_velo(image_base, zoom_manager, distance_roues_mm):
    etat = {"etape": "CALIB_ARR", "index": 0}
    calibration = {}
    coords_pixels = {}
    
    # Nouvelle variable : True si l'utilisateur a appuyé sur Z et va cliquer pour zoomer
    attente_clic_zoom = False 

    def maj_consigne(img_temp):
        cv2.rectangle(img_temp, (10, 10), (450, 70), (0, 0, 0), -1)
        
        # Affichage dynamique selon le mode (Zoom ou Pointage)
        if attente_clic_zoom:
            txt, col = "MODE ZOOM : CLIQUEZ POUR VISER", (0, 0, 255) # Rouge
            cv2.putText(img_temp, txt, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 2)
        else:
            if etat["etape"] == "CALIB_ARR":
                txt, col = "CLIQUER : CENTRE ROUE ARRIERE", (0, 165, 255)
            elif etat["etape"] == "CALIB_AV":
                txt, col = "CLIQUER : CENTRE ROUE AVANT", (0, 165, 255)
            elif etat["etape"] == "POINTS_VELO":
                txt, col = f"CLIQUER : {POINTS_VELO[etat['index']].upper()}", (255, 0, 0)
            else:
                txt, col = "FINI - Appuyez sur 'q'", (0, 255, 0)
            cv2.putText(img_temp, txt, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 2)
            
        cv2.putText(img_temp, "[Z] Zoomer | [D] Dezoomer | [Echap] Quitter", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    def gestion_souris(event, x, y, flags, param):
        nonlocal attente_clic_zoom
        
        if event == cv2.EVENT_LBUTTONDOWN:
            if attente_clic_zoom:
                # 1. ACTION DE ZOOM : Le clic sert uniquement à zoomer
                zoom_manager.image_zoomee_actuelle = zoom_manager.activer_zoom(x, y)
                attente_clic_zoom = False  # On repasse en mode pointage normal
            else:
                # 2. ACTION DE POINTAGE : Le clic sert à valider le point
                x_reel, y_reel = zoom_manager.corriger_coordonnees(x, y)
                
                if etat["etape"] == "CALIB_ARR":
                    calibration["Roue_Arriere"] = (x_reel, y_reel)
                    etat["etape"] = "CALIB_AV"
                elif etat["etape"] == "CALIB_AV":
                    calibration["Roue_Avant"] = (x_reel, y_reel)
                    etat["etape"] = "POINTS_VELO"
                elif etat["etape"] == "POINTS_VELO":
                    if etat["index"] < len(POINTS_VELO):
                        nom_pt = POINTS_VELO[etat["index"]]
                        coords_pixels[nom_pt] = (x_reel, y_reel)
                        etat["index"] += 1
                        if etat["index"] >= len(POINTS_VELO):
                            etat["etape"] = "TERMINE"
                            print("\n[OK] Pointage du vélo terminé. Appuyez sur 'q'.")
                
                # Auto-dézoom une fois le pointage effectué
                if zoom_manager.actif:
                    zoom_manager.desactiver_zoom()

    cv2.namedWindow("Pointage Velo")
    cv2.setMouseCallback("Pointage Velo", gestion_souris)

    while True:
        if zoom_manager.actif:
            img_a_afficher = zoom_manager.image_zoomee_actuelle.copy()
        else:
            img_a_afficher = image_base.copy()
        
        maj_consigne(img_a_afficher)
        cv2.imshow("Pointage Velo", img_a_afficher)
        
        touche = cv2.waitKey(1) & 0xFF
        if touche == ord('q'):
            break
        elif touche == 27:  # 27 = Touche ECHAP
            cv2.destroyAllWindows()
            return "QUIT", None
        elif touche == ord('z'):
            if zoom_manager.actif:
                zoom_manager.desactiver_zoom() # On dézoome si on était zoomé
            attente_clic_zoom = not attente_clic_zoom # Active/Désactive l'attente du clic
        elif touche == ord('d'):
            zoom_manager.desactiver_zoom()
            attente_clic_zoom = False
            
    cv2.destroyAllWindows()
    
    if "Roue_Arriere" in calibration and "Roue_Avant" in calibration:
        dist_px = calculer_distance_pixels(calibration["Roue_Arriere"], calibration["Roue_Avant"])
        pixel_par_mm = dist_px / distance_roues_mm
        
        # ---> CORRECTION : On réinjecte les roues avec l'orthographe EXACTE du fichier configuration.py
        coords_pixels["Roue arrière"] = calibration["Roue_Arriere"]
        coords_pixels["Roue avant"] = calibration["Roue_Avant"]
        # ------------------------------------------------------------------------------------------

        return coords_pixels, pixel_par_mm
        
    return None, None
    
    if "Roue_Arriere" in calibration and "Roue_Avant" in calibration:
        dist_px = calculer_distance_pixels(calibration["Roue_Arriere"], calibration["Roue_Avant"])
        pixel_par_mm = dist_px / distance_roues_mm
        return coords_pixels, pixel_par_mm
        
    return None, None


def lancer_pointage_cycliste(image_base, zoom_manager, position_dossier, numero_test):
    etat = {"index": 0}
    coords_pixels = {}
    attente_clic_zoom = False

    def maj_consigne(img_temp):
        cv2.rectangle(img_temp, (10, 10), (550, 70), (0, 0, 0), -1)
        
        if attente_clic_zoom:
            txt, col = "MODE ZOOM : CLIQUEZ POUR VISER", (0, 0, 255)
            cv2.putText(img_temp, txt, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 2)
        else:
            if etat["index"] < len(POINTS_ANATOMIQUES):
                point_actuel = POINTS_ANATOMIQUES[etat["index"]]
                txt = f"[{position_dossier.upper()} - TEST {numero_test}] CLIQUER : {point_actuel.upper()}"
                col = (255, 255, 0)
            else:
                txt, col = "FIN PHOTO - Appuyez sur 'q' pour valider", (0, 255, 0)
            cv2.putText(img_temp, txt, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 2)
            
        cv2.putText(img_temp, "Pour la photo du velo un clic droit avant de commencer \\[Z] Zoomer | [D] Dezoomer ", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    def gestion_souris(event, x, y, flags, param):
        nonlocal attente_clic_zoom
        
        if event == cv2.EVENT_LBUTTONDOWN:
            if attente_clic_zoom:
                # 1. Action de Zoom
                zoom_manager.image_zoomee_actuelle = zoom_manager.activer_zoom(x, y)
                attente_clic_zoom = False
            else:
                # 2. Action de Pointage
                x_reel, y_reel = zoom_manager.corriger_coordonnees(x, y)
                if etat["index"] < len(POINTS_ANATOMIQUES):
                    nom_pt = POINTS_ANATOMIQUES[etat["index"]]
                    coords_pixels[nom_pt] = (x_reel, y_reel)
                    etat["index"] += 1
                    if etat["index"] == len(POINTS_ANATOMIQUES):
                        print(f" -> Pointage de la photo terminé. Pressez 'q' pour valider.")
                
                if zoom_manager.actif:
                    zoom_manager.desactiver_zoom()

    fenetre_nom = f"Pointage Cycliste - Test {numero_test}"
    cv2.namedWindow(fenetre_nom)
    cv2.setMouseCallback(fenetre_nom, gestion_souris)

    while True:
        if zoom_manager.actif:
            img_a_afficher = zoom_manager.image_zoomee_actuelle.copy()
        else:
            img_a_afficher = image_base.copy()
            
        maj_consigne(img_a_afficher)
        cv2.imshow(fenetre_nom, img_a_afficher)
        
        touche = cv2.waitKey(1) & 0xFF
        if touche == ord('q'):
            break
        elif touche == 27:  # ECHAP
            cv2.destroyWindow(fenetre_nom)
            return "QUIT"
        elif touche == ord('z'):
            if zoom_manager.actif:
                zoom_manager.desactiver_zoom()
            attente_clic_zoom = not attente_clic_zoom
        elif touche == ord('d'):
            zoom_manager.desactiver_zoom()
            attente_clic_zoom = False
            
    cv2.destroyWindow(fenetre_nom)
    return coords_pixels if etat["index"] == len(POINTS_ANATOMIQUES) else None