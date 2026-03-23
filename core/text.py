import re

import pandas as pd
from unidecode import unidecode


def normalizar_texto(texto: str) -> str:
    if texto is None or pd.isna(texto):
        return ""

    texto = str(texto).strip().lower()
    texto = unidecode(texto)

    substituicoes = {
        "fck": "resistencia caracteristica",
        "mpa": "megapascal",
        "concreto armado": "concreto estrutural armado",
        "concreto simples": "concreto sem armadura",
        "divisoria": "parede divisoria vedacao compartimentacao interna",
        "drywall": "parede leve em gesso acartonado",
        "alvenaria": "parede de alvenaria vedacao",
        "parede": "vedacao parede fechamento",
        "aco": "aco armadura",
        "armacao": "armadura aco",
        "forma": "forma madeira compensado",
        "tubo": "tubulacao",
        "tubos": "tubulacao",
        "eletroduto": "tubulacao eletrica conduite",
        "conduite": "tubulacao eletrica eletroduto",
        "piso": "pavimentacao revestimento piso",
        "bloco": "alvenaria bloco",
        "reboco": "argamassa revestimento",
        "chapisco": "argamassa aderencia",
        "escavacao": "movimento de terra escavacao",
        "aterro": "movimento de terra aterro compactacao",
        "lastro": "camada de regularizacao lastro",
    }

    for de, para in substituicoes.items():
        texto = texto.replace(de, para)

    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def eh_linha_de_titulo_ou_subtitulo(texto) -> bool:
    if texto is None or str(texto).strip() == "":
        return True

    texto_original = str(texto).strip()
    texto_normalizado = normalizar_texto(texto_original)
    palavras = texto_normalizado.split()

    if len(texto_normalizado) <= 3:
        return True

    termos_genericos = {
        "servicos preliminares",
        "fundacoes",
        "estrutura",
        "superestrutura",
        "arquitetura",
        "instalacoes",
        "instalacoes eletricas",
        "instalacoes hidraulicas",
        "urbanizacao",
        "cobertura",
        "revestimentos",
        "esquadrias",
        "pintura",
        "demolicoes",
        "demolicao",
        "movimento de terra",
        "infraestrutura",
        "equipamentos",
        "geral",
        "administracao local",
    }
    if texto_normalizado in termos_genericos:
        return True

    unidades = {"m", "m2", "m3", "kg", "un", "vb", "cj", "h", "mes"}
    tem_numero = bool(re.search(r"\d", texto_normalizado))
    tem_unidade = any(unidade in palavras for unidade in unidades)

    if len(palavras) <= 3 and not tem_numero and not tem_unidade:
        return True

    letras = [caractere for caractere in texto_original if caractere.isalpha()]
    if letras:
        proporcao_maiuscula = sum(1 for caractere in letras if caractere.isupper()) / len(letras)
        if proporcao_maiuscula > 0.8 and len(palavras) <= 5:
            return True

    return False

