from typing import Callable, Dict, List, Optional, Tuple

import pandas as pd

from .excel_io import obter_nome_coluna_referencia
from .scoring import buscar_melhor_item_em_lote, preparar_base_para_busca
from .text import eh_linha_de_titulo_ou_subtitulo, normalizar_texto


ProgressCallback = Callable[[float, str], None]


def processar_preenchimento(
    df_base: pd.DataFrame,
    df_destino: pd.DataFrame,
    coluna_busca_destino: str,
    colunas_base_retorno: List[str],
    colunas_destino_preencher: List[str],
    coluna_texto_base: str,
    score_minimo: float,
    top_k_candidatos: int,
    progress_callback: Optional[ProgressCallback] = None,
) -> pd.DataFrame:
    def atualizar_progresso(fracao: float, mensagem: str):
        if progress_callback:
            progress_callback(fracao, mensagem)

    df_destino_proc = df_destino.copy()
    score_col = "IA_SCORE"
    match_col = "IA_DESCRICAO_ENCONTRADA"
    idx_col = "IA_LINHA_BASE"
    tipo_col = "IA_TIPO_LINHA"
    referencia_col = obter_nome_coluna_referencia(coluna_texto_base)

    for col in [score_col, match_col, idx_col, tipo_col, referencia_col]:
        if col not in df_destino_proc.columns:
            df_destino_proc[col] = None

    atualizar_progresso(0.01, "Preparando base semântica")
    df_base_proc, _, indice = preparar_base_para_busca(df_base, coluna_texto_base)
    atualizar_progresso(0.10, "Base preparada")

    if coluna_busca_destino not in df_destino_proc.columns:
        atualizar_progresso(1.0, "Coluna de busca não encontrada")
        return df_destino_proc

    total = len(df_destino_proc)
    buscas_originais = df_destino_proc[coluna_busca_destino].tolist()

    mapa_buscas_validas: Dict[str, str] = {}
    for busca in buscas_originais:
        if busca is None or str(busca).strip() == "":
            continue
        if eh_linha_de_titulo_ou_subtitulo(busca):
            continue
        busca_norm = normalizar_texto(str(busca))
        if busca_norm:
            mapa_buscas_validas[str(busca)] = busca_norm

    buscas_norm_unicas = list(set(mapa_buscas_validas.values()))
    atualizar_progresso(0.25, "Calculando correspondências")

    resultados_unicos = buscar_melhor_item_em_lote(
        buscas_norm_unicas=buscas_norm_unicas,
        df_base_proc=df_base_proc,
        indice=indice,
        top_k_candidatos=top_k_candidatos,
    )
    atualizar_progresso(0.55, "Aplicando preenchimento")

    cache_busca_original: Dict[str, Optional[Tuple[int, dict]]] = {}
    for busca_original, busca_norm in mapa_buscas_validas.items():
        cache_busca_original[busca_original] = resultados_unicos.get(busca_norm)

    for i, busca in enumerate(buscas_originais):
        if busca is None or str(busca).strip() == "":
            df_destino_proc.at[i, tipo_col] = "Vazia"
            continue

        if eh_linha_de_titulo_ou_subtitulo(busca):
            df_destino_proc.at[i, tipo_col] = "Título/Subtítulo"
            continue

        res = cache_busca_original.get(str(busca))
        if res is None:
            df_destino_proc.at[i, tipo_col] = "Sem correspondência"
            df_destino_proc.at[i, referencia_col] = "Sem correspondência"
            continue

        idx_match, det = res
        referencia_base = df_base_proc.iloc[idx_match][coluna_texto_base]

        if det["score_final"] < score_minimo:
            df_destino_proc.at[i, score_col] = det["score_final"]
            df_destino_proc.at[i, match_col] = "Confiança baixa"
            df_destino_proc.at[i, idx_col] = int(idx_match) + 2
            df_destino_proc.at[i, tipo_col] = "Item, confiança baixa"
            df_destino_proc.at[i, referencia_col] = referencia_base
        else:
            for col_base, col_dest in zip(colunas_base_retorno, colunas_destino_preencher):
                df_destino_proc.at[i, col_dest] = df_base_proc.iloc[idx_match][col_base]
            df_destino_proc.at[i, score_col] = det["score_final"]
            df_destino_proc.at[i, match_col] = referencia_base
            df_destino_proc.at[i, idx_col] = int(idx_match) + 2
            df_destino_proc.at[i, tipo_col] = "Item"
            df_destino_proc.at[i, referencia_col] = referencia_base

        if total and (i % 25 == 0 or i == total - 1):
            atualizar_progresso(0.55 + 0.45 * ((i + 1) / total), f"Linha {i + 1}/{total}")

    atualizar_progresso(1.0, "Processamento concluído")
    return df_destino_proc

