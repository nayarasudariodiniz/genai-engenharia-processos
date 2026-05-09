#!/usr/bin/env python
import sys
import json
import warnings

from datetime import datetime
from crew import CaseEngprocessos

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


CENARIOS = {
    "onboarding": """
    O processo de onboarding está demorando muito.
    Existem muitos retornos manuais entre áreas e retrabalho no preenchimento de formulários.
    """,

    "aprovacao_credito": """
    Temos alto volume de chamados relacionados à aprovação de crédito e suspeitamos que existam gargalos operacionais.
    """,

    "atendimento_cliente": """
    O processo de atendimento possui muitas transferências entre times e o cliente frequentemente precisa repetir informações.
    """,

    "fechamento_operacional": """
    Existe divergência frequente entre sistemas durante o fechamento operacional, gerando retrabalho manual e atraso nas entregas.
    """
}


CENARIO_PADRAO = "onboarding"


def build_inputs(nome_cenario: str = CENARIO_PADRAO) -> dict:
    """
    Monta os inputs para execução da crew no contexto de banco,
    Engenharia de Processos, governança e eficiência operacional.
    """

    if nome_cenario not in CENARIOS:
        raise ValueError(
            f"Cenário inválido: {nome_cenario}. "
            f"Cenários disponíveis: {', '.join(CENARIOS.keys())}"
        )

    solicitacao = CENARIOS[nome_cenario]

    return {
        "topic": solicitacao,
        "cenario": nome_cenario,
        "current_year": str(datetime.now().year),

        "contexto_organizacional": """
        Banco de grande porte, com múltiplas áreas de negócio, alto volume de solicitações operacionais
        e atuação transversal da Engenharia de Processos na identificação, análise e evolução dos processos.
        """,

        "desafio": """
        Receber solicitações textuais não estruturadas;
        identificar possíveis gargalos e causas;
        classificar criticidade e prioridade;
        sugerir análises ou abordagens iniciais;
        gerar uma saída estruturada para apoio à tomada de decisão.
        """,

        "dor_principal": """
        Grande parte das solicitações recebidas pelas áreas de negócio ocorre de forma manual e não estruturada,
        gerando alto tempo de análise inicial, retrabalho, dificuldade de priorização, falta de padronização,
        dependência de conhecimento tácito e baixa rastreabilidade das análises realizadas.
        """,

        "objetivo_da_solucao": """
        Transformar uma solicitação operacional não estruturada em uma saída estruturada, rastreável e acionável,
        contendo criticidade, impacto operacional, possíveis gargalos, hipóteses de causa-raiz e melhor abordagem
        inicial de atuação pela Engenharia de Processos.
        """,

        "criterios_de_analise": """
        A análise deve considerar:
        - impacto operacional;
        - impacto financeiro;
        - impacto regulatório;
        - risco operacional;
        - experiência do cliente;
        - volume ou recorrência;
        - SLA;
        - retrabalho;
        - handoffs entre áreas;
        - falhas sistêmicas;
        - ausência de padronização;
        - rastreabilidade;
        - governança.
        """,

        "metodologias_recomendadas": """
        Utilizar raciocínio baseado em Engenharia de Processos, Lean, BPM, SIPOC, Ishikawa, 5 Porquês,
        análise de gargalos, análise de handoffs, priorização por criticidade e identificação de quick wins.
        """,

        "formato_esperado_saida": """
        A saída final deve conter:
        - resumo executivo;
        - solicitação normalizada;
        - processo impactado;
        - áreas envolvidas;
        - sistemas mencionados;
        - sintomas operacionais;
        - possíveis gargalos;
        - possíveis causas-raiz;
        - criticidade/prioridade;
        - impacto operacional;
        - abordagem inicial recomendada;
        - próximos passos;
        - encaminhamento sugerido;
        - registro rastreável para governança.
        """
    }


def run():
    """
    Executa a crew para um cenário específico.

    Para mudar o cenário, altere CENARIO_PADRAO ou execute:
    python main.py onboarding
    python main.py aprovacao_credito
    python main.py atendimento_cliente
    python main.py fechamento_operacional
    python main.py todos
    """

    nome_cenario = sys.argv[1] if len(sys.argv) > 1 else CENARIO_PADRAO

    if nome_cenario == "todos":
        resultados = {}

        for cenario in CENARIOS.keys():
            print(f"\n\n===== EXECUTANDO CENÁRIO: {cenario.upper()} =====\n")

            inputs = build_inputs(cenario)

            try:
                result = CaseEngprocessos().crew().kickoff(inputs=inputs)
                resultados[cenario] = result
                print(f"\n\n===== RESULTADO DO CENÁRIO: {cenario.upper()} =====\n")
                print(result)

            except Exception as e:
                resultados[cenario] = f"Erro ao executar cenário {cenario}: {e}"
                print(resultados[cenario])

        return resultados

    inputs = build_inputs(nome_cenario)

    try:
        result = CaseEngprocessos().crew().kickoff(inputs=inputs)
        print(f"\n\n===== RESULTADO FINAL DA CREW | CENÁRIO: {nome_cenario.upper()} =====\n")
        print(result)
        return result

    except Exception as e:
        raise Exception(f"Erro ao executar a crew para o cenário '{nome_cenario}': {e}")


def train():
    """
    Treina a crew usando um cenário específico.
    Uso:
    python main.py train <n_iterations> <filename> <cenario>
    """

    nome_cenario = sys.argv[3] if len(sys.argv) > 3 else CENARIO_PADRAO
    inputs = build_inputs(nome_cenario)

    try:
        CaseEngprocessos().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs=inputs
        )

    except Exception as e:
        raise Exception(f"Erro ao treinar a crew: {e}")


def replay():
    """
    Reexecuta a crew a partir de uma task específica.
    Uso:
    python main.py replay <task_id>
    """

    try:
        CaseEngprocessos().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"Erro ao executar replay da crew: {e}")


def test():
    """
    Testa a execução da crew.
    Uso:
    python main.py test <n_iterations> <eval_llm> <cenario>
    """

    nome_cenario = sys.argv[3] if len(sys.argv) > 3 else CENARIO_PADRAO
    inputs = build_inputs(nome_cenario)

    try:
        CaseEngprocessos().crew().test(
            n_iterations=int(sys.argv[1]),
            eval_llm=sys.argv[2],
            inputs=inputs
        )

    except Exception as e:
        raise Exception(f"Erro ao testar a crew: {e}")


def run_with_trigger():
    """
    Executa a crew recebendo um payload externo.
    Exemplo de payload:
    {"solicitacao": "Descrição livre da solicitação recebida pela área de negócio"}
    """

    if len(sys.argv) < 2:
        raise Exception("Nenhum payload informado. Envie um JSON como argumento.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Payload inválido. Envie um JSON válido.")

    solicitacao = trigger_payload.get("solicitacao", CENARIOS[CENARIO_PADRAO])

    inputs = build_inputs(CENARIO_PADRAO)
    inputs["topic"] = solicitacao
    inputs["cenario"] = "payload_externo"
    inputs["crewai_trigger_payload"] = trigger_payload

    try:
        result = CaseEngprocessos().crew().kickoff(inputs=inputs)
        print("\n\n===== RESULTADO FINAL DA CREW | PAYLOAD EXTERNO =====\n")
        print(result)
        return result

    except Exception as e:
        raise Exception(f"Erro ao executar a crew com trigger: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "train":
        train()
    elif len(sys.argv) > 1 and sys.argv[1] == "replay":
        replay()
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    elif len(sys.argv) > 1 and sys.argv[1] == "trigger":
        run_with_trigger()
    else:
        run()