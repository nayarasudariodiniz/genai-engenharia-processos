import os
import re
import json
import requests
import streamlit as st

from io import BytesIO
from datetime import datetime
from html import escape
from pypdf import PdfReader
from crew import CaseEngprocessos

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


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

        Importante:
        - O relatório executivo não deve exibir o payload JSON.
        - O JSON deve ser gerado apenas para integração sistêmica.
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


def remover_secao_payload_do_markdown(texto: str) -> str:
    padroes = [
        r"(?is)#{1,6}\s*Payload JSON para Integração com Backlog.*?(?=#{1,6}\s|\Z)",
        r"(?is)#{1,6}\s*Payload JSON.*?(?=#{1,6}\s|\Z)",
        r"(?is)\*\*Payload JSON para Integração com Backlog\*\*.*?(?=\n\s*\*\*|\n\s*#{1,6}\s|\Z)",
        r"(?is)Payload JSON para Integração com Backlog\s*json\s*",
    ]

    texto_limpo = texto

    for padrao in padroes:
        texto_limpo = re.sub(padrao, "", texto_limpo).strip()

    texto_limpo = re.sub(r"(?im)^\s*json\s*$", "", texto_limpo).strip()

    return texto_limpo


def limpar_markdown(texto: str) -> str:
    texto = texto.replace("\\n", "\n")
    texto = re.sub(r"```markdown", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"```json[\s\S]*?```", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"```", "", texto)
    texto = re.sub(r"^\s*Final Answer:\s*", "", texto, flags=re.IGNORECASE)
    texto = remover_secao_payload_do_markdown(texto)
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


def markdown_para_html_basico(texto: str) -> str:
    texto = escape(texto)
    texto = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", texto)
    texto = re.sub(r"\*(.*?)\*", r"<i>\1</i>", texto)
    return texto


def gerar_pdf_analise(markdown_analise: str) -> bytes:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=48,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        "TituloPrincipal",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#111827"),
        spaceAfter=16,
        alignment=TA_LEFT
    )

    h1_style = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1f2937"),
        spaceBefore=14,
        spaceAfter=8
    )

    h2_style = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1f2937"),
        spaceBefore=12,
        spaceAfter=7
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#374151"),
        spaceAfter=7
    )

    bullet_style = ParagraphStyle(
        "Bullet",
        parent=body_style,
        leftIndent=16,
        firstLineIndent=-8,
        spaceAfter=5
    )

    elementos = [
        Paragraph("Análise Estruturada da Solicitação", titulo_style),
        Paragraph(
            f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            body_style
        ),
        Spacer(1, 12)
    ]

    linhas = markdown_analise.splitlines()

    for linha in linhas:
        linha = linha.strip()

        if not linha:
            elementos.append(Spacer(1, 6))
            continue

        if linha.startswith("# "):
            elementos.append(Paragraph(markdown_para_html_basico(linha.replace("# ", "", 1)), h1_style))

        elif linha.startswith("## "):
            elementos.append(Paragraph(markdown_para_html_basico(linha.replace("## ", "", 1)), h1_style))

        elif linha.startswith("### "):
            elementos.append(Paragraph(markdown_para_html_basico(linha.replace("### ", "", 1)), h2_style))

        elif linha.startswith("- "):
            elementos.append(Paragraph("• " + markdown_para_html_basico(linha.replace("- ", "", 1)), bullet_style))

        elif re.match(r"^\d+\.\s", linha):
            elementos.append(Paragraph(markdown_para_html_basico(linha), bullet_style))

        else:
            elementos.append(Paragraph(markdown_para_html_basico(linha), body_style))

    doc.build(elementos)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes


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

            markdown_analise = remover_json_da_resposta(resultado_texto)
            markdown_analise = limpar_markdown(markdown_analise)

            st.success("Análise concluída com sucesso!")

            st.markdown("## Análise estruturada")
            renderizar_analise_amigavel(markdown_analise)

            pdf_analise = gerar_pdf_analise(markdown_analise)

            st.download_button(
                label="Baixar análise em PDF",
                data=pdf_analise,
                file_name="analise_solicitacao.pdf",
                mime="application/pdf"
            )

            st.markdown("---")
            st.markdown("## Integração com backlog")

            if payload_json:
                st.download_button(
                    label="Baixar payload JSON de integração",
                    data=json.dumps(payload_json, ensure_ascii=False, indent=2),
                    file_name="payload_backlog.json",
                    mime="application/json"
                )

                if modo_integracao:
                    if simular_envio:
                        st.success("Envio simulado com sucesso. Nenhuma API real foi chamada.")
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