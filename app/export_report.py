"""Exportación PDF de resumen del expediente."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
from .catalog import SLOTS,ANALYSES

def export_patient_pdf(path,patient,media,analyses):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SmallClinical",parent=styles["BodyText"],fontSize=8,leading=10))
    story=[Paragraph("Expediente odontológico",styles["Title"]),
      Paragraph("Pack Análisis Dentales · Resumen de estudios y registros",styles["Normal"]),Spacer(1,6*mm),
      Paragraph("Datos del paciente",styles["Heading2"])]
    rows=[["Paciente",escape(patient.get("full_name","")),"Expediente",escape(patient.get("record_number",""))],
      ["Nacimiento",escape(patient.get("birth_date") or "No registrado"),"Sexo",escape(patient.get("sex") or "No especificado")],
      ["Teléfono",escape(patient.get("phone") or "—"),"Correo",escape(patient.get("email") or "—")]]
    t=Table(rows,colWidths=[25*mm,64*mm,25*mm,64*mm])
    t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.35,colors.HexColor("#cbd5df")),
      ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#edf2f7")),("BACKGROUND",(2,0),(2,-1),colors.HexColor("#edf2f7")),
      ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8)]))
    story += [t,Spacer(1,5*mm),Paragraph("Estudios cargados",styles["Heading2"])]
    if media:
        data=[["Vista","Archivo original","Fecha"]]
        for m in media:
            slot=SLOTS.get(m["slot_key"]); data.append([slot.label if slot else m["slot_key"],escape(m["filename"]),m["created_at"][:10]])
        tab=Table(data,colWidths=[55*mm,100*mm,24*mm],repeatRows=1)
        tab.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1d3448")),
          ("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.3,colors.HexColor("#cbd5df")),
          ("FONTSIZE",(0,0),(-1,-1),7.5),("VALIGN",(0,0),(-1,-1),"TOP")]))
        story.append(tab)
    else: story.append(Paragraph("No hay estudios cargados.",styles["BodyText"]))
    story += [Spacer(1,5*mm),Paragraph("Análisis registrados",styles["Heading2"])]
    if analyses:
        for key,item in analyses.items():
            story.append(Paragraph(escape(ANALYSES.get(key,key)),styles["Heading3"]))
            story.append(Paragraph("Estado: "+escape(item["status"]),styles["SmallClinical"]))
            for label,value in item.get("values",{}).items():
                if str(value).strip(): story.append(Paragraph(escape(label)+": "+escape(str(value)),styles["SmallClinical"]))
            if item.get("observations"): story.append(Paragraph("Observaciones: "+escape(item["observations"]).replace("\n","<br/>"),styles["SmallClinical"]))
            if item.get("conclusion"): story.append(Paragraph("Conclusión profesional: "+escape(item["conclusion"]).replace("\n","<br/>"),styles["SmallClinical"]))
            story.append(Spacer(1,2*mm))
    else: story.append(Paragraph("Aún no hay análisis registrados.",styles["BodyText"]))
    if patient.get("notes"): story += [Spacer(1,4*mm),Paragraph("Notas",styles["Heading2"]),Paragraph(escape(patient["notes"]),styles["BodyText"])]
    story += [Spacer(1,6*mm),Paragraph("Resumen de datos capturados. Debe ser revisado y validado por el odontólogo responsable; no constituye un diagnóstico autónomo.",styles["SmallClinical"])]
    SimpleDocTemplate(str(path),pagesize=A4,rightMargin=15*mm,leftMargin=15*mm,topMargin=15*mm,bottomMargin=15*mm).build(story)
    return path


def _safe_paragraph(value, style):
    text = escape(str(value)).replace("\n", "<br/>")
    return Paragraph(text if text else "—", style)


def _analysis_display_rows(key, record):
    """Return readable label/value pairs, omitting internal image coordinates."""
    values = record.get("values", {}) or {}
    rows = []
    if key == "steiner":
        results = values.get("Resultados", {}) or {}
        for measure, result in results.items():
            if not isinstance(result, dict):
                continue
            rows.append((
                measure,
                result.get("valor", "—"),
                result.get("norma", "—"),
                result.get("clasificación", "—"),
                result.get("interpretación", "—"),
            ))
        if values.get("Puntos"):
            rows.append(("Puntos anatómicos marcados", len(values["Puntos"]), "", "", ""))
        if values.get("Píxeles por mm"):
            rows.append((
                "Calibración",
                f"{values.get('Distancia de calibración · mm', '—')} mm",
                "",
                "",
                f"{float(values['Píxeles por mm']):.4f} px/mm",
            ))
        return rows, True

    if key == "dental_age":
        for label in (
            "Cuadrante", "Sexo", "Edad cronológica · años", "Edad cronológica · meses",
            "Suma de estadios", "Edad dental estimada · años",
            "Edad dental estimada · años y meses",
            "Diferencia respecto a edad cronológica · meses",
        ):
            if values.get(label) not in (None, ""):
                rows.append((label, values[label]))
        stages = values.get("Estadios por cuadrante", {}) or {}
        selected_quadrant = values.get("Cuadrante")
        tooth_stages = stages.get(selected_quadrant, {}) if selected_quadrant else {}
        if tooth_stages:
            rows.append(("Estadios por órgano dentario", ", ".join(
                f"{tooth}: {stage if stage is not None else 'sin seleccionar'}"
                for tooth, stage in tooth_stages.items()
            )))
        return rows, False

    for label, value in values.items():
        if label in {"Puntos", "Puntos de calibración", "Estadios por cuadrante"}:
            continue
        if value in (None, ""):
            continue
        if isinstance(value, (dict, list, tuple)):
            import json
            value = json.dumps(value, ensure_ascii=False)
        rows.append((label, value))
    return rows, False


def _image_bytes(path):
    """Load a stored image for the PDF, including DICOM where possible."""
    from io import BytesIO
    from PIL import Image as PILImage

    buffer = BytesIO()
    try:
        with PILImage.open(path) as source:
            source.convert("RGB").save(buffer, format="PNG")
    except Exception:
        from .imaging import load_image
        import cv2
        image = load_image(path)
        if image.ndim == 2:
            rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            rgb = cv2.cvtColor(image[:, :, :3], cv2.COLOR_BGR2RGB)
        PILImage.fromarray(rgb).save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def export_academic_report(path, patient, student_name, teacher_email,
                           selected_modules, analyses_snapshot, media):
    """Create a PDF containing only selected modules and completed analysis records."""
    from io import BytesIO
    from datetime import datetime
    from reportlab.platypus import Image as ReportImage, PageBreak, KeepTogether
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.styles import ParagraphStyle
    from .reports import REPORT_MODULES

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not selected_modules:
        raise ValueError("Selecciona al menos un módulo.")
    if not analyses_snapshot:
        raise ValueError("No hay análisis completos para incluir.")

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="YSMSubtitle", parent=styles["Normal"], alignment=TA_CENTER,
        textColor=colors.HexColor("#788A87"), fontSize=9, leading=12,
    ))
    styles.add(ParagraphStyle(
        name="YSMSection", parent=styles["Heading1"],
        textColor=colors.HexColor("#356B72"), spaceBefore=8*mm, spaceAfter=3*mm,
    ))
    styles.add(ParagraphStyle(
        name="YSMBody", parent=styles["BodyText"], fontSize=8.5, leading=11,
        spaceAfter=1.5*mm,
    ))
    styles.add(ParagraphStyle(
        name="YSMCaption", parent=styles["BodyText"], fontSize=7.5, leading=9,
        textColor=colors.HexColor("#788A87"), alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="YSMCell", parent=styles["BodyText"], fontSize=7.2, leading=9,
    ))
    styles.add(ParagraphStyle(
        name="YSMCellBold", parent=styles["BodyText"], fontSize=7.2,
        leading=9, fontName="Helvetica-Bold",
    ))

    story = [
        Spacer(1, 8*mm),
        Paragraph("YSM ANÁLISIS", ParagraphStyle(
            name="YSMTitle", parent=styles["Title"],
            textColor=colors.HexColor("#356B72"), fontSize=25, leading=29,
        )),
        Paragraph("INFORME ACADÉMICO DE ANÁLISIS ORTODÓNCICOS", styles["YSMSubtitle"]),
        Spacer(1, 9*mm),
        Paragraph("Datos del expediente", styles["Heading2"]),
    ]
    patient_rows = [
        ["Paciente", patient.get("full_name") or "No registrado",
         "Expediente", patient.get("record_number") or "—"],
        ["Nacimiento", patient.get("birth_date") or "No registrado",
         "Sexo", patient.get("sex") or "No especificado"],
        ["Estudiante", student_name, "Docente", teacher_email],
        ["Fecha de generación", datetime.now().strftime("%d/%m/%Y %H:%M"),
         "Tipo", "Entrega académica"],
    ]
    info = Table(patient_rows, colWidths=[27*mm, 61*mm, 25*mm, 65*mm])
    info.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#D5DEDA")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E7ECE9")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#E7ECE9")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#273B43")),
        ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor("#273B43")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.7),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([info, Spacer(1, 7*mm), Paragraph("Contenido incluido", styles["Heading2"])])
    for module_id in selected_modules:
        module = REPORT_MODULES.get(module_id)
        if module and analyses_snapshot.get(module_id):
            count = len(analyses_snapshot[module_id])
            story.append(_safe_paragraph(f"{module['title']} · {count} análisis completos", styles["YSMBody"]))

    media_by_slot = {}
    for item in media:
        slot = item.get("slot_key")
        if not slot:
            continue
        current = media_by_slot.get(slot)
        if current is None or item.get("created_at", "") > current.get("created_at", ""):
            media_by_slot[slot] = item

    added_images = set()
    for module_id in selected_modules:
        module = REPORT_MODULES.get(module_id)
        module_analyses = analyses_snapshot.get(module_id, {})
        if not module or not module_analyses:
            continue
        story.append(Paragraph(escape(module["title"]), styles["YSMSection"]))

        for analysis_key, record in module_analyses.items():
            if record.get("status") != "Completo":
                continue
            story.append(Paragraph(
                escape(ANALYSES.get(analysis_key, analysis_key)),
                styles["Heading2"],
            ))
            if record.get("updated_at"):
                story.append(_safe_paragraph(
                    "Registro actualizado: " + str(record["updated_at"])[:10],
                    styles["YSMCaption"],
                ))

            rows, has_ceph_table = _analysis_display_rows(analysis_key, record)
            if rows:
                if has_ceph_table:
                    data = [[
                        Paragraph("Medición", styles["YSMCellBold"]),
                        Paragraph("Valor", styles["YSMCellBold"]),
                        Paragraph("Referencia", styles["YSMCellBold"]),
                        Paragraph("Clasificación", styles["YSMCellBold"]),
                        Paragraph("Interpretación", styles["YSMCellBold"]),
                    ]]
                    for label, value, normal, classification, interpretation in rows:
                        data.append([
                            _safe_paragraph(label, styles["YSMCell"]),
                            _safe_paragraph(value, styles["YSMCell"]),
                            _safe_paragraph(normal, styles["YSMCell"]),
                            _safe_paragraph(classification, styles["YSMCell"]),
                            _safe_paragraph(interpretation, styles["YSMCell"]),
                        ])
                    table = Table(data, colWidths=[27*mm, 19*mm, 23*mm, 27*mm, 82*mm], repeatRows=1)
                else:
                    data = [[
                        Paragraph("Parámetro", styles["YSMCellBold"]),
                        Paragraph("Resultado", styles["YSMCellBold"]),
                    ]]
                    for label, value in rows:
                        data.append([
                            _safe_paragraph(label, styles["YSMCellBold"]),
                            _safe_paragraph(value, styles["YSMCell"]),
                        ])
                    table = Table(data, colWidths=[57*mm, 121*mm], repeatRows=1)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#356B72")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), .3, colors.HexColor("#D5DEDA")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                     [colors.white, colors.HexColor("#F3F4F1")]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.extend([table, Spacer(1, 2*mm)])

            if record.get("observations"):
                story.append(_safe_paragraph(
                    "Observaciones: " + record["observations"], styles["YSMBody"]
                ))
            if record.get("conclusion"):
                story.append(_safe_paragraph(
                    "Conclusión registrada: " + record["conclusion"], styles["YSMBody"]
                ))

        module_slots = module.get("media_slots", ())
        module_images = []
        for slot_key in module_slots:
            item = media_by_slot.get(slot_key)
            if not item:
                continue
            image_path = item.get("current_path") or item.get("original_path")
            if not image_path or image_path in added_images or not Path(image_path).is_file():
                continue
            try:
                buffer = _image_bytes(image_path)
                image = ReportImage(buffer)
                max_width, max_height = 175*mm, 82*mm
                factor = min(max_width / image.imageWidth, max_height / image.imageHeight)
                image.drawWidth = image.imageWidth * factor
                image.drawHeight = image.imageHeight * factor
                module_images.append(KeepTogether([
                    Spacer(1, 2*mm),
                    Paragraph(
                        escape(SLOTS.get(slot_key).label if SLOTS.get(slot_key) else slot_key),
                        styles["YSMCaption"],
                    ),
                    image,
                ]))
                added_images.add(image_path)
            except Exception:
                # The report still contains the analysis data when an image
                # format cannot be rendered; no missing image is fabricated.
                continue
        if module_images:
            story.extend(module_images)

    story.extend([
        Spacer(1, 7*mm),
        Paragraph("Alcance del informe", styles["Heading2"]),
        _safe_paragraph(
            "Este documento reúne exclusivamente los análisis completos seleccionados por el estudiante. "
            "Los resultados y las interpretaciones corresponden a los registros guardados en el expediente. "
            "El informe tiene finalidad académica y requiere revisión y validación del docente responsable; "
            "no constituye por sí solo un diagnóstico ni una indicación terapéutica.",
            styles["YSMBody",
        ),
    ])

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D5DEDA"))
        canvas.line(15*mm, 12*mm, A4[0]-15*mm, 12*mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#788A87"))
        canvas.drawString(15*mm, 8*mm, "YSM Análisis · Informe académico")
        canvas.drawRightString(A4[0]-15*mm, 8*mm, f"Página {doc.page}")
        canvas.restoreState()

    SimpleDocTemplate(
        str(path), pagesize=A4, rightMargin=15*mm, leftMargin=15*mm,
        topMargin=15*mm, bottomMargin=18*mm,
        title="YSM Análisis · Informe académico",
        author=student_name,
    ).build(story, onFirstPage=footer, onLaterPages=footer)
    return path
