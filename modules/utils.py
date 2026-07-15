# -*- coding: utf-8 -*-
import cv2
import os
import math
from modules.image_loader import *
from openpyxl import load_workbook


def demander_infos_depart():
    """
    Demande proprement le numéro du candidat et la distance entre les roues.
    Input: 
    Output: (candidat (str), distance_roues_mm (float))
    """
    candidat = input("Entrez le numéro du candidat (ex: WR00, S01) : ").strip().upper()
    
    while True:
        try:
            distance_roues_mm = float(input("Entrez la distance entre les deux roues (mm) : "))
            if distance_roues_mm > 0:
                break
            print("[ERREUR] La distance doit être supérieure à 0.")
        except ValueError:
            print("[ERREUR] Veuillez entrer un nombre valide.")
            
    return candidat, distance_roues_mm



def calculer_et_afficher_coords_mm(coords_pixels, facteur_zoom, pixel_par_mm):
    """
    Convertit les coordonnées de pixels écrans en coordonnées réelles (mm)
    en annulant l'effet du zoom, puis affiche le compte-rendu.
    Retourne le dictionnaire des coordonnées en mm.
    """
    print("\n--- COORDONNÉES VÉLO ENREGISTRÉES (en mm) ---")
    coords_mm = {}
    
    for pt, (px_x, px_y) in coords_pixels.items():
        # 1. On retrouve le vrai pixel sur la photo originale non-zoomée
        vrai_px_x = px_x / facteur_zoom
        vrai_px_y = px_y / facteur_zoom
        
        # 2. On convertit en mm grâce à l'échelle
        vrai_x_mm = round(vrai_px_x / pixel_par_mm, 2)
        vrai_y_mm = round(vrai_px_y / pixel_par_mm, 2)
        
        coords_mm[pt] = (vrai_x_mm, vrai_y_mm)
        print(f"{pt} : X={vrai_x_mm} mm, Y={vrai_y_mm} mm")
        
    print("\nPrêt pour passer à l'étape suivante (les positions du cycliste).")
    return coords_mm


