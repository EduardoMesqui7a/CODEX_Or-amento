import streamlit as st
import pandas as pd

from core.excel_io import (
    aplicar_resultado_no_excel_original,
    carregar_excel,
    obter_nome_coluna_referencia,
)
from core.pipeline import processar_preenchimento
from core.scoring import carregar_modelo


st.set_page_config(page_title="Orçamento IA - VSN", layout="wide")
st.title("Orçamento IA - VSN")
st.caption("Importe a base de dados e a planilha a preencher, escolha as colunas e gere o arquivo preenchido.")


with st.sidebar:
    st.header("Configurações")
    score_minimo = st.slider("Score mínimo para preencher", 0.0, 1.0, 0.35, 0.01)
    header_base = st.number_input("Linha do cabeçalho da base", min_value=1, value=1, step=1)
    header_dest = st.number_input("Linha do cabeçalho da planilha a preencher", min_value=1, value=1, step=1)
    st.markdown("Sugestão, se a base tem cabeçalho na linha 3 do Excel, informe 3.")
    top_k_candidatos = st.number_input("Qtd. de candidatos por busca", min_value=5, max_value=100, value=30, step=5)


col1, col2 = st.columns(2)
with col1:
    st.subheader("1. Base de dados")
    arquivo_base = st.file_uploader("Importar base de dados", type=["xlsx", "xlsm", "xls"], key="base")
with col2:
    st.subheader("2. Planilha a preencher")
    arquivo_destino = st.file_uploader("Importar planilha de destino", type=["xlsx", "xlsm", "xls"], key="destino")


if arquivo_base and arquivo_destino:
    try:
        carregar_modelo()

        arquivo_base.seek(0)
        xls_base = pd.ExcelFile(arquivo_base)
        arquivo_destino.seek(0)
        xls_dest = pd.ExcelFile(arquivo_destino)

        col3, col4 = st.columns(2)
        with col3:
            aba_base = st.selectbox("Aba da base", options=xls_base.sheet_names)
        with col4:
            aba_dest = st.selectbox("Aba da planilha a preencher", options=xls_dest.sheet_names)

        df_base = carregar_excel(arquivo_base, aba_base, int(header_base) - 1)
        df_destino = carregar_excel(arquivo_destino, aba_dest, int(header_dest) - 1)

        st.divider()
        st.subheader("3. Mapeamento das colunas")

        c1, c2 = st.columns(2)
        with c1:
            coluna_texto_base = st.selectbox(
                "Coluna da base usada para comparação semântica",
                options=df_base.columns.tolist(),
                index=df_base.columns.tolist().index("DESCRIÇÃO") if "DESCRIÇÃO" in df_base.columns else 0,
            )
        with c2:
            coluna_busca_destino = st.selectbox(
                "Coluna da planilha de destino usada como busca",
                options=df_destino.columns.tolist(),
                index=df_destino.columns.tolist().index("G") if "G" in df_destino.columns else 0,
            )

        st.info(
            f"A referência do item encontrado será gravada em uma nova coluna no final da planilha, "
            f"usando os valores da coluna '{coluna_texto_base}' da base."
        )

        st.markdown("### Colunas da base que deseja obter")
        colunas_base_retorno = st.multiselect(
            "Selecione as colunas da base",
            options=df_base.columns.tolist(),
            default=[c for c in ["R$ CAPEX/NOVO", "CÓDIGO", "FONTE", "UNID", "SEM BDI"] if c in df_base.columns],
        )

        st.markdown("### Colunas da planilha de destino que receberão os dados")
        st.caption("A ordem deve corresponder exatamente à ordem escolhida na base.")

        colunas_destino_preencher = []
        for i, col_base in enumerate(colunas_base_retorno, start=1):
            escolha = st.selectbox(
                f"Destino para '{col_base}'",
                options=df_destino.columns.tolist(),
                key=f"dest_{i}_{col_base}",
            )
            colunas_destino_preencher.append(escolha)

        if len(colunas_base_retorno) != len(colunas_destino_preencher):
            st.error("A quantidade de colunas da base e de destino precisa ser a mesma.")
        elif len(set(colunas_destino_preencher)) != len(colunas_destino_preencher):
            st.error("Você repetiu colunas de destino. Cada coluna de destino deve ser usada apenas uma vez.")
        else:
            st.divider()
            st.subheader("4. Prévia")

            p1, p2 = st.columns(2)
            with p1:
                st.write("Base")
                st.dataframe(df_base.head(10), use_container_width=True)
            with p2:
                st.write("Planilha a preencher")
                st.dataframe(df_destino.head(10), use_container_width=True)

            if st.button("Processar preenchimento", type="primary"):
                status = st.empty()
                progresso = st.progress(0.0)

                def progress_callback(fracao: float, mensagem: str):
                    status.info(f"Em processamento. {mensagem}")
                    progresso.progress(max(0.0, min(fracao, 1.0)))

                resultado = processar_preenchimento(
                    df_base=df_base,
                    df_destino=df_destino,
                    coluna_busca_destino=coluna_busca_destino,
                    colunas_base_retorno=colunas_base_retorno,
                    colunas_destino_preencher=colunas_destino_preencher,
                    coluna_texto_base=coluna_texto_base,
                    score_minimo=score_minimo,
                    top_k_candidatos=int(top_k_candidatos),
                    progress_callback=progress_callback,
                )

                status.success("Processamento concluído.")
                st.dataframe(resultado.head(50), use_container_width=True)

                excel_bytes = aplicar_resultado_no_excel_original(
                    uploaded_file=arquivo_destino,
                    nome_aba=aba_dest,
                    header_index=int(header_dest) - 1,
                    df_original=df_destino,
                    df_resultado=resultado,
                    colunas_destino_preencher=colunas_destino_preencher,
                    nome_coluna_referencia=obter_nome_coluna_referencia(coluna_texto_base),
                )

                st.download_button(
                    label="Baixar planilha preenchida",
                    data=excel_bytes,
                    file_name="planilha_preenchida.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
    except Exception as e:
        st.error(f"Erro ao processar os arquivos: {e}")
else:
    st.info("Importe os dois arquivos para habilitar o mapeamento e o preenchimento automático.")

