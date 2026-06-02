from __future__ import annotations

import unicodedata

from ..models import AudioTranscript, AuditAnalysis, AuditFinding, formatar_tempo

CATEGORIAS = {
    "nao_conformidades": [
        "não conform",
        "desvio",
        "falha",
        "erro",
        "incidente",
        "parada",
        "atraso",
        "não cumpr",
        "descumpr",
    ],
    "evidencias_criticas": [
        "risco",
        "impacto",
        "perda",
        "multa",
        "fraude",
        "acidente",
        "retrabalho",
        "interrupção",
    ],
    "controles_efetivos": [
        "conforme",
        "controle",
        "checklist",
        "aprovado",
        "monitoramento",
        "rastreabilidade",
        "padronizado",
        "procedimento seguido",
    ],
}


def _normalizar(texto: str) -> str:
    sem_acentos = "".join(
        c
        for c in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(c) != "Mn"
    )
    return sem_acentos


def _conta_por_categoria(
    transcricoes: list[AudioTranscript], categoria: str
) -> list[AuditFinding]:
    palavras_chave = [_normalizar(p) for p in CATEGORIAS[categoria]]
    achados: list[AuditFinding] = []
    vistos: set[tuple[str, str]] = set()

    for transcricao in transcricoes:
        for seg in transcricao.segmentos:
            norm = _normalizar(seg.texto)
            if any(chave in norm for chave in palavras_chave):
                origem = (
                    f"{seg.arquivo} "
                    f"[{formatar_tempo(seg.inicio)} - {formatar_tempo(seg.fim)}]"
                )
                dedupe_key = (origem, seg.texto)
                if dedupe_key in vistos:
                    continue
                vistos.add(dedupe_key)
                achados.append(
                    AuditFinding(
                        categoria=categoria,
                        trecho=seg.texto,
                        origem=origem,
                    )
                )
    return achados[:12]


def _nivel_risco(
    nao_conformidades: list[AuditFinding],
    evidencias_criticas: list[AuditFinding],
    controles_efetivos: list[AuditFinding],
) -> str:
    score = (len(nao_conformidades) * 2) + len(evidencias_criticas) - len(
        controles_efetivos
    )
    if score >= 12:
        return "ALTO"
    if score >= 6:
        return "MÉDIO"
    return "BAIXO"


def _recomendacoes(
    nao_conformidades: list[AuditFinding],
    evidencias_criticas: list[AuditFinding],
    controles_efetivos: list[AuditFinding],
) -> list[str]:
    recomendacoes: list[str] = []
    if nao_conformidades:
        recomendacoes.append(
            "Criar plano de ação com responsáveis e prazo para tratar não conformidades."
        )
    if evidencias_criticas:
        recomendacoes.append(
            "Priorizar matriz de risco operacional para os pontos com maior impacto."
        )
    if len(controles_efetivos) < 2:
        recomendacoes.append(
            "Reforçar evidências de execução de controles (checklists e aprovações)."
        )
    if not recomendacoes:
        recomendacoes.append(
            "Manter a rotina atual de monitoramento e revisar indicadores periodicamente."
        )
    return recomendacoes


def analisar_transcricoes(transcricoes: list[AudioTranscript]) -> AuditAnalysis:
    if not transcricoes:
        raise ValueError("Nenhuma transcrição foi gerada.")

    nao_conformidades = _conta_por_categoria(transcricoes, "nao_conformidades")
    evidencias_criticas = _conta_por_categoria(transcricoes, "evidencias_criticas")
    controles_efetivos = _conta_por_categoria(transcricoes, "controles_efetivos")

    nivel = _nivel_risco(nao_conformidades, evidencias_criticas, controles_efetivos)
    total_segmentos = sum(len(t.segmentos) for t in transcricoes)
    total_palavras = sum(len(t.texto_completo.split()) for t in transcricoes)

    resumo = (
        f"Foram avaliados {len(transcricoes)} áudio(s), totalizando {total_segmentos} "
        f"segmentos e aproximadamente {total_palavras} palavras transcritas. "
        f"Identificadas {len(nao_conformidades)} não conformidades, "
        f"{len(evidencias_criticas)} evidências críticas e "
        f"{len(controles_efetivos)} sinais de controles efetivos. "
        f"Nível de risco operacional estimado: {nivel}."
    )

    return AuditAnalysis(
        resumo_executivo=resumo,
        nivel_risco=nivel,
        nao_conformidades=nao_conformidades,
        evidencias_criticas=evidencias_criticas,
        controles_efetivos=controles_efetivos,
        recomendacoes=_recomendacoes(
            nao_conformidades,
            evidencias_criticas,
            controles_efetivos,
        ),
    )
