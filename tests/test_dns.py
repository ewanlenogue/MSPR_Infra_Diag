import pytest
import dns.resolver
from unittest.mock import patch, MagicMock
from scripts.ad_dns.Diag_AD_DNS import check_dns  # adapte selon ton chemin

# --- Test : résolution DNS réussie ---
@patch("scripts.ad_dns.Diag_AD_DNS.dns.resolver.Resolver.resolve")
def test_check_dns_success(mock_resolve):
    # On simule la réponse du resolver
    mock_answer = [MagicMock()]
    mock_answer[0].to_text.return_value = "192.168.1.100"
    mock_resolve.return_value = mock_answer

    result, message = check_dns("192.168.1.10", "example.com")

    mock_resolve.assert_called_once_with("example.com", "A")
    assert result is True
    assert "Résolu (192.168.1.100)" in message

# --- Test : timeout DNS ---
@patch("scripts.ad_dns.Diag_AD_DNS.dns.resolver.Resolver.resolve", side_effect=dns.resolver.Timeout)
def test_check_dns_timeout(mock_resolve):
    result, message = check_dns("192.168.1.10", "example.com")
    assert result is False
    assert "Timeout" in message

# --- Test : autre erreur DNS ---
@patch("scripts.ad_dns.Diag_AD_DNS.dns.resolver.Resolver.resolve", side_effect=Exception("Erreur quelconque"))
def test_check_dns_exception(mock_resolve):
    result, message = check_dns("192.168.1.10", "example.com")
    assert result is False
    assert "Échec de résolution" in message