# -*- coding: utf-8 -*-
import cv2
import os
from PIL import Image
import pillow_heif
import numpy as np

def charger_image_heic_ou_standard(chemin_fichier):
    """
    Charge une image en prenant en charge le format HEIC.
    Input:
    chemin_fichier : str
    Output:
    numpy.ndarray (image) ou None :
        L'image chargée au format OpenCV (BGR) prête à être affichée ou traitée.
        Renvoie None si le fichier n'existe pas ou ne peut pas être lu.
    """
    if chemin_fichier.lower().endswith('.heic'):
        heif_file = pillow_heif.read_heif(chemin_fichier)
        image_pil = Image.frombytes(
            heif_file.mode, heif_file.size, heif_file.data, 
            "raw", heif_file.mode, heif_file.stride
        )
        return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    return cv2.imread(chemin_fichier)




def preparer_photo_velo(racine_drive, candidat):
    """
    Vérifie les dossiers du Drive pour le vélo, trouve le fichier 
    et charge l'image originale.
    Retourne l'image OpenCV ou None si une erreur survient.
    Input:
    chemin_fichier : str
    Numéro de candidat : str
    Output:

    """
    # 1. Reconstruction du chemin exact
    chemin_candidat_images = os.path.join(racine_drive, candidat, "photo")
    chemin_dossier_velo = os.path.join(chemin_candidat_images, "velo")
    
    # 2. Sécurité : Vérification du dossier
    if not os.path.exists(chemin_dossier_velo):
        print(f"\n[ERREUR] Le dossier n'existe pas sur votre Drive : {chemin_dossier_velo}")
        return None

    # 3. Recherche du fichier image (.jpg, .png, .heic)
    fichiers = [f for f in os.listdir(chemin_dossier_velo) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))]
    if not fichiers:
        print(f"[ERREUR] Aucune image trouvée dans le dossier : {chemin_dossier_velo}")
        return None
        
    photo_velo = os.path.join(chemin_dossier_velo, fichiers[0])
    print(f"[INFO] Ouverture de l'image vélo : {fichiers[0]}")

    # 4. Chargement et retour de l'image
    return charger_image_heic_ou_standard(photo_velo)


def adapter_image_a_ecran(image_originale, largeur_max_affichage=1024):
    """
    Calcule le ratio et redimensionne l'image pour qu'elle s'affiche 
    entièrement sur l'écran sans déborder.
    Retourne : (image_affichage, facteur_zoom)
    """
    hauteur_origine, largeur_origine = image_originale.shape[:2]
    
    if largeur_origine > largeur_max_affichage:
        facteur_zoom = largeur_max_affichage / largeur_origine
        nouvelle_hauteur = int(hauteur_origine * facteur_zoom)
        image_affichage = cv2.resize(image_originale, (largeur_max_affichage, nouvelle_hauteur))
        print(f"[INFO] Image adaptée à l'écran : {largeur_max_affichage}x{nouvelle_hauteur} (Ratio: {facteur_zoom:.2f})")
    else:
        image_affichage = image_originale.copy()
        facteur_zoom = 1.0
        
    return image_affichage, facteur_zoom


def lancer_fenetre_pointage(nom_fenetre, image_a_afficher, fonction_clic, fonction_maj_consigne):
    """
     Gère la boucle d'affichage OpenCV pour le pointage des gommettes.
    """
    cv2.namedWindow(nom_fenetre)
    cv2.setMouseCallback(nom_fenetre, fonction_clic)
        
    fonction_maj_consigne()
        
    while True:
        cv2.imshow(nom_fenetre, image_a_afficher)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
cv2.destroyAllWindows()