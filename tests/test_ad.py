from scripts.ad_dns.Diag_AD_DNS import check_ad_ldap


def test_ad_connection(mocker):

    mock_connection = mocker.patch("ldap3.Connection")

    instance = mock_connection.return_value
    instance.bind.return_value = True

    result, message = check_ad_ldap(
        "192.168.1.10",
        "admin",
        "password"
    )

    assert result is True