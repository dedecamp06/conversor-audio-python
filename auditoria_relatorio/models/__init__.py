from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class TranscriptSegment:
    arquivo: str
    inicio: float
    fim: float
    texto: str


@dataclass
class AudioTranscript:
    arquivo: Path
    idioma: str | None
    duracao_segundos: float
    texto_completo: str
    segmentos: list[TranscriptSegment] = field(default_factory=list)


@dataclass(frozen=True)
class AuditFinding:
    categoria: str
    trecho: str
    origem: str


@dataclass
class AuditAnalysis:
    resumo_executivo: str
    nivel_risco: str
    nao_conformidades: list[AuditFinding]
    evidencias_criticas: list[AuditFinding]
    controles_efetivos: list[AuditFinding]
    recomendacoes: list[str]


def formatar_tempo(segundos: float) -> str:
    total = max(int(segundos), 0)
    horas = total // 3600
    minutos = (total % 3600) // 60
    secs = total % 60
    return f"{horas:02d}:{minutos:02d}:{secs:02d}"
