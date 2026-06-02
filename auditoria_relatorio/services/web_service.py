from __future__ import annotations

import datetime as dt
import tempfile
from pathlib import Path

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .analysis_service import analisar_transcricoes
from .report_service import gerar_relatorio_pdf
from .transcription_service import AudioTranscriber, encontrar_audios

BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = BASE_DIR / "pdfs_gerados"


def reports_dir() -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return REPORTS_DIR


def form_defaults() -> dict[str, str | bool]:
    return {
        "empresa": "Não informado",
        "operacao": "",
        "auditor": "Não informado",
        "data_auditoria": dt.date.today().strftime("%d/%m/%Y"),
        "idioma": "pt",
        "model": "tiny",
        "device": "cpu",
        "compute_type": "int8",
        "incluir_transcricao": True,
    }


def list_pdfs() -> list[dict[str, str]]:
    lista: list[dict[str, str]] = []
    for arquivo in sorted(
        reports_dir().glob("*.pdf"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    ):
        stat = arquivo.stat()
        lista.append(
            {
                "nome": arquivo.name,
                "modificado_em": dt.datetime.fromtimestamp(stat.st_mtime).strftime(
                    "%d/%m/%Y %H:%M"
                ),
                "tamanho": f"{(stat.st_size / 1024):.1f} KB",
            }
        )
    return lista


def _metadata(
    empresa: str,
    operacao: str,
    auditor: str,
    data_auditoria: str,
    total_audios: int,
) -> dict[str, str]:
    return {
        "Empresa": empresa,
        "Operação": operacao,
        "Auditor": auditor,
        "Data da auditoria": data_auditoria,
        "Data de emissão": dt.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Total de áudios": str(total_audios),
    }


def generate_report_from_uploads(
    uploads: list[FileStorage],
    form: dict[str, str | bool],
) -> str:
    with tempfile.TemporaryDirectory(prefix="auditoria_web_") as tmp:
        tmp_dir = Path(tmp)
        audio_dir = tmp_dir / "audios"
        audio_dir.mkdir(parents=True, exist_ok=True)

        saved = 0
        for index, upload in enumerate(uploads, start=1):
            if not upload.filename:
                continue
            original_name = Path(upload.filename).name
            safe_name = secure_filename(original_name) or f"audio_{index}.wav"
            destino = audio_dir / safe_name
            upload.save(destino)
            saved += 1

        if saved == 0:
            raise ValueError("Nenhum arquivo válido foi enviado.")

        audio_files = encontrar_audios(audio_dir)
        transcriber = AudioTranscriber(
            model_name=str(form["model"]),
            device=str(form["device"]),
            compute_type=str(form["compute_type"]),
        )
        idioma = str(form["idioma"]).strip() or None
        transcricoes = transcriber.transcrever_varios(audio_files, idioma=idioma)
        analise = analisar_transcricoes(transcricoes)

        file_name = (
            "relatorio_auditoria_" + dt.datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".pdf"
        )
        output_pdf = reports_dir() / file_name
        gerar_relatorio_pdf(
            output_path=output_pdf,
            metadados=_metadata(
                empresa=str(form["empresa"]),
                operacao=str(form["operacao"]),
                auditor=str(form["auditor"]),
                data_auditoria=str(form["data_auditoria"]),
                total_audios=len(audio_files),
            ),
            transcricoes=transcricoes,
            analise=analise,
            anexar_transcricao=bool(form["incluir_transcricao"]),
        )

    return file_name
