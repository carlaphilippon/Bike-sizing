# -*- coding: utf-8 -*-
"""
Module utilitaire contenant les fonctions d'algèbre, de géométrie 
et de validation du système de fichiers.
"""
import os
import math
from openpyxl.utils import column_index_from_string

def valider_chemin(chemin, description="Le fichier ou dossier"):
    """
    Vérifie l'existence d'un chemin système et affiche une alerte si manquant.

    Input :
    -------
    chemin : str
        Chemin d'accès à valider.
    description : str
        Nom intelligible de la cible pour l'utilisateur.

    Output :
    --------
    bool :
        True si le chemin existe, False sinon.
    """
    if not os.path.exists(chemin):
        print(f"\n[ERREUR] {description} est introuvable :")
        print(f" -> {chemin}")
        return False
    return True


def calculer_distance_pixels(p1, p2):
    """
    Calcule la distance euclidienne en pixels entre deux points (x, y).

    Input :
    -------
    p1 : tuple (int, int)
        Coordonnées (X, Y) du premier point.
    p2 : tuple (int, int)
        Coordonnées (X, Y) du second point.

    Output :
    --------
    float :
        Distance en pixels.
    """
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def convertir_pixels_en_mm(coords_pixels, facteur_zoom, pixel_par_mm, coord_origine_pixels=None):
    """
    Convertit un dictionnaire de coordonnées pixels vers l'image d'origine,
    applique l'échelle, et place l'origine (0,0) sur un point précis si fourni.

    Input :
    -------
    coords_pixels : dict {Nom: (X_ecran, Y_ecran)}
    facteur_zoom : float
    pixel_par_mm : float
    coord_origine_pixels : tuple (X, Y) du point qui servira de (0,0). Si None, repère standard.

    Output :
    --------
    dict : Coordonnées réelles converties en millimètres.
    """
    coords_mm = {}
    
    for point, (x, y) in coords_pixels.items():
        # 1. Conversion écran -> photo haute résolution
        x_orig = x / facteur_zoom
        y_orig = y / facteur_zoom
        
        if coord_origine_pixels is not None:
            # 2A. Repère Biomécanique (Origine au pédalier)
            x_ref = coord_origine_pixels[0] / facteur_zoom
            y_ref = coord_origine_pixels[1] / facteur_zoom
            
            # Axe X : vers la droite (X_point - X_origine)
            # Axe Y : vers le HAUT (Y_origine - Y_point car OpenCV descend)
            x_mm = (x_orig - x_ref) / pixel_par_mm
            y_mm = (y_ref - y_orig) / pixel_par_mm
        else:
            # 2B. Repère informatique standard (Origine haut-gauche)
            x_mm = x_orig / pixel_par_mm
            y_mm = y_orig / pixel_par_mm
            
        coords_mm[point] = (round(x_mm, 2), round(y_mm, 2))
        
    return coords_mm

def incrementer_colonne_excel(lettre_colonne, offset):
    """
    Prend une lettre de colonne Excel (ex: 'Q') et lui ajoute un offset numérique
    pour retourner la lettre de la colonne décalée correspondante.

    Input :
    -------
    lettre_colonne : str
        Lettre ou combinaison de lettres de la colonne d'origine (ex: 'Q' ou 'AA').
    offset : int
        Nombre de colonnes à décaler vers la droite.

    Output :
    --------
    str :
        Lettre de la colonne décalée (ex: 'S' pour 'Q' avec offset=2).
    """
    from openpyxl.utils import get_column_letter
    col_index = column_index_from_string(lettre_colonne)
    return get_column_letter(col_index + offset)