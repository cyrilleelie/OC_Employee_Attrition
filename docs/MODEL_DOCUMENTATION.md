# Documentation Technique du Modèle de Prédiction d'Attrition RH

## 1. Objectif du Modèle

Ce modèle de Machine Learning a pour objectif de prédire la probabilité qu'un employé quitte volontairement l'entreprise (attrition). Il vise à identifier les employés à risque afin de permettre des actions proactives de rétention.

## 2. Source et Préparation des Données

### 2.1. Source des Données
Les données utilisées pour l'entraînement et l'évaluation du modèle proviennent de la table `employees` de la base de données PostgreSQL du projet.
Initialement, ces données ont été consolidées à partir de trois fichiers CSV : `extrait_sirh.csv`, `extrait_eval.csv`, et `extrait_sondage.csv`.

### 2.2. Préparation des Données Avant Entraînement
Avant d'être stockées dans la base de données et utilisées par la pipeline d'entraînement Scikit-learn, les données brutes subissent les transformations suivantes (principalement via les scripts `src/data_processing/load_data.py` et `src/data_processing/preprocess.py` lors du peuplement de la base) :

* Fusion des différentes sources de données.
* Création de la clé `id_employee` (si nécessaire, à partir de `eval_number`).
* Nettoyage des données :
    * Conversion de la variable cible `a_quitte_l_entreprise` en format numérique (`0` pour Non, `1` pour Oui).
    * Conversion de la colonne `augmentation_salaire_precedente` (ex: "XX %") en valeur numérique (float).
    * Suppression des colonnes identifiées comme non pertinentes ou redondantes avant le feature engineering (ex: `eval_number` après utilisation).
    * Gestion des doublons.
* Mappage des variables binaires textuelles en format numérique (ex: `genre`, `heure_supplementaires`).
* (Optionnel) Création de features dérivées (ex: `satisfaction_moyenne` si vous l'avez implémentée et stockée).

## 3. Features Utilisées par le Modèle

Le modèle final est entraîné sur les features suivantes (après les étapes de préparation ci-dessus et avant le préprocessing Scikit-learn comme le scaling ou le one-hot encoding) :

* **Variables Numériques (destinées au Scaling) :**
    * `age`
    * `revenu_mensuel`
    * `nombre_experiences_precedentes`
    * `annees_dans_l_entreprise`
    * `satisfaction_employee_environnement`
    * `note_evaluation_precedente`
    * `satisfaction_employee_nature_travail`
    * `satisfaction_employee_equipe`
    * `satisfaction_employee_equilibre_pro_perso`
    * `note_evaluation_actuelle`
    * `augementation_salaire_precedente` (numérique)
    * `nombre_participation_pee`
    * `nb_formations_suivies`
    * `distance_domicile_travail`
    * `annees_depuis_la_derniere_promotion`
* **Variables Catégorielles Binaires (mappées en 0/1 avant préprocesseur) :**
    * `genre`
    * `heure_supplementaires`
* **Variables Catégorielles Ordinales (destinées à `OrdinalEncoder`) :**
    * `frequence_deplacement`
* **Variables Catégorielles Nominales (destinées à `OneHotEncoder` avec `drop='first'`) :**
    * `statut_marital`
    * `departement`
    * `poste`
    * `niveau_education`
    * `domaine_etude`

*(Note : La variable `id_employee` et les dates de métadonnées comme `date_creation_enregistrement` ne sont PAS utilisées comme features pour l'entraînement.)*

## 4. Algorithme et Configuration du Modèle

* **Algorithme Utilisé :** Régression Logistique (via `sklearn.linear_model.LogisticRegression`).
* **Motivation (brève) :** Choisi pour sa simplicité, son interprétabilité et ses bonnes performances sur les problèmes de classification binaire, surtout après un bon preprocessing des features. C'est un bon point de départ.
* **Hyperparamètres Clés :**
    * `random_state=42` (pour la reproductibilité).
    * `class_weight='balanced'` (pour aider à gérer le déséquilibre des classes dans la variable cible).
    * `max_iter=1000` (pour assurer la convergence).
    * *(Autres hyperparamètres importants si vous les avez modifiés)*.

## 5. Métriques de Performance (sur le Jeu de Test)

Les performances du modèle sont évaluées sur un jeu de test mis de côté (20% des données). Voici les résultats obtenus lors du dernier entraînement :

*(ICI, copiez-collez la sortie de la Matrice de Confusion et du Rapport de Classification de votre script `train_model.py`)*

* **Matrice de Confusion :**
    ```
    # Exemple
    [[194  53]
    [ 13  34]]
    ```
* **Rapport de Classification :**
    ```
    # Exemple
               precision    recall  f1-score   support

         Non       0.94      0.79      0.85       247
         Oui       0.39      0.72      0.51        47

    accuracy                           0.78       294
   macro avg       0.66      0.75      0.68       294
weighted avg       0.85      0.78      0.80       294
    ```
* **F2-Score (privilégie le Rappel pour la classe positive 'Oui') :**
    * `0.XX`

## 7. Procédure de Ré-entraînement

Pour ré-entraîner le modèle (par exemple, si de nouvelles données sont disponibles dans la table `employees`) :

1.  Assurez-vous que l'environnement Poetry est actif (`poetry shell`).
2.  Exécutez le script d'entraînement :
    ```bash
    python -m src.modeling.train_model
    ```
3.  Le nouveau modèle (`.joblib`) sera sauvegardé dans le dossier `models/`, écrasant l'ancien.
4.  Si l'API est déployée, il faudra redéployer l'application avec le nouveau fichier modèle.

## 8. Considérations de Maintenance et Monitoring

* **Monitoring des Données d'Entrée :** Surveiller la distribution des données reçues par l'API pour détecter une éventuelle dérive par rapport aux données d'entraînement.
* **Monitoring des Performances :** Si possible, suivre la performance réelle du modèle sur les nouvelles prédictions (nécessiterait un feedback sur les départs réels).
* **Ré-entraînement Périodique :** Envisager un ré-entraînement régulier (ex: trimestriel, semestriel) avec des données fraîches pour maintenir la pertinence du modèle.

---