# -*- coding: utf-8 -*-
"""
Module de chargement, traitement et redimensionnement d'images.
Prend en charge nativement les formats HEIC issus de smartphones Apple.
"""
import os
import cv2
import numpy as np
from PIL import Image
import pillow_heif
from modules.utils import valider_chemin

def charger_image_heic_ou_standard(chemin_fichier):
    """
    Charge une image à partir de son chemin de fichier en prenant en charge le format HEIC.
    Si l'image est un HEIC (iPhone), elle est convertie pour être compatible avec OpenCV.

    Input :
    -------
    chemin_fichier : str
        Le chemin d'accès complet vers l'image à charger.

    Output :
    --------
    numpy.ndarray ou None :
        L'image chargée au format OpenCV (BGR) prête à être affichée.
        Renvoie None si l'image n'est pas lisible.
    """
    if not valider_chemin(chemin_fichier, "Fichier image"):
        return None

    if chemin_fichier.lower().endswith('.heic'):
        try:
            heif_file = pillow_heif.read_heif(chemin_fichier)
            image_pil = Image.frombytes(
                heif_file.mode, heif_file.size, heif_file.data, 
                "raw", heif_file.mode, heif_file.stride
            )
            return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"[ERREUR] Échec de décodage du fichier HEIC : {e}")
            return None
            
    return cv2.imread(chemin_fichier)


def preparer_photo_velo(racine_drive, candidat):
    """
    Localise le dossier vélo d'un candidat et charge l'image haute définition correspondante.

    Input :
    -------
    racine_drive : str
        Chemin d'accès racine vers le dossier de données.
    candidat : str
        Code unique du candidat (ex: "WR00").

    Output :
    --------
    numpy.ndarray ou None :
        Image OpenCV du vélo ou None si manquante.
    """
    chemin_dossier_velo = os.path.join(racine_drive, candidat, "photo", "velo")
    
    if not valider_chemin(chemin_dossier_velo, f"Dossier vélo pour {candidat}"):
        return None

    fichiers = [f for f in os.listdir(chemin_dossier_velo) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))]
    if not fichiers:
        print(f"[ERREUR] Aucune image trouvée dans le dossier vélo : {chemin_dossier_velo}")
        return None
        
    photo_velo = os.path.join(chemin_dossier_velo, fichiers[0])
    print(f"[INFO] Image trouvée : {fichiers[0]}")
    return charger_image_heic_ou_standard(photo_velo)


def lister_photos_cycliste_par_dossier(racine_drive, candidat, position_dossier):
    """
    Récupère la liste triée des chemins absolus des 3 photos d'une position donnée (ex: pos_0_deg).

    Input :
    -------
    racine_drive : str
        Chemin d'accès racine vers le dossier de données.
    candidat : str
        Code unique du candidat (ex: "WR00").
    position_dossier : str
        Nom du sous-dossier de position (ex: "pos_0_deg").

    Output :
    --------
    list :
        Liste contenant exactement les chemins d'accès absolus vers les 3 photos du test.
    """
    chemin_position = os.path.join(racine_drive, candidat, "photo", position_dossier)
    
    if not valider_chemin(chemin_position, f"Dossier {position_dossier} pour {candidat}"):
        return []

    fichiers = [
        os.path.join(chemin_position, f) for f in os.listdir(chemin_position) 
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))
    ]
    
    # Tri alphabétique pour s'assurer d'attribuer dans l'ordre de prise de vue (Test 1, Test 2, Test 3)
    fichiers.sort()
    return fichiers


def adapter_image_a_ecran(image_originale, largeur_max_affichage=1024):
    """
    Calcule le ratio de réduction et génère une image d'affichage adaptée à l'écran.

    Input :
    -------
    image_originale : numpy.ndarray
        Image haute résolution originale.
    largeur_max_affichage : int
        Largeur de confort pour l'affichage écran.

    Output :
    --------
    tuple :
        (image_affichage (numpy.ndarray), facteur_zoom (float))
    """
    hauteur_origine, largeur_origine = image_originale.shape[:2]
   
    if largeur_origine > largeur_max_affichage:
        facteur_zoom = largeur_max_affichage / largeur_origine
        nouvelle_hauteur = int(hauteur_origine * facteur_zoom)
        image_affichage = cv2.resize(image_originale, (largeur_max_affichage, nouvelle_hauteur))
    else:
        image_affichage = image_originale.copy()
        facteur_zoom = 1.0
       
    return image_affichage, facteur_zoom