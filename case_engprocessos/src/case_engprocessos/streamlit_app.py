import os
import re
import json
import requests
import streamlit as st

from datetime import datetime
from pypdf import PdfReader
from crew import CaseEngprocessos


API_BACKLOG_URL = os.getenv("API_BACKLOG_URL", "")
API_BACKLOG_TOKEN = os.getenv("API_BACKLOG_TOKEN", "")


def extrair_texto_pdf(arquivo_pdf) -> str:
    reader = PdfReader(arquivo_pdf)
    texto = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            texto += page_text + "\n"

    return texto.strip()


def build_inputs(solicitacao: str) -> dict:
    return {
        "topic": solicitacao,
        "current_year": str(datetime.now().year),
        "contexto_organizacional": """
        Banco de grande porte, com múltiplas áreas de negócio, alto volume de solicitações operacionais
        e atuação transversal da Engenharia de Processos.
        """,
        "desafio": """
        Receber solicitações textuais não estruturadas;
        identificar possíveis gargalos e causas;
        classificar criticidade e prioridade;
        sugerir análises ou abordagens iniciais;
        gerar uma saída estruturada para apoio à tomada de decisão.
        """,
        "dor_principal": """
        Solicitações recebidas de forma manual e não estruturada, gerando alto tempo de análise inicial,
        retrabalho, dificuldade de priorização, falta de padronização, dependência de conhecimento tácito
        e baixa rastreabilidade.
        """,
        "objetivo_da_solucao": """
        Transformar uma solicitação operacional não estruturada em uma saída estruturada, rastreável e acionável,
        contendo criticidade, impacto operacional, gargalos, hipóteses de causa-raiz e abordagem recomendada.
        """,
        "criterios_de_analise": """
        Considerar impacto operacional, financeiro, regulatório, risco operacional, experiência do cliente,
        volume, recorrência, SLA, retrabalho, handoffs, falhas sistêmicas, padronização, rastreabilidade e governança.
        """,
        "metodologias_recomendadas": """
        Lean, BPM, SIPOC, Ishikawa, 5 Porquês, análise de gargalos, análise de handoffs,
        priorização por criticidade e identificação de quick wins.
        """,
        "formato_esperado_saida": """
        A saída final deve conter:
        1. Relatório executivo em Markdown;
        2. Payload JSON válido para integração via API com sistema de backlog da Engenharia de Processos.
        """
    }


def executar_crew(solicitacao: str):
    inputs = build_inputs(solicitacao)
    return CaseEngprocessos().crew().kickoff(inputs=inputs)


def extrair_json_da_resposta(resposta: str):
    texto = str(resposta)
    match = re.search(r"\{[\s\S]*\}", texto)

    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def remover_json_da_resposta(resposta: str) -> str:
    return re.sub(r"\{[\s\S]*\}", "", str(resposta)).strip()


def limpar_markdown(texto: str) -> str:
    texto = texto.replace("\\n", "\n")
    texto = re.sub(r"```markdown", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"```", "", texto)
    texto = re.sub(r"^\s*Final Answer:\s*", "", texto, flags=re.IGNORECASE)
    texto = texto.strip()
    return texto


def renderizar_analise_amigavel(markdown_analise: str):
    markdown_analise = limpar_markdown(markdown_analise)

    st.markdown(
        """
        <style>
            .analise-container {
                background-color: #ffffff;
                border: 1px solid #e6e9ef;
                border-radius: 14px;
                padding: 26px;
                margin-top: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.04);
            }
            .analise-container h1,
            .analise-container h2,
            .analise-container h3 {
                color: #1f2937;
                margin-top: 1.1rem;
                margin-bottom: 0.6rem;
            }
            .analise-container p,
            .analise-container li {
                font-size: 16px;
                line-height: 1.65;
                color: #374151;
            }
            .analise-container ul {
                margin-top: 0.4rem;
                margin-bottom: 0.8rem;
            }
            .analise-container strong {
                color: #111827;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.container(border=True):
        st.markdown(markdown_analise)


def converter_payload_para_supabase(payload: dict) -> dict:
    return {
        "id_externo": payload.get("id_externo"),
        "criticidade": payload.get("classificacao", {}).get("criticidade"),
        "score_criticidade": payload.get("classificacao", {}).get("score_criticidade"),
        "processo_impactado": payload.get("solicitacao", {}).get("processo_impactado"),
        "resumo_executivo": payload.get("solicitacao", {}).get("resumo_executivo"),
        "impacto_operacional": payload.get("diagnostico", {}).get("impacto_operacional"),
        "abordagem_recomendada": payload.get("recomendacao", {}).get("abordagem_recomendada"),
        "payload": payload
    }


def enviar_payload_para_backlog(payload: dict, api_url: str):
    if not API_BACKLOG_TOKEN:
        raise ValueError("API_BACKLOG_TOKEN não configurado nos Secrets do Streamlit.")

    if not api_url:
        raise ValueError("API_BACKLOG_URL não configurada.")

    payload_supabase = converter_payload_para_supabase(payload)

    headers = {
        "apikey": API_BACKLOG_TOKEN,
        "Authorization": f"Bearer {API_BACKLOG_TOKEN}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    response = requests.post(
        api_url,
        json=payload_supabase,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()
    return response.json()


st.set_page_config(
    page_title="Triagem Inteligente - Engenharia de Processos",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Triagem Inteligente de Solicitações")
st.subheader("IA Generativa aplicada à Engenharia de Processos Bancários")

st.markdown("""
Esta aplicação recebe solicitações não estruturadas das áreas de negócio e utiliza uma crew multiagente
para identificar criticidade, impacto operacional, gargalos, possíveis causas-raiz e abordagem recomendada.
""")

with st.sidebar:
    st.header("Integração futura via API")

    modo_integracao = st.toggle(
        "Habilitar envio para API de backlog",
        value=False
    )

    st.caption(
        "Quando habilitado, o payload JSON gerado pela análise poderá ser enviado "
        "para um sistema de backlog da Engenharia de Processos."
    )

    api_url_editavel = st.text_input(
        "URL da API de backlog",
        value=API_BACKLOG_URL
    )

    simular_envio = st.toggle(
        "Simular envio sem chamar API real",
        value=True
    )


tipo_entrada = st.radio(
    "Como deseja informar a solicitação?",
    ["Texto livre", "E-mail colado", "PDF"]
)

solicitacao = ""

if tipo_entrada == "Texto livre":
    solicitacao = st.text_area(
        "Digite a solicitação não estruturada:",
        height=220,
        placeholder="Ex: O processo de onboarding está demorando muito..."
    )

elif tipo_entrada == "E-mail colado":
    solicitacao = st.text_area(
        "Cole aqui o conteúdo do e-mail:",
        height=260,
        placeholder="Cole o corpo do e-mail recebido pela área de negócio..."
    )

elif tipo_entrada == "PDF":
    arquivo_pdf = st.file_uploader(
        "Faça upload do PDF contendo a solicitação:",
        type=["pdf"]
    )

    if arquivo_pdf is not None:
        solicitacao = extrair_texto_pdf(arquivo_pdf)

        with st.expander("Texto extraído do PDF"):
            st.write(solicitacao)


if st.button("Analisar solicitação", type="primary"):
    if not solicitacao.strip():
        st.warning("Informe uma solicitação antes de executar a análise.")
    else:
        try:
            with st.spinner("Executando análise multiagente..."):
                resultado = executar_crew(solicitacao)

            resultado_texto = str(resultado)
            payload_json = extrair_json_da_resposta(resultado_texto)
            markdown_analise = limpar_markdown(remover_json_da_resposta(resultado_texto))

            st.success("Análise concluída com sucesso!")

            st.markdown("## Análise estruturada")
            renderizar_analise_amigavel(markdown_analise)

            st.download_button(
                label="Baixar análise em Markdown",
                data=markdown_analise,
                file_name="analise_solicitacao.md",
                mime="text/markdown"
            )

            st.markdown("---")
            st.markdown("## Integração com backlog")

            if payload_json:
                st.info(
                    "Payload JSON de integração gerado com sucesso. "
                    "Ele não será exibido na tela, mas está disponível para download "
                    "ou envio futuro via API."
                )

                st.download_button(
                    label="Baixar payload JSON de integração",
                    data=json.dumps(payload_json, ensure_ascii=False, indent=2),
                    file_name="payload_backlog.json",
                    mime="application/json"
                )

                if modo_integracao:
                    if simular_envio:
                        st.success("Envio simulado com sucesso. Nenhuma API real foi chamada.")
                        st.caption(f"URL configurada: {api_url_editavel}")
                    else:
                        try:
                            with st.spinner("Enviando payload para API de backlog..."):
                                enviar_payload_para_backlog(
                                    payload_json,
                                    api_url_editavel
                                )

                            st.success("Payload enviado com sucesso para o sistema de backlog.")

                        except Exception as api_error:
                            st.warning(
                                "A análise foi gerada com sucesso, mas houve erro ao enviar "
                                "o payload para a API de backlog."
                            )
                            st.exception(api_error)

            else:
                st.warning(
                    "A análise foi concluída, mas não foi possível localizar "
                    "um payload JSON válido."
                )

        except Exception as e:
            st.error("Erro ao executar a análise.")
            st.exception(e)