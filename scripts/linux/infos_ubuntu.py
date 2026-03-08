import paramiko         # Librairie pour SSH
import json
import sys
import time

def ssh_execute(client, commande):
    stdin, stdout, stderr = client.exec_command(commande)
    return stdout.read().decode().strip()


def lire_cpu(client):
    """
    Calcule l'utilisation CPU en lisant /proc/stat deux fois à 0.1 sec d'intervalle.
    """
    def cpu_stats():
        data = ssh_execute(client, "cat /proc/stat")
        ligne_cpu = data.splitlines()[0].split()[1:]  # Ex : ['33582', '234', ...]
        valeurs = list(map(int, ligne_cpu))
        total = sum(valeurs)
        idle = valeurs[3]
        return total, idle

    total1, idle1 = cpu_stats()
    time.sleep(0.1)
    total2, idle2 = cpu_stats()

    total_diff = total2 - total1
    idle_diff = idle2 - idle1

    if total_diff == 0:
        return 0.0

    utilisation = (1 - idle_diff / total_diff) * 100
    return round(utilisation, 2)


def diagnostiquer_serveur_linux(info):
    """
    Connexion SSH + exécution des commandes système sur Linux.
    info = {
       "nom": "...",
       "ip": "...",
       "utilisateur": "...",
       "mot_de_passe": "..."
    }
    """

    nom = info["nom"]
    ip = info["ip"]
    utilisateur = info["utilisateur"]
    mot_de_passe = info["mot_de_passe"]

    print(f"\n===== Diagnostic de {nom} ({ip}) =====")

    # Création du client SSH
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connexion SSH
        client.connect(ip, username=utilisateur, password=mot_de_passe, timeout=5)
    except Exception as e:
        print(f"[ERREUR] Impossible de se connecter à {nom} ({ip}) : {e}")
        return


    # Version OS
    version_os = ssh_execute(client, "lsb_release -d | cut -f2-")
    print(f"{nom} - Version_OS : {version_os}")

    # Uptime
    uptime = ssh_execute(client, "uptime -p").replace("up ", "")
    print(f"{nom} - Uptime : {uptime}")


    # CPU utilisé (%)
    cpu_utilise = lire_cpu(client)
    print(f"{nom} - CPU_utilise : {cpu_utilise}%")

    # RAM utilisée (%)
    ligne_mem = ssh_execute(client, "free -m").splitlines()[1].split()
    ram_totale = int(ligne_mem[1])
    ram_utilisee = int(ligne_mem[2])
    ram_pourcent = round(ram_utilisee / ram_totale * 100, 2)
    print(f"{nom} - RAM_utilisee : {ram_pourcent}%")

    # Disque root utilisé (%)
    disque_root = ssh_execute(client, "df -h /").splitlines()[1].split()[4]
    disque_pourcent = float(disque_root.replace("%", ""))
    print(f"{nom} - Disque_root_utilise : {disque_pourcent}%")

    client.close()

# MAIN : lecture du fichier config_linux.json et diagnostic
def main():
    # Charger config Linux
    config_path = "config_linux.json"

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERREUR] Lecture de {config_path} impossible : {e}")
        sys.exit(1)

    serveurs_linux = data.get("serveurs_linux", [])

    if not serveurs_linux:
        print("[ERREUR] Aucun serveur Linux défini dans le JSON")
        sys.exit(1)

    for srv in serveurs_linux:
        diagnostiquer_serveur_linux(srv)

    print("\n=== Fin du diagnostic Linux ===\n")


if __name__ == "__main__":
    main()