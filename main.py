# -*- coding: utf-8 -*-
import cv2
import os
import math
from modules.utils import *
from modules.image_loader import *
from modules.interface import *
from modules.transfert_excel import completer_raw_data_excel


def main():
    # 1. On lance l'interface et on récupère le pack complet de données
    candidat, coords_pixels, zoom, px_mm = main_interface()
    
    # 2. Si le candidat n'est pas None, c'est que l'étape s'est bien terminée sur "TERMINE" !
    if candidat is not None:
        # On calcule les vraies coordonnées
        coords_velo_mm = calculer_et_afficher_coords_mm(coords_pixels, zoom, px_mm)
        
        # On enregistre dans le fichier Excel global raw_data.xlsx
        completer_raw_data_excel(r"H:\Mon Drive\Project", candidat, coords_velo_mm)
        
    else:
        print("\n[ATTENTION] Le protocole a été fermé avant la fin. Aucune donnée enregistrée dans Excel.")
if __name__ == "__main__":
    main()