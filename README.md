# Hiring Challenge DataEngineer

## 🚀 Description

Ce projet met en place un **pipeline ETL (Extract, Transform, Load) automatisé** avec Apache Airflow, permettant l’extraction, la transformation et le chargement des **données provenant de deux capteurs de surveillance de qualité de l'air** dans **MongoDB**.
Les données collectées sont ensuite accessibles via **Apache Drill**, offrant une interface **SQL** pour interroger **MongoDB**, et sont visualisées dans **Apache Superset** pour une analyse et un suivi en temps réel de la qualité de l'air.

## 🏗️ Technologies utilisées

- **Apache Airflow** : Orchestration du pipeline ETL
- **MongoDB** : Stockage des données
- **Apache Drill** : Accès SQL aux données MongoDB
- **Apache Superset** : Visualisation et exploration des données

## ⚡ Fonctionnalités

✔️ Extraction et transformation des données  
✔️ Chargement automatique dans MongoDB  
✔️ Connexion et interrogation SQL via Apache Drill  
✔️ Tableaux de bord interactifs avec Superset

## 🛠️ Installation & Exécution

**NB :** _Avant de poursuivre, il est important de noter que toutes les opérations ont été réalisées sur un système Linux. Si vous utilisez un autre système d'exploitation, vous devrez adapter les commandes en conséquence. Assurez-vous d'avoir déjà installé **MongoDB**, **Python** et **Java**._

1. **Clone le projet et accède** :
   ```sh
   git clone https://github.com/Lambda225/HiringChallengeDataEngineer.git
   cd HiringChallengeDataEngineer
   ```
2. **Crée un environnement virtul et activation**

   ```sh
    python3 -m venv .venv
    source .venv/bin/activate
   ```

3. **Installe les dépandance python**
   ```sh
   pip install -r requirements.txt
   ```
4. **Définit les variables d'environnement**

   créer une fichier nommé `.env` a la racine du repectoire et ajouter les variables suvantes en modifiant les valeurs:

   ```.env
   STATION_ID = keyStation1,keyStation1
   DB_URL = yourDataBaseUrl
   ```

5. **lance apache Airflow et excecute le dag**

   ```sh
   export AIRFLOW_HOME=projectPath
   airflow db init
   airflow users create --username admin --firstname firstname --lastname lastname --role Admin --email admin@domain.com
   ```

   après ses étapes vous serez amené a entrer un mots de passe.Juste après cela veiller exécuter ses commande

   ```sh
   airflow standalone
   ```

   accédez a l'addresse http://localhost:8080 pour vous connecté a airflow et activé le dag _ETL_airquality_

   **NB** : _Avant cela assurer vous aurez vous que mongoDB est lancé_

   ![activation du dag](./image/active_dag.png)

6. **Connect mongoDB a apache Drill**

   ```sh
   ./apache-drill-1.21.2/bin/drill-embedded
   ```

   accédez a l'addresse http://localhost:8047 puis allez dans storage. Ensuite clické sur enable en face de mongo. Allez dans query entrer les codes suivant pour vous assurer que la connection a été éffectuer

   ![activation du connecteur](./image/active_drill_connector.png)

   ```sql
   SELECT * FROM mongo.airquality.sensor
   ```

   **NB :** Vous pouvez toujours modier url de connection si celui par défault ne correspond pas

7. **Visualise avec Apache Superset**

   ```sh
   export FLASK_APP=superset
   export SUPERSET_CONFIG_PATH=yourProjectPath/superset_config.py
   superset db upgrade
   superset fab create-admin
   ```

   après ses étapes vous serais amenez a créer votre utilisateur superset

   ```sh
   superset init
   ```

   rajouter le chemain vers le fichier `activate` de votre environement virtule à la troisème ligne du fichier `run_superset.sh`

   ```sh
   ./run_superset
   ```

   rendez-vous à l'addresse http://localhost:8088
   pour accéder à apache superset

## ⏳ Comment Apache Airflow récupère les données chaque heure ?

Dans ce projet, nous avons eu à notre disposition une **API** fournissant des données issues de **deux stations de surveillance** qui mesurent, chaque heure, des informations sur la **qualité de l'air** sur une période d’un an.

L’ETL que nous avons conçu suit les étapes suivantes :

---

### 1️. **Extraction (Extract)**

- Récupération des données brutes provenant des **deux capteurs de qualité de l’air** via une API REST.
- Extraction des mesures de **température, PM2.5, CO, et autres polluants atmosphériques**.

---

### 2. **Vérification de l'existence de la base de données**

Avant de procéder à la transformation des données, nous nous connectons à **MongoDB** et vérifions si la base de données `airquality` existe déjà.

---

### 3️. **Transformation (Transform)**

🔹 **Pré-traitement des données** :

- Conversion de la variable **`timestamp`** en format date.
- Renommage de certaines variables pour assurer la cohérence des données.

🔹 **Deux cas de figure se présentent :**

1️. **Si la base de données `airquality` n'existe pas** :

- Calcul de la **moyenne journalière** des variables **CO et PM2.5**, sans prendre en compte la journée en cours si elle n'est pas terminée.

2️. **Si la base de données `airquality` existe** :

- Récupération de la **dernière valeur enregistrée** par chaque capteur.
- Mise à jour de la **moyenne journalière** des variables CO et PM2.5 si nous sommes en fin de journée.

---

### 4️. **Chargement (Load)**

- Stockage des données transformées dans **MongoDB**.
- Indexation pour une interrogation rapide via **Apache Drill**.
- Intégration des données dans **Apache Superset** pour la visualisation et l'analyse.

## 🚀 Mise en Production du Pipeline ETL avec Apache Airflow

Pour mettre en production ce projet, je vous recommande de créer une **machine virtuelle Linux** proposée par un **fournisseur cloud** (ex: AWS, Azure, GCP).

Vous devrez également disposer d'un **compte MongoDB**, soit via une **instance autogérée** (MongoDB installé sur votre VM) ou un **service managé** comme **MongoDB Atlas**.

Une fois la machine virtuelle créée, **accédez à la console** via **SSH** et suivez les étapes définies dans la section suivante :

🔗 [🛠️ Installation & Exécution](#-installation--exécution)

📌 **Prérequis recommandés** :

- Une machine virtuelle avec **Ubuntu 20.04+** ou **Debian**.
- Un accès **root** ou un utilisateur avec les permissions `sudo`.
- Une connexion Internet stable pour installer les dépendances.
- Un compte **MongoDB Atlas** ou une base **MongoDB locale**.

Une fois connecté à la machine virtuelle, vous pourrez procéder aux installations et configurations nécessaires pour exécuter le pipeline ETL avec **Apache Airflow**.

## 🎯 **Conclusion**

Ce projet a été une **expérience enrichissante**, permettant d’acquérir et de renforcer plusieurs compétences clés dans le domaine du **Big Data, de l'orchestration des workflows et de la visualisation des données**.

Grâce à la mise en place d’un **pipeline ETL automatisé** avec **Apache Airflow**, nous avons appris à orchestrer efficacement l’extraction, la transformation et le chargement des données issues de **capteurs de surveillance de la qualité de l'air**.

L’intégration avec **MongoDB** nous a permis de mieux comprendre le stockage et la gestion des bases de données **NoSQL**, tandis que **Apache Drill** nous a familiarisés avec l'interrogation des bases de données **semi-structurées** via SQL. Enfin, la visualisation des données avec **Apache Superset** a renforcé nos compétences en **analyse de données et en business intelligence**.
