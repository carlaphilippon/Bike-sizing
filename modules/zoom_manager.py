# -*- coding: utf-8 -*-
"""
Module de gestion du zoom dynamique et interactif sous OpenCV.
Assure le tracking et la correction des coordonnées physiques.
"""
import cv2

class ZoomManager:
    """
    Gestionnaire d'état de zoom pour une fenêtre OpenCV.
    Permet de zoomer sur le curseur souris et d'ajuster les coordonnées de clic.
    """
    def __init__(self, image_originale, image_affichage_de_base, facteur_zoom_de_base):
        self.img_orig = image_originale
        self.img_base = image_affichage_de_base
        self.zoom_base = facteur_zoom_de_base
        
        # État du zoom courant
        self.actif = False
        self.x_offset = 0
        self.y_offset = 0
        self.facteur_courant = facteur_zoom_de_base

    def activer_zoom(self, x_souris_ecran, y_souris_ecran, taille_boite_pixel_orig=300):
        """
        Découpe une zone haute résolution centrée sur la souris et l'étire sur l'écran.

        Input :
        -------
        x_souris_ecran, y_souris_ecran : int
            Position courante du pointeur sur l'image d'affichage standard.
        taille_boite_pixel_orig : int
            Largeur en pixel de la boîte capturée sur l'image d'origine (plus c'est petit, plus on zoom).

        Output :
        --------
        numpy.ndarray :
            L'image recadrée et agrandie prête pour l'affichage de précision.
        """
        h_orig, w_orig = self.img_orig.shape[:2]
        
        # 1. Calcul du centre de la souris projeté sur la photo HD d'origine
        x_centre_HD = int(x_souris_ecran / self.zoom_base)
        y_centre_HD = int(y_souris_ecran / self.zoom_base)
        
        # 2. Calcul du rectangle de découpe
        self.x_offset = max(0, x_centre_HD - taille_boite_pixel_orig // 2)
        self.y_offset = max(0, y_centre_HD - taille_boite_pixel_orig // 2)
        
        x_max = min(w_orig, self.x_offset + taille_boite_pixel_orig)
        y_max = min(h_orig, self.y_offset + taille_boite_pixel_orig)
        
        # Ajustement d'offset aux limites d'image
        self.x_offset = max(0, x_max - taille_boite_pixel_orig)
        self.y_offset = max(0, y_max - taille_boite_pixel_orig)
        
        # 3. Extraction de la zone
        zone_decoupee = self.img_orig[self.y_offset:y_max, self.x_offset:x_max]
        
        # 4. Redimensionnement
        h_fenetre, w_fenetre = self.img_base.shape[:2]
        image_zoomee = cv2.resize(zone_decoupee, (w_fenetre, h_fenetre))
        
        # 5. Mise à jour de l'échelle locale de zoom
        self.facteur_courant = w_fenetre / taille_boite_pixel_orig
        self.actif = True
        
        return image_zoomee

    def desactiver_zoom(self):
        """Réinitialise les paramètres pour revenir à la vue globale."""
        self.actif = False
        self.x_offset = 0
        self.y_offset = 0
        self.facteur_courant = self.zoom_base

    def corriger_coordonnees(self, x_clic, y_clic):
        """
        Convertit les coordonnées d'un clic écran vers l'image originale HD
        en prenant en compte l'état actuel de zoom ou de dézoom.

        Input :
        -------
        x_clic, y_clic : int
            Position de l'événement de clic de souris OpenCV.

        Output :
        --------
        tuple :
            Coordonnées (x_reel, y_reel) ajustées sur l'image d'origine.
        """
        if self.actif:
            x_reel = int(x_clic / self.facteur_courant) + self.x_offset
            y_reel = int(y_clic / self.facteur_courant) + self.y_offset
        else:
            x_reel = int(x_clic / self.zoom_base)
            y_reel = int(y_clic / self.zoom_base)
            
        return x_reel, y_reel