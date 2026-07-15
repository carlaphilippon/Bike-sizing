# -*- coding: utf-8 -*-
import cv2
import os
import math
from modules.image_loader import *
from modules.utils import *
# ==============================================================================
# CONFIGURATION DES CHEMINS 
# ==============================================================================
RACINE_DRIVE = r"H:\Mon Drive\Project\data\images_video"

# Liste des points spécifiques au vélo seul
POINTS_VELO = [
    "Pedale", "Centre_Pedalier", "Selle", "Guidon"
]

# Liste des points anatomiques pour le cycliste
POINTS_ANATOMIQUES = [
    "Pied", "Cheville", "Genou", "Hanche", "Epaule", "Coude", "Poignet"
]

# Variables globales de suivi
etape = "CALIB_ARR"
index_point = 0
pixel_par_mm = 1.0
distance_roues_mm = 0.0
facteur_zoom = 1.0  

# Dictionnaires pour stocker les résultats en pixels
calibration = {}
coords_velo_pixels = {}
image_affichage = None

def clic_souris(event, x, y, flags, param):
    global etape, index_point, pixel_par_mm, image_affichage
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # 1. Calibration Roue Arrière
        if etape == "CALIB_ARR":
            calibration["Roue_Arriere"] = (x, y)
            marquer_point(x, y, "Roue Arr", (0, 165, 255))
            etape = "CALIB_AV"
            
        # 2. Calibration Roue Avant
        elif etape == "CALIB_AV":
            calibration["Roue_Avant"] = (x, y)
            marquer_point(x, y, "Roue Av", (0, 165, 255))
            
            # Calcul immédiat de l'échelle
            p1 = calibration["Roue_Arriere"]
            p2 = calibration["Roue_Avant"]
            dist_px = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
            pixel_par_mm = dist_px / distance_roues_mm
            
            print(f"-> Échelle calculée : {pixel_par_mm:.4f} px/mm")
            etape = "POINTS_VELO"
            index_point = 0
            
        # 3. Pointage des éléments du Vélo
        elif etape == "POINTS_VELO":
            if index_point < len(POINTS_VELO):
                nom_pt = POINTS_VELO[index_point]
                coords_velo_pixels[nom_pt] = (x, y)
                marquer_point(x, y, nom_pt, (255, 0, 0)) # Bleu pour le vélo
                
                index_point += 1
                if index_point == len(POINTS_VELO):
                    etape = "TERMINE"
                    print("\n[OK] Pointage du vélo terminé. Appuyez sur 'q' pour passer à la suite.")

        maj_consigne_ecran()
        cv2.imshow("Pointage", image_affichage)

def marquer_point(x, y, texte, couleur):
    """Dessine le point et son texte sur l'image"""
    cv2.circle(image_affichage, (x, y), 6, couleur, -1)
    cv2.putText(image_affichage, texte, (x + 12, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, couleur, 2)

def maj_consigne_ecran():
    """Met à jour le bandeau d'instruction noir en haut à gauche"""
    cv2.rectangle(image_affichage, (10, 10), (450, 50), (0, 0, 0), -1)
    if etape == "CALIB_ARR":
        txt, col = "CLIQUER : CENTRE ROUE ARRIERE", (0, 165, 255)
    elif etape == "CALIB_AV":
        txt, col = "CLIQUER : CENTRE ROUE AVANT", (0, 165, 255)
    elif etape == "POINTS_VELO":
        txt, col = f"CLIQUER : {POINTS_VELO[index_point].upper()}", (255, 0, 0)
    else:
        txt, col = "FINI - Appuyez sur 'q'", (0, 255, 0)
    cv2.putText(image_affichage, txt, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 2)

def main_interface():
    global distance_roues_mm, image_affichage, etape

    # Extraction de données candidat et calibration
    candidat, distance_roues_mm = demander_infos_depart()
    
    # Chargement image vélo
    image_originale = preparer_photo_velo(RACINE_DRIVE, candidat)
    if image_originale is None:
        print("[STOP] Impossible de continuer sans l'image du vélo. Arrêt du programme.")
        return None, None, None, None

    # --- REDIMENSIONNEMENT POUR L'ÉCRAN ---
    global image_affichage, facteur_zoom
    image_affichage, facteur_zoom = adapter_image_a_ecran(image_originale, largeur_max_affichage=1024)
    
    # --- 1. LANCEMENT DE L'INTERFACE GRAPHIQUE ---
    print("\n[INFO] Fenêtre de pointage ouverte. Suivez les instructions à l'écran...")
    lancer_fenetre_pointage("Pointage", image_affichage, clic_souris, maj_consigne_ecran)
    
    # --- 2. RETOUR DES DONNÉES VERS LE MAIN ---
    if etape == "TERMINE":
        # On renvoie TOUTES les informations nécessaires au main.py
        return candidat, coords_velo_pixels, facteur_zoom, pixel_par_mm
    else:
        # Si l'utilisateur a quitté avant, on renvoie du vide
        return None, None, None, None

if __name__ == "__main__":
    main()