from __future__ import annotations

from flask import render_template_string

from ..services.transcription_service import SUPPORTED_AUDIO_EXTENSIONS

HTML = """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Conversor Audio</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, Helvetica, sans-serif; }
    body { background: #f7f7fb; color: #1f2937; }
    header {
      width: 100%;
      height: 80px;
      background: #fff;
      border-bottom: 1px solid #e5e7eb;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 60px;
    }
    .logo { display: flex; align-items: center; gap: 12px; }
    .logo-icon {
      width: 42px;
      height: 42px;
      border-radius: 12px;
      background: #111827;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 20px;
      font-weight: 700;
    }
    .logo h1 { font-size: 22px; font-weight: 700; }
    .top-nav { display: flex; align-items: center; gap: 10px; }
    .nav-link {
      text-decoration: none;
      color: #111827;
      padding: 10px 16px;
      border: 1px solid #d1d5db;
      border-radius: 12px;
      font-size: 14px;
      font-weight: 600;
      background: #fff;
    }
    .nav-link.active { background: #4f5fff; color: #fff; border-color: #4f5fff; }
    .main-container {
      width: 100%;
      min-height: calc(100vh - 80px);
      display: flex;
      justify-content: center;
      padding: 50px 20px;
    }
    .upload-card {
      width: 100%;
      max-width: 980px;
      background: #fff;
      border-radius: 24px;
      padding: 40px;
      box-shadow: 0 5px 20px rgba(0, 0, 0, .05);
    }
    .alert {
      margin-bottom: 16px;
      border-radius: 12px;
      padding: 10px 12px;
      font-size: 14px;
    }
    .alert-error { background: #fee2e2; border: 1px solid #fca5a5; color: #991b1b; }
    .alert-ok { background: #dcfce7; border: 1px solid #86efac; color: #166534; }
    .alert-ok a { margin-left: 8px; color: #166534; font-weight: 700; }
    .steps {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 16px;
      margin-bottom: 30px;
      flex-wrap: wrap;
    }
    .step { display: flex; align-items: center; gap: 12px; }
    .step-number {
      width: 42px;
      height: 42px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 18px;
    }
    .active { background: #4f5fff; color: #fff; }
    .inactive { background: #e5e7eb; color: #6b7280; }
    .step-text { font-size: 16px; font-weight: 500; }
    .step-disabled { color: #9ca3af; }
    .arrow { color: #9ca3af; font-size: 22px; }
    .upload-area {
      border: 2px dashed #d1d5db;
      border-radius: 24px;
      padding: 45px 20px;
      text-align: center;
      transition: .3s;
    }
    .upload-area.dragover { border-color: #4f5fff; background: #f5f7ff; }
    .upload-icons { display: flex; justify-content: center; gap: 12px; margin-bottom: 20px; }
    .upload-icon {
      width: 64px;
      height: 64px;
      border-radius: 18px;
      background: #f4f6ff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28px;
    }
    .upload-text { font-size: 28px; margin-bottom: 14px; color: #374151; }
    .divider {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 16px;
      margin: 18px 0;
      color: #9ca3af;
    }
    .divider::before,
    .divider::after {
      content: "";
      width: 100px;
      height: 1px;
      background: #d1d5db;
    }
    .file-input { display: none; }
    .file-label {
      display: inline-block;
      padding: 16px 32px;
      border-radius: 16px;
      border: 1px solid #d1d5db;
      background: #fff;
      font-size: 20px;
      cursor: pointer;
      transition: .3s;
    }
    .file-label:hover { background: #f9fafb; }
    .formats { margin-top: 16px; color: #6b7280; font-size: 14px; }
    .file-preview {
      background: #f9fafb;
      border: 1px solid #e5e7eb;
      border-radius: 14px;
      padding: 16px;
      text-align: left;
      max-width: 620px;
      margin: 0 auto;
    }
    .file-preview-title { font-weight: 700; margin-bottom: 8px; }
    .file-row {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 6px 0;
      font-size: 14px;
      border-bottom: 1px solid #e5e7eb;
    }
    .file-row:last-child { border-bottom: 0; }
    .hidden { display: none; }
    .fields-grid {
      margin-top: 22px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }
    .field { display: flex; flex-direction: column; gap: 6px; }
    .field.full { grid-column: 1 / -1; }
    .field label { font-size: 14px; font-weight: 600; }
    .field input,
    .field select {
      width: 100%;
      border: 1px solid #d1d5db;
      border-radius: 10px;
      padding: 11px 12px;
      background: #fff;
    }
    .check {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      font-weight: 600;
    }
    .check input { width: auto; }
    .bottom-button { display: flex; justify-content: center; margin-top: 24px; }
    .big-button {
      width: 380px;
      height: 64px;
      border: 0;
      border-radius: 18px;
      background: #4f5fff;
      color: #fff;
      font-size: 24px;
      font-weight: 700;
      cursor: pointer;
      transition: .3s;
    }
    .big-button:hover { opacity: .9; }
    .pdf-header { margin-bottom: 14px; }
    .pdf-header h2 { font-size: 24px; }
    .table-wrap { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; border-bottom: 1px solid #e5e7eb; padding: 10px; }
    th { background: #f9fafb; }
    @media (max-width: 900px) {
      header { padding: 20px; flex-direction: column; gap: 12px; height: auto; }
      .upload-card { padding: 24px 16px; }
      .upload-text { font-size: 22px; }
      .fields-grid { grid-template-columns: 1fr; }
      .big-button { width: 100%; font-size: 20px; }
    }
  </style>
</head>
<body>
  <header>
    <div class="logo">
      <div class="logo-icon">🎵</div>
      <h1>Conversor Audio</h1>
    </div>
    <nav class="top-nav">
      <a class="nav-link {% if aba == 'gerar' %}active{% endif %}" href="{{ url_for('home_get', aba='gerar') }}">Conversor</a>
      <a class="nav-link {% if aba == 'pdfs' %}active{% endif %}" href="{{ url_for('home_get', aba='pdfs') }}">PDFs gerados</a>
    </nav>
  </header>

  <main class="main-container">
    <div class="upload-card">
      {% if erro %}<div class="alert alert-error">{{ erro }}</div>{% endif %}
      {% if sucesso %}
        <div class="alert alert-ok">
          {{ sucesso }}
          {% if arquivo_gerado %}
            <a href="{{ url_for('baixar_pdf', nome_arquivo=arquivo_gerado) }}">Baixar agora</a>
          {% endif %}
        </div>
      {% endif %}

      {% if aba == "gerar" %}
        <div class="steps">
          <div class="step">
            <div class="step-number active" id="step1">1</div>
            <div class="step-text" id="textStep1">Enviar áudio</div>
          </div>
          <div class="arrow">→</div>
          <div class="step">
            <div class="step-number inactive" id="step2">2</div>
            <div class="step-text step-disabled" id="textStep2">Transcrever e resumir</div>
          </div>
          <div class="arrow">→</div>
          <div class="step">
            <div class="step-number inactive">3</div>
            <div class="step-text step-disabled">Concluir</div>
          </div>
        </div>

        <form method="post" enctype="multipart/form-data" id="converterForm">
          <div class="upload-area" id="uploadArea">
            <div id="uploadContent">
              <div class="upload-icons" id="uploadIcons">
                <div class="upload-icon">🎵</div>
              </div>
              <div class="upload-text" id="uploadText">Arraste e solte aqui</div>
              <div class="divider" id="uploadDivider">ou</div>
              <label class="file-label" for="fileInput">Escolher arquivo(s)</label>
              <input id="fileInput" type="file" name="audios" class="file-input" multiple required>
              <div class="formats">Formatos suportados: {{ formatos }}</div>
              <div class="file-preview hidden" id="filePreview">
                <div class="file-preview-title" id="filePreviewTitle"></div>
                <div id="filePreviewRows"></div>
              </div>
            </div>
          </div>

          <div class="fields-grid">
            <div class="field">
              <label for="empresa">Empresa</label>
              <input id="empresa" name="empresa" value="{{ form.empresa }}">
            </div>
            <div class="field">
              <label for="operacao">Operação</label>
              <input id="operacao" name="operacao" value="{{ form.operacao }}" required>
            </div>
            <div class="field">
              <label for="auditor">Auditor</label>
              <input id="auditor" name="auditor" value="{{ form.auditor }}">
            </div>
            <div class="field">
              <label for="data_auditoria">Data da auditoria</label>
              <input id="data_auditoria" name="data_auditoria" value="{{ form.data_auditoria }}" placeholder="DD/MM/AAAA">
            </div>
            <div class="field">
              <label for="idioma">Idioma</label>
              <input id="idioma" name="idioma" value="{{ form.idioma }}" placeholder="pt">
            </div>
            <div class="field">
              <label for="model">Modelo Whisper</label>
              <select id="model" name="model">
                {% for m in ["tiny", "base", "small", "medium", "large-v3"] %}
                  <option value="{{ m }}" {% if form.model == m %}selected{% endif %}>{{ m }}</option>
                {% endfor %}
              </select>
            </div>
            <div class="field">
              <label for="device">Dispositivo</label>
              <select id="device" name="device">
                {% for d in ["cpu", "cuda", "auto"] %}
                  <option value="{{ d }}" {% if form.device == d %}selected{% endif %}>{{ d }}</option>
                {% endfor %}
              </select>
            </div>
            <div class="field">
              <label for="compute_type">Compute type</label>
              <select id="compute_type" name="compute_type">
                {% for c in ["int8", "int8_float16", "float16", "float32"] %}
                  <option value="{{ c }}" {% if form.compute_type == c %}selected{% endif %}>{{ c }}</option>
                {% endfor %}
              </select>
            </div>
            <div class="field full">
              <label class="check">
                <input type="checkbox" name="incluir_transcricao" {% if form.incluir_transcricao %}checked{% endif %}>
                Incluir transcrição detalhada no PDF
              </label>
            </div>
          </div>

          <div class="bottom-button">
            <button type="submit" class="big-button">Transcrever →</button>
          </div>
        </form>
      {% endif %}

      {% if aba == "pdfs" %}
        <div class="pdf-header">
          <h2>PDFs gerados</h2>
        </div>
        <div class="table-wrap">
          {% if pdfs %}
            <table>
              <thead>
                <tr>
                  <th>Arquivo</th>
                  <th>Gerado em</th>
                  <th>Tamanho</th>
                  <th>Ação</th>
                </tr>
              </thead>
              <tbody>
                {% for pdf in pdfs %}
                  <tr>
                    <td>{{ pdf.nome }}</td>
                    <td>{{ pdf.modificado_em }}</td>
                    <td>{{ pdf.tamanho }}</td>
                    <td><a href="{{ url_for('baixar_pdf', nome_arquivo=pdf.nome) }}">Baixar</a></td>
                  </tr>
                {% endfor %}
              </tbody>
            </table>
          {% else %}
            <p>Nenhum PDF gerado ainda.</p>
          {% endif %}
        </div>
      {% endif %}
    </div>
  </main>

  <script>
    (() => {
      const uploadArea = document.getElementById("uploadArea");
      const fileInput = document.getElementById("fileInput");
      const uploadContent = document.getElementById("uploadContent");
      const uploadIcons = document.getElementById("uploadIcons");
      const uploadText = document.getElementById("uploadText");
      const uploadDivider = document.getElementById("uploadDivider");
      const filePreview = document.getElementById("filePreview");
      const filePreviewTitle = document.getElementById("filePreviewTitle");
      const filePreviewRows = document.getElementById("filePreviewRows");
      const converterForm = document.getElementById("converterForm");
      const step1 = document.getElementById("step1");
      const step2 = document.getElementById("step2");
      const textStep1 = document.getElementById("textStep1");
      const textStep2 = document.getElementById("textStep2");

      if (
        !uploadArea
        || !fileInput
        || !uploadContent
        || !uploadIcons
        || !uploadText
        || !uploadDivider
        || !filePreview
        || !filePreviewTitle
        || !filePreviewRows
        || !converterForm
      ) {
        return;
      }

      const escapeHtml = (text) => text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");

      const renderFiles = (files) => {
        if (!files || files.length === 0) {
          uploadIcons.classList.remove("hidden");
          uploadText.classList.remove("hidden");
          uploadDivider.classList.remove("hidden");
          filePreview.classList.add("hidden");
          filePreviewTitle.textContent = "";
          filePreviewRows.innerHTML = "";
          return;
        }

        const linhas = Array.from(files).map((file) => {
          const tamanhoMb = (file.size / 1024 / 1024).toFixed(2);
          return `<div class="file-row"><span>${escapeHtml(file.name)}</span><span>${tamanhoMb} MB</span></div>`;
        }).join("");

        uploadIcons.classList.add("hidden");
        uploadText.classList.add("hidden");
        uploadDivider.classList.add("hidden");
        filePreview.classList.remove("hidden");
        filePreviewTitle.textContent = `${files.length} arquivo(s) selecionado(s)`;
        filePreviewRows.innerHTML = linhas;
      };

      fileInput.addEventListener("change", () => {
        renderFiles(fileInput.files);
      });

      uploadArea.addEventListener("dragover", (event) => {
        event.preventDefault();
        uploadArea.classList.add("dragover");
      });

      uploadArea.addEventListener("dragleave", () => {
        uploadArea.classList.remove("dragover");
      });

      uploadArea.addEventListener("drop", (event) => {
        event.preventDefault();
        uploadArea.classList.remove("dragover");
        if (!event.dataTransfer || !event.dataTransfer.files || event.dataTransfer.files.length === 0) {
          return;
        }
        fileInput.files = event.dataTransfer.files;
        renderFiles(fileInput.files);
      });

      converterForm.addEventListener("submit", (event) => {
        if (!fileInput.files || fileInput.files.length === 0) {
          event.preventDefault();
          return;
        }

        if (step1 && step2 && textStep1 && textStep2) {
          step1.classList.remove("active");
          step1.classList.add("inactive");
          step2.classList.remove("inactive");
          step2.classList.add("active");
          textStep1.classList.add("step-disabled");
          textStep2.classList.remove("step-disabled");
        }
      });
    })();
  </script>
</body>
</html>
"""


def render_home(
    form_data: dict[str, str | bool],
    pdfs: list[dict[str, str]],
    aba: str = "gerar",
    erro: str = "",
    sucesso: str = "",
    arquivo_gerado: str = "",
) -> str:
    formatos = ", ".join(sorted(SUPPORTED_AUDIO_EXTENSIONS))
    return render_template_string(
        HTML,
        formatos=formatos,
        form=form_data,
        erro=erro,
        sucesso=sucesso,
        arquivo_gerado=arquivo_gerado,
        aba=aba,
        pdfs=pdfs,
    )
