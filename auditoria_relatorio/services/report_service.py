from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..models import AudioTranscript, AuditAnalysis, AuditFinding, formatar_tempo


def _styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TituloRelatorio",
            parent=styles["Title"],
            fontSize=20,
            leading=24,
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Secao",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            spaceBefore=12,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Corpo",
            parent=styles["BodyText"],
            fontSize=10,
            leading=14,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CorpoPequeno",
            parent=styles["BodyText"],
            fontSize=8,
            leading=11,
            spaceAfter=3,
        )
    )
    return styles


def _tabela_metadados(metadados: dict[str, str]):
    dados = [["Campo", "Valor"]]
    for campo, valor in metadados.items():
        dados.append([campo, valor])

    tabela = Table(dados, colWidths=[5.2 * cm, 11.8 * cm], repeatRows=1)
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b5394")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ]
        )
    )
    return tabela


def _renderiza_achados(achados: list[AuditFinding], vazio_msg: str, styles) -> list[Paragraph]:
    if not achados:
        return [Paragraph(vazio_msg, styles["Corpo"])]
    linhas: list[Paragraph] = []
    for item in achados:
        texto = f"• <b>{escape(item.origem)}</b>: {escape(item.trecho)}"
        linhas.append(Paragraph(texto, styles["Corpo"]))
    return linhas


def gerar_relatorio_pdf(
    output_path: Path,
    metadados: dict[str, str],
    transcricoes: list[AudioTranscript],
    analise: AuditAnalysis,
    anexar_transcricao: bool = True,
) -> None:
    styles = _styles()
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="Relatório de Auditoria Operacional",
        author=metadados.get("Auditor", ""),
    )

    elementos = [
        Paragraph("Relatório de Auditoria Operacional", styles["TituloRelatorio"]),
        _tabela_metadados(metadados),
        Spacer(1, 10),
        Paragraph("Resumo Executivo", styles["Secao"]),
        Paragraph(escape(analise.resumo_executivo), styles["Corpo"]),
        Paragraph(f"<b>Nível de risco consolidado:</b> {analise.nivel_risco}", styles["Corpo"]),
        Paragraph("Não Conformidades", styles["Secao"]),
    ]
    elementos.extend(
        _renderiza_achados(
            analise.nao_conformidades,
            "Nenhuma não conformidade foi detectada com base nos termos monitorados.",
            styles,
        )
    )

    elementos.append(Paragraph("Evidências Críticas", styles["Secao"]))
    elementos.extend(
        _renderiza_achados(
            analise.evidencias_criticas,
            "Nenhuma evidência crítica foi detectada com base nos termos monitorados.",
            styles,
        )
    )

    elementos.append(Paragraph("Controles Efetivos", styles["Secao"]))
    elementos.extend(
        _renderiza_achados(
            analise.controles_efetivos,
            "Não houve menções suficientes de controles efetivos na amostra analisada.",
            styles,
        )
    )

    elementos.append(Paragraph("Recomendações", styles["Secao"]))
    for recomendacao in analise.recomendacoes:
        elementos.append(Paragraph(f"• {escape(recomendacao)}", styles["Corpo"]))

    if anexar_transcricao:
        elementos.extend([PageBreak(), Paragraph("Anexo - Transcrição Consolidada", styles["Secao"])])
        for transcricao in transcricoes:
            elementos.append(
                Paragraph(
                    f"<b>Arquivo:</b> {escape(transcricao.arquivo.name)}",
                    styles["Corpo"],
                )
            )
            elementos.append(
                Paragraph(
                    f"<b>Idioma:</b> {escape(transcricao.idioma or 'não identificado')} | "
                    f"<b>Duração:</b> {formatar_tempo(transcricao.duracao_segundos)}",
                    styles["Corpo"],
                )
            )
            if transcricao.segmentos:
                for seg in transcricao.segmentos:
                    linha = (
                        f"[{formatar_tempo(seg.inicio)} - {formatar_tempo(seg.fim)}] "
                        f"{escape(seg.texto)}"
                    )
                    elementos.append(Paragraph(linha, styles["CorpoPequeno"]))
            else:
                elementos.append(Paragraph("Sem segmentos reconhecidos.", styles["Corpo"]))
            elementos.append(Spacer(1, 8))

    doc.build(elementos)
