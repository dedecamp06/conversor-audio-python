from __future__ import annotations

from pathlib import Path

from flask import Flask, Response, redirect, request, send_from_directory, url_for

from ..services.web_service import (
    form_defaults,
    generate_report_from_uploads,
    list_pdfs,
    reports_dir,
)
from ..views.web_view import render_home


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def home_get() -> str:
        aba = request.args.get("aba", "gerar")
        if aba not in {"gerar", "pdfs"}:
            aba = "gerar"
        return render_home(
            form_data=form_defaults(),
            pdfs=list_pdfs(),
            aba=aba,
            sucesso=request.args.get("sucesso", ""),
            arquivo_gerado=request.args.get("arquivo", ""),
        )

    @app.post("/")
    def home_post() -> Response | str:
        form = form_defaults()
        form.update(
            {
                "empresa": request.form.get("empresa", form["empresa"]),
                "operacao": request.form.get("operacao", ""),
                "auditor": request.form.get("auditor", form["auditor"]),
                "data_auditoria": request.form.get(
                    "data_auditoria", form["data_auditoria"]
                ),
                "idioma": request.form.get("idioma", form["idioma"]),
                "model": request.form.get("model", form["model"]),
                "device": request.form.get("device", form["device"]),
                "compute_type": request.form.get("compute_type", form["compute_type"]),
                "incluir_transcricao": request.form.get("incluir_transcricao") == "on",
            }
        )

        arquivos = request.files.getlist("audios")
        if not arquivos or all(not a.filename for a in arquivos):
            return render_home(
                form_data=form,
                pdfs=list_pdfs(),
                aba="gerar",
                erro="Selecione ao menos um arquivo de áudio.",
            )

        if not str(form["operacao"]).strip():
            return render_home(
                form_data=form,
                pdfs=list_pdfs(),
                aba="gerar",
                erro="O campo Operação é obrigatório.",
            )

        try:
            file_name = generate_report_from_uploads(arquivos, form)
            return redirect(
                url_for(
                    "home_get",
                    aba="pdfs",
                    sucesso="Relatório gerado com sucesso.",
                    arquivo=file_name,
                )
            )
        except (FileNotFoundError, PermissionError, RuntimeError, ValueError, OSError) as exc:
            return render_home(
                form_data=form,
                pdfs=list_pdfs(),
                aba="gerar",
                erro=f"Erro ao gerar relatório: {exc}",
            )

    @app.get("/pdfs")
    def pdfs_get() -> Response:
        return redirect(url_for("home_get", aba="pdfs"))

    @app.get("/pdfs/<path:nome_arquivo>")
    def baixar_pdf(nome_arquivo: str) -> Response:
        safe_name = Path(nome_arquivo).name
        pasta_pdfs = reports_dir()
        arquivo = pasta_pdfs / safe_name
        if not arquivo.exists():
            return Response(
                "PDF não encontrado.",
                status=404,
                mimetype="text/plain; charset=utf-8",
            )
        return send_from_directory(
            pasta_pdfs,
            safe_name,
            as_attachment=True,
            download_name=safe_name,
        )

    return app
