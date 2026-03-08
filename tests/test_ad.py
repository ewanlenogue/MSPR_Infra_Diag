import pytest
from unittest.mock import patch, MagicMock, ANY
from scripts.ad_dns.Diag_AD_DNS import check_ad_ldap  # adapte selon ton chemin

@patch("scripts.ad_dns.Diag_AD_DNS.Connection")
@patch("scripts.ad_dns.Diag_AD_DNS.Server")
def test_check_ad_ldap_success(mock_server, mock_connection):
    # Configuration du mock pour la connexion
    mock_conn_instance = MagicMock()
    mock_connection.return_value = mock_conn_instance
    mock_conn_instance.unbind.return_value = None  # simule le unbind

    # Appel de la fonction
    result, message = check_ad_ldap("192.168.1.10", "user", "password")

    # Assertions
    mock_server.assert_called_once_with("192.168.1.10", get_info=ANY)  # ✅ ANY importé
    mock_connection.assert_called_once_with(
        mock_server.return_value, user="user", password="password", auto_bind=True, receive_timeout=3
    )
    mock_conn_instance.unbind.assert_called_once()
    assert result is True
    assert message == "Authentification réussie"