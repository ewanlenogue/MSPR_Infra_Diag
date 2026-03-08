from ..scripts.ad_dns.Diag_AD_DNS import check_dns


def test_dns_success(mocker):

    mock_resolve = mocker.patch("dns.resolver.Resolver.resolve")

    mock_answer = mocker.Mock()
    mock_answer.__iter__.return_value = [
        mocker.Mock(to_text=lambda: "192.168.1.1")
    ]

    mock_resolve.return_value = mock_answer

    result, ip = check_dns("192.168.1.10", "example.com")

    assert result is True