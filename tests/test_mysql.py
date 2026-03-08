from ..scripts.mysql.StatusMysql import check_mysql_connection


def test_mysql_connection(mocker):

    mock_conn = mocker.patch("mysql.connector.connect")

    instance = mock_conn.return_value
    instance.is_connected.return_value = True

    result = check_mysql_connection(
        "127.0.0.1",
        3306,
        "user",
        "password",
        "db"
    )

    assert result is True
