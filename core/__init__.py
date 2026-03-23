from .constants import MODELO_EMBEDDING, PESO_FUZZY, PESO_REGRAS, PESO_SEMANTICO
from .excel_io import (
    aplicar_resultado_no_excel_original,
    carregar_excel,
    encontrar_ultima_coluna_com_dados,
    obter_celula_segura_para_escrita,
    obter_nome_coluna_referencia,
)
from .pipeline import processar_preenchimento
from .scoring import buscar_melhor_item_em_lote, preparar_base_para_busca, score_regras
from .text import eh_linha_de_titulo_ou_subtitulo, normalizar_texto

