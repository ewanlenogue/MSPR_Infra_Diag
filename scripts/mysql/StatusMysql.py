import mysql.connector
from mysql.connector import Error

# Infos de connexion au serveur & Base de données

liste_servers=["172.16.133.5", "172.16.133.7"]
port=3306
user_bdd="check_if_well"
pwd_bdd="t#in9isg@@d"
bdd="WMS_BASE"


for ip in liste_servers:
    print("\n=======================================================")
    print(f"Connexion au serveur de base de données: {ip}")
    print("=======================================================")

    #conn = None
    #cursor = None

    # Etablir la connexion aux serveurs
    try:
        conn = mysql.connector.connect(
            host=ip,
            port=port,
            user=user_bdd,
            passwd=pwd_bdd,
            database=bdd,
            connect_timeout=3
        )
        if conn.is_connected():
            print("Connexion à MySQL réussie !\n")

            # Création d'un curseur pour l'exécution des requêtes
            cursor = conn.cursor()
            # Requête SQL à exécuter
            sql_cmd = "SELECT 1;"
            # Exécution de la requête
            cursor.execute(sql_cmd)
            # Récupération des résultats
            results = cursor.fetchone()
            print(f"Réponse de la base de données", results)
            # Affichage des données
            for row in results:
                print(row)

    except Error as e:
        print(f"Erreur : {e}")

    # Fermeture du curseur et de la connexion
    finally:
        print("Connexion à MySQL fermée.")