import json
from datetime import datetime
from typing import Type, List, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class BacklogPayloadInput(BaseModel):
    solicitacao_original: str = Field(..., description="Texto original da solicitação recebida.")
    resumo_executivo: str = Field(..., description="Resumo executivo da análise.")
    processo_impactado: str = Field(..., description="Processo operacional impactado.")
    criticidade: str = Field(..., description="Nível de criticidade: Baixa, Média, Alta ou Crítica.")
    score_criticidade: float = Field(..., description="Score de criticidade de 1 a 10.")
    impacto_operacional: str = Field(..., description="Descrição do impacto operacional.")
    gargalos: List[str] = Field(default_factory=list, description="Lista de gargalos identificados.")
    causas_raiz: List[str] = Field(default_factory=list, description="Lista de causas-raiz ou hipóteses.")
    abordagem_recomendada: str = Field(..., description="Abordagem recomendada pela Engenharia de Processos.")
    proximos_passos: List[str] = Field(default_factory=list, description="Próximos passos sugeridos.")
    encaminhamento: str = Field(..., description="Destino recomendado: backlog, quick win, projeto, squad etc.")


class GeradorJSONBacklogTool(BaseTool):
    name: str = "Gerador JSON de Integração com Backlog"
    description: str = (
        "Gera um payload JSON estruturado para integração via API com sistema de backlog "
        "da área de Engenharia de Processos do banco."
    )
    args_schema: Type[BaseModel] = BacklogPayloadInput

    def _run(
        self,
        solicitacao_original: str,
        resumo_executivo: str,
        processo_impactado: str,
        criticidade: str,
        score_criticidade: float,
        impacto_operacional: str,
        gargalos: Optional[List[str]] = None,
        causas_raiz: Optional[List[str]] = None,
        abordagem_recomendada: str = "",
        proximos_passos: Optional[List[str]] = None,
        encaminhamento: str = ""
    ) -> str:
        payload = {
            "id_externo": f"PROC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "data_criacao": datetime.now().isoformat(),
            "origem": "crew_ai_streamlit",
            "tipo_registro": "demanda_engenharia_processos",

            "solicitacao": {
                "texto_original": solicitacao_original,
                "resumo_executivo": resumo_executivo,
                "processo_impactado": processo_impactado
            },

            "classificacao": {
                "criticidade": criticidade,
                "score_criticidade": score_criticidade
            },

            "diagnostico": {
                "impacto_operacional": impacto_operacional,
                "gargalos_identificados": gargalos or [],
                "causas_raiz_hipoteticas": causas_raiz or []
            },

            "recomendacao": {
                "abordagem_recomendada": abordagem_recomendada,
                "proximos_passos": proximos_passos or [],
                "encaminhamento": encaminhamento
            },

            "governanca": {
                "status_integracao": "pronto_para_envio",
                "sistema_destino": "backlog_engenharia_processos",
                "versao_payload": "1.0"
            }
        }

        return json.dumps(payload, ensure_ascii=False, indent=2)