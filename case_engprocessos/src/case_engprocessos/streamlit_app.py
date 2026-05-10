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


SECOES_ANALISE = {
    "resumo_executivo_secao": "1. Resumo Executivo",
    "solicitacao_normalizada": "2. Solicitação Normalizada",
    "processo_impactado_secao": "3. Processo Impactado",
    "areas_envolvidas": "4. Áreas Envolvidas",
    "sistemas_mencionados": "5. Sistemas Mencionados",
    "gargalos_identificados_secao": "6. Gargalos Identificados",
    "causas_raiz_secao": "7. Possíveis Causas-Raiz",
    "criticidade_prioridade_secao": "8. Criticidade e Prioridade",
    "impactos_operacionais_secao": "9. Impactos Operacionais",
    "abordagem_recomendada_secao": "10. Abordagem Recomendada",
    "quick_wins": "11. Quick Wins",
    "proximos_passos_secao": "12. Próximos Passos",
    "encaminhamento_recomendado": "13. Encaminhamento Recomendado",
}


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
        r"(?is)-+\s*PARTE\s*2\s*[—-]\s*JSON\s*DE\s*INTEGRAÇÃO\s*-+.*",
        r"(?is)PARTE\s*2\s*[—-]\s*JSON\s*DE\s*INTEGRAÇÃO.*",
        r"(?s)\{.*\}",
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
    return texto.strip()


def extrair_secao(markdown_texto: str, titulo_secao: str) -> str:
    padrao = rf"(?is)##\s*{re.escape(titulo_secao)}\s*(.*?)(?=\n##\s*\d+\.|\Z)"
    match = re.search(padrao, markdown_texto)

    if not match:
        return "não informado"

    conteudo = match.group(1).strip()
    return conteudo if conteudo else "não informado"


def extrair_secoes_analise(markdown_analise: str) -> dict:
    return {
        coluna: extrair_secao(markdown_analise, titulo)
        for coluna, titulo in SECOES_ANALISE.items()
    }


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

    for linha in markdown_analise.splitlines():
        linha = linha.strip()

        if not linha:
            elementos.append(Spacer(1, 6))
            continue

        if linha.startswith("# "):
            elementos.append(
                Paragraph(markdown_para_html_basico(linha.replace("# ", "", 1)), h1_style)
            )
        elif linha.startswith("## "):
            elementos.append(
                Paragraph(markdown_para_html_basico(linha.replace("## ", "", 1)), h1_style)
            )
        elif linha.startswith("### "):
            elementos.append(
                Paragraph(markdown_para_html_basico(linha.replace("### ", "", 1)), h2_style)
            )
        elif linha.startswith("- "):
            elementos.append(
                Paragraph("• " + markdown_para_html_basico(linha.replace("- ", "", 1)), bullet_style)
            )
        elif re.match(r"^\d+\.\s", linha):
            elementos.append(
                Paragraph(markdown_para_html_basico(linha), bullet_style)
            )
        else:
            elementos.append(
                Paragraph(markdown_para_html_basico(linha), body_style)
            )

    doc.build(elementos)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes


def converter_payload_para_supabase(
    payload: dict,
    nome: str,
    email: str,
    area_negocio: str,
    markdown_analise: str
) -> dict:
    solicitacao = payload.get("solicitacao", {})
    classificacao = payload.get("classificacao", {})
    diagnostico = payload.get("diagnostico", {})
    recomendacao = payload.get("recomendacao", {})

    secoes = extrair_secoes_analise(markdown_analise)

    return {
        "nome": nome,
        "email": email,
        "area_negocio": area_negocio,
        "id_externo": payload.get("id_externo", "não informado"),
        "criticidade": classificacao.get("criticidade", "não informado"),
        "score_criticidade": classificacao.get("score_criticidade", 0),
        "processo_impactado": solicitacao.get("processo_impactado", "não informado"),
        "resumo_executivo": solicitacao.get("resumo_executivo", "não informado"),
        "impacto_operacional": diagnostico.get("impacto_operacional", "não informado"),
        "abordagem_recomendada": recomendacao.get("abordagem_recomendada", "não informado"),
        "analise_completa": markdown_analise,
        "payload": payload,
        **secoes
    }


def enviar_payload_para_backlog(
    payload: dict,
    api_url: str,
    nome: str,
    email: str,
    area_negocio: str,
    markdown_analise: str
):
    if not API_BACKLOG_TOKEN:
        raise ValueError("API_BACKLOG_TOKEN não configurado nos Secrets do Streamlit.")

    if not api_url:
        raise ValueError("API_BACKLOG_URL não configurada.")

    payload_supabase = converter_payload_para_supabase(
        payload=payload,
        nome=nome,
        email=email,
        area_negocio=area_negocio,
        markdown_analise=markdown_analise
    )

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


def validar_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


st.set_page_config(
    page_title="Triagem Inteligente - Engenharia de Processos",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Triagem Inteligente de Solicitações")
st.subheader("IA Generativa aplicada à Engenharia de Processos")

st.markdown("""
Esta aplicação recebe solicitações não estruturadas das áreas de negócio e utiliza uma crew multiagente
para identificar criticidade, impacto operacional, gargalos, possíveis causas-raiz e abordagem recomendada.
""")

st.markdown("### Dados do solicitante")

col1, col2 = st.columns(2)

with col1:
    nome = st.text_input("Nome completo")

with col2:
    email = st.text_input("E-mail corporativo")

area_negocio = st.text_input("Área de negócio")

st.markdown("### Solicitação")

tipo_entrada = st.radio(
    "Como deseja informar a solicitação?",
    ["Texto livre", "PDF"]
)

solicitacao = ""

if tipo_entrada == "Texto livre":
    solicitacao = st.text_area(
        "Digite a solicitação não estruturada:",
        height=220,
        placeholder="Ex: O processo de onboarding está demorando muito..."
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


if st.button("Enviar solicitação", type="primary"):
    if not nome.strip():
        st.warning("Informe o nome do solicitante.")
    elif not email.strip():
        st.warning("Informe o e-mail do solicitante.")
    elif not validar_email(email):
        st.warning("Informe um e-mail válido.")
    elif not area_negocio.strip():
        st.warning("Informe a área de negócio.")
    elif not solicitacao.strip():
        st.warning("Informe uma solicitação antes de enviar.")
    else:
        try:
            with st.spinner("Analisando e enviando solicitação..."):
                resultado = executar_crew(solicitacao)

            resultado_texto = str(resultado)
            payload_json = extrair_json_da_resposta(resultado_texto)

            markdown_analise = limpar_markdown(
                remover_json_da_resposta(resultado_texto)
            )

            pdf_analise = gerar_pdf_analise(markdown_analise)

            st.download_button(
                label="Baixar análise em PDF",
                data=pdf_analise,
                file_name="analise_solicitacao.pdf",
                mime="application/pdf"
            )

            if payload_json:
                try:
                    with st.spinner("Enviando solicitação para o sistema de backlog..."):
                        enviar_payload_para_backlog(
                            payload=payload_json,
                            api_url=API_BACKLOG_URL,
                            nome=nome,
                            email=email,
                            area_negocio=area_negocio,
                            markdown_analise=markdown_analise
                        )

                    id_externo = payload_json.get("id_externo", "não informado")

                    st.success(
                        f"Solicitação nº {id_externo} enviada com sucesso! "
                        "Em breve a área de processos entrará em contato."
                    )

                except Exception as api_error:
                    st.warning(
                        "A análise foi gerada com sucesso, mas houve erro ao enviar "
                        "a solicitação para o sistema de backlog."
                    )
                    st.exception(api_error)

            else:
                st.warning(
                    "A análise foi concluída, mas não foi possível localizar "
                    "um payload JSON válido para integração."
                )

        except Exception as e:
            st.error("Erro ao executar a análise.")
            st.exception(e)