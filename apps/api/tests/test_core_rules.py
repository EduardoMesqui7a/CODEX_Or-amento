from core.text import eh_linha_de_titulo_ou_subtitulo, normalizar_texto


def test_normalizacao_basica():
    assert normalizar_texto("Concreto armado 30 MPa") == "concreto estrutural armado 30 megapascal"


def test_linha_titulo_detectada():
    assert eh_linha_de_titulo_ou_subtitulo("INSTALAÇÕES ELÉTRICAS")


def test_linha_item_nao_titulo():
    assert not eh_linha_de_titulo_ou_subtitulo("Concreto fck 30 MPa m3")

