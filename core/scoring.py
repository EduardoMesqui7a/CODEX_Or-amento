from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import pandas as pd
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors

from .constants import MODELO_EMBEDDING, PESO_FUZZY, PESO_REGRAS, PESO_SEMANTICO
from .text import normalizar_texto


@lru_cache(maxsize=1)
def carregar_modelo():
    return SentenceTransformer(MODELO_EMBEDDING)


def score_regras(busca_norm: str, descricao_norm: str) -> float:
    score = 0.0

    numeros_relevantes = ["5", "8", "10", "12", "15", "20", "25", "30", "35", "40", "50"]
    for numero in numeros_relevantes:
        if numero in busca_norm and numero in descricao_norm:
            score += 0.10

    pares = [
        ("concreto", "concreto"),
        ("armado", "armado"),
        ("argamassa", "argamassa"),
        ("alvenaria", "alvenaria"),
        ("divisoria", "divisoria"),
        ("drywall", "drywall"),
        ("piso", "piso"),
        ("tubulacao", "tubulacao"),
        ("eletrica", "eletrica"),
        ("hidraulica", "hidraulica"),
        ("escavacao", "escavacao"),
        ("aterro", "aterro"),
        ("forma", "forma"),
        ("aco", "aco"),
        ("vedacao", "vedacao"),
        ("bloco", "bloco"),
        ("porta", "porta"),
        ("janela", "janela"),
    ]

    for termo_busca, termo_desc in pares:
        if termo_busca in busca_norm and termo_desc in descricao_norm:
            score += 0.08

    if "divisoria" in busca_norm and any(
        valor in descricao_norm for valor in ["drywall", "alvenaria", "parede", "vedacao"]
    ):
        score += 0.20

    if "concreto" in busca_norm and "megapascal" in busca_norm:
        if "concreto" in descricao_norm and any(
            valor in descricao_norm for valor in ["megapascal", "resistencia caracteristica"]
        ):
            score += 0.20

    return min(score, 1.0)


def preparar_base_para_busca(df_base: pd.DataFrame, coluna_texto_base: str):
    modelo = carregar_modelo()

    df_base_proc = df_base.copy()
    df_base_proc[coluna_texto_base] = df_base_proc[coluna_texto_base].fillna("").astype(str)
    df_base_proc["__texto_base_norm__"] = df_base_proc[coluna_texto_base].map(normalizar_texto)

    textos_norm = df_base_proc["__texto_base_norm__"].tolist()
    embeddings = modelo.encode(
        textos_norm,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
        batch_size=128,
    )

    indice = NearestNeighbors(metric="cosine", algorithm="auto")
    indice.fit(embeddings)

    return df_base_proc, embeddings, indice


def buscar_melhor_item_em_lote(
    buscas_norm_unicas: List[str],
    df_base_proc: pd.DataFrame,
    indice,
    top_k_candidatos: int,
) -> Dict[str, Optional[Tuple[int, dict]]]:
    modelo = carregar_modelo()
    if not buscas_norm_unicas:
        return {}

    emb_buscas = modelo.encode(
        buscas_norm_unicas,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
        batch_size=128,
    )

    k = min(top_k_candidatos, len(df_base_proc))
    distancias_lote, indices_lote = indice.kneighbors(emb_buscas, n_neighbors=k)

    resultados = {}
    for pos_busca, busca_norm in enumerate(buscas_norm_unicas):
        melhores_indices = indices_lote[pos_busca]
        melhores_distancias = distancias_lote[pos_busca]

        melhor_idx = None
        melhor_score = -1.0
        melhor_det = None

        for pos_cand, idx_base in enumerate(melhores_indices):
            texto_base_norm = df_base_proc.iloc[idx_base]["__texto_base_norm__"]
            score_sem = 1.0 - float(melhores_distancias[pos_cand])
            score_fuzzy = fuzz.token_set_ratio(busca_norm, texto_base_norm) / 100.0
            score_reg = score_regras(busca_norm, texto_base_norm)

            score_final = PESO_SEMANTICO * score_sem + PESO_FUZZY * score_fuzzy + PESO_REGRAS * score_reg

            if score_final > melhor_score:
                melhor_score = score_final
                melhor_idx = int(idx_base)
                melhor_det = {
                    "score_final": round(score_final, 4),
                    "score_semantico": round(score_sem, 4),
                    "score_fuzzy": round(score_fuzzy, 4),
                    "score_regras": round(score_reg, 4),
                }

        resultados[busca_norm] = None if melhor_idx is None else (melhor_idx, melhor_det)

    return resultados

