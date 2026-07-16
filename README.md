# 🚲 Bike Sizing - Outil de Métrologie par Analyse d'Image

Ce projet est une application Python de pointage interactif sur image (OpenCV). Il permet de relever les coordonnées millimétriques de différentes pièces d'un vélo et des repères anatomiques d'un cycliste selon plusieurs angles de vue (0°, 90°, 180°, 270°), puis d'exporter ces données automatiquement vers un tableur Excel pré-formaté.

## 📁 Architecture du Projet

L'application est découpée de manière modulaire selon le principe de responsabilité unique :

*   `resultat.py` : **Chef d'orchestre.** C'est le seul script à exécuter. Il pilote l'enchaînement des opérations.
*   `modules/` :
    *   `configuration.py` : Centralise les chemins (Drive), les listes de points et le routage des colonnes Excel.
    *   `image_loader.py` : Charge les photos (prise en charge native des `.heic` d'Apple) et adapte la taille à l'écran.
    *   `pointage.py` : Gère l'interface graphique OpenCV (fenêtre, clics, instructions).
    *   `zoom_manager.py` : Moteur de zoom dynamique permettant un pointage de haute précision avec recalcul des coordonnées réelles.
    *   `transfert_excel.py` : Ouvre, sécurise (backup automatique), trouve la ligne du candidat et écrit les données dans `raw_data.xlsx`.
    *   `utils.py` : Fonctions mathématiques (calcul d'échelle) et validation du système de fichiers.

## ⚙️ Prérequis et Installation

1.  Assurez-vous d'avoir installé **Python 3.9+**.
2.  Clonez ou téléchargez ce dossier sur votre ordinateur.
3.  Ouvrez un terminal dans le dossier du projet et créez un environnement virtuel :
    ```bash
    python -m venv venv
    venv\Scripts\activate  # Sur Windows
    ```
4.  Installez les dépendances requises :
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Comment utiliser l'outil ?

**⚠️ IMPORTANT :** Assurez-vous que le fichier Excel `raw_data.xlsx` est **FERMÉ** sur votre ordinateur avant de lancer le script, sinon l'enregistrement échouera (Permission Error).

1.  Lancez le programme principal depuis votre terminal :
    ```bash
    python resultat.py
    ```
2.  Saisissez l'identifiant du candidat (ex: `WR00`).
3.  Le programme va automatiquement chercher l'échelle (distance entre les roues) dans l'Excel. S'il ne la trouve pas, il vous demandera de la saisir manuellement.
4.  **Pointage du vélo :** La photo s'ouvre. Suivez les instructions affichées dans le bandeau noir en haut à gauche.
5.  **Pointage du cycliste :** Le programme enchaîne automatiquement avec les dossiers de position (`pos_0_deg`, `pos_90_deg`, etc.).

### ⌨️ Raccourcis de l'interface (Zoom interactif)
Pour garantir une précision millimétrique, un système de zoom intelligent est intégré :
*   **Pointer un élément :** Clic gauche de la souris.
*   **Zoomer :** Placez votre souris sur la zone difficile à voir et appuyez sur **`Z`**.
*   **Dézoomer :** Appuyez sur **`D`** pour revenir à la vue globale (le dézoom est automatique après chaque clic).
*   **Quitter/Passer à l'étape suivante :** Appuyez sur **`Q`**.

## 🗂️ Structure des données attendue (Google Drive)

Le code s'attend à trouver l'arborescence suivante :
```text
H:\Mon Drive\Project\data\
│
├── raw_data.xlsx
└── images_video\
    └── [ID_CANDIDAT] (ex: WR00)\
        └── photo\
            ├── velo\ (1 photo)
            ├── pos_0_deg\ (3 photos)
            ├── pos_90_deg\ (3 photos)
            ├── pos_180_deg\ (3 photos)
            └── pos_270_deg\ (3 photos)