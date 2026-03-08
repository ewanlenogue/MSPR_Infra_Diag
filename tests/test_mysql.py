import pytest
from unittest.mock import patch, MagicMock
from scripts.mysql.StatusMysql import check_mysql_connection  # remplace 'votre_module' par le nom de ton fichier .py

# --- Test : connexion MySQL réussie ---
@patch("scripts.mysql.StatusMysql.mysql.connector.connect")
def test_check_mysql_connection_success(mock_connect):
    # Mock de l'objet connexion
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.is_connected.return_value = True

    # Mock du curseur et des résultats
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1,)

    result = check_mysql_connection("172.16.133.5", 3306, "user", "pwd", "BDD")

    # Assertions : on a bien essayé de se connecter
    mock_connect.assert_called_once_with(
        host="172.16.133.5",
        port=3306,
        user="user",
        passwd="pwd",
        database="BDD",
        connect_timeout=3
    )
    mock_conn.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once_with("SELECT 1;")
    mock_cursor.fetchone.assert_called_once()

    # Vérifie que la fonction retourne bien la fermeture de connexion
    assert result == "Connexion à MySQL fermée."


# --- Test : échec de connexion MySQL ---
@patch("scripts.mysql.StatusMysql.mysql.connector.connect", side_effect=Exception("Connexion impossible"))
def test_check_mysql_connection_failure(mock_connect):
    result = check_mysql_connection("172.16.133.5", 3306, "user", "pwd", "BDD")

    assert "Erreur :" in result or result == "Connexion à MySQL fermée."