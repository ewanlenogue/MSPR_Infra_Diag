import os
import dns.resolver
from ldap3 import Server, Connection, ALL
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Initialisation de la console pour l'affichage coloré
console = Console()
# Chargement des variables depuis config.env
load_dotenv("config.env")


def check_dns(dc_ip, domain_name):
    """
    Vérifie le service DNS en forçant la requête vers l'IP du DC spécifié.
    """
    try:
        # On crée un résolveur personnalisé pour interroger spécifiquement NOTRE serveur
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [dc_ip]
        resolver.lifetime = 3  # Timeout au bout de 3 secondes si pas de réponse

        # On demande au DC de résoudre le nom du domaine
        answer = resolver.resolve(domain_name, 'A')
        return True, f"Résolu ({answer[0].to_text()})"
    except dns.exception.Timeout:
        return False, "Délai d'attente dépassé (Timeout)"
    except Exception as e:
        return False, "Échec de résolution"


def check_ad_ldap(dc_ip, user, password):
    """
    Vérifie le service Active Directory en tentant une connexion LDAP (Bind).
    """
    try:
        # On définit le serveur cible (port 389 par défaut)
        server = Server(dc_ip, get_info=ALL)

        # On tente de s'authentifier (Bind)
        # auto_bind=True lance la connexion immédiatement
        conn = Connection(server, user=user, password=password, auto_bind=True, receive_timeout=3)

        # Si la ligne ci-dessus ne lève pas d'erreur, c'est que les identifiants sont bons
        # et que l'AD répond bien
        conn.unbind()  # On referme la connexion proprement
        return True, "Authentification réussie"
    except Exception as e:
        return False, "Échec LDAP (Service arrêté ou mauvais pass)"


def run_ad_dns_diagnostic():
    # Affichage du titre du module
    console.print("\n[bold blue]Lancement du diagnostic AD & DNS...[/bold blue]\n")

    # Récupération des variables du fichier .env
    domain_name = os.getenv("DOMAIN_NAME")

    # Gestion du problème potentiel de backslash pour le nom d'utilisateur
    # On force la conversion en raw string ou on laisse tel quel si on utilise format email
    domain_user = os.getenv("DOMAIN_USER")

    domain_pass = os.getenv("DOMAIN_PASS")

    # Dictionnaire de nos contrôleurs de domaine
    domain_controllers = {
        "DC01": os.getenv("DC01_IP"),
        "DC02": os.getenv("DC02_IP")
    }

    # Création du tableau d'affichage avec rich
    table = Table(title=f"État des Contrôleurs de Domaine ({domain_name})")
    table.add_column("Serveur", style="cyan", justify="center")
    table.add_column("Adresse IP", style="magenta", justify="center")
    table.add_column("Service DNS (Port 53)", justify="center")
    table.add_column("Service AD (Port 389)", justify="center")

    # Boucle de test pour chaque machine
    with console.status("[bold green]Analyse des services en cours...[/bold green]"):
        for dc_name, dc_ip in domain_controllers.items():
            if not dc_ip:
                continue  # Passe au suivant si l'IP n'est pas renseignée

            # --- 1. Test du DNS ---
            dns_ok, dns_msg = check_dns(dc_ip, domain_name)
            if dns_ok:
                dns_display = f"[green]✔ Actif[/green]\n[dim]{dns_msg}[/dim]"
            else:
                dns_display = f"[red]✖ Hors ligne[/red]\n[dim]{dns_msg}[/dim]"

            # --- 2. Test de l'Active Directory ---
            ad_ok, ad_msg = check_ad_ldap(dc_ip, domain_user, domain_pass)
            if ad_ok:
                ad_display = f"[green]✔ Actif[/green]\n[dim]{ad_msg}[/dim]"
            else:
                ad_display = f"[red]✖ Hors ligne[/red]\n[dim]{ad_msg}[/dim]"

            # Ajout des résultats dans le tableau
            table.add_row(dc_name, dc_ip, dns_display, ad_display)
            table.add_section()  # Ajoute un trait de séparation entre les DC

    # Affichage final
    console.print(table)


if __name__ == "__main__":
    run_ad_dns_diagnostic()
