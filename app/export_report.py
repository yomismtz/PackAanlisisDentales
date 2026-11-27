"""Exportación PDF de resumen del expediente."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
from .catalog import SLOTS,ANALYSES
from .theme import REPORT_PALETTES, report_bird_path

def _report_page_decorator(palette_id="colibri"):
    palette = REPORT_PALETTES.get(palette_id, REPORT_PALETTES["colibri"])["colors"]
    bird_path = report_bird_path(palette_id)
    brand_icon_path = report_bird_path("colibri")

    def draw_page(canvas, doc):
        canvas.saveState()
        if bird_path.is_file():
            try:
                if hasattr(canvas, "setFillAlpha"):
                    canvas.setFillAlpha(0.065)
                canvas.drawImage(str(bird_path), 58*mm, 100*mm, width=92*mm, height=92*mm,
                                 preserveAspectRatio=True, anchor="c", mask="auto")
                if hasattr(canvas, "setFillAlpha"):
                    canvas.setFillAlpha(1)
                canvas.drawImage(str(bird_path), A4[0]-34*mm, A4[1]-29*mm,
                                 width=20*mm, height=20*mm, preserveAspectRatio=True,
                                 anchor="c", mask="auto")
            except Exception:
                pass
        if brand_icon_path.is_file():
            canvas.drawImage(str(brand_icon_path), 15*mm, A4[1]-28*mm, width=19*mm, height=19*mm,
                             preserveAspectRatio=True, mask="auto")
        canvas.setFillColor(colors.HexColor(palette["primary"]))
        canvas.setFont("Helvetica-Bold", 19)
        canvas.drawString(36*mm, A4[1]-19*mm, "AVIS")
        canvas.setFillColor(colors.HexColor(palette["plum"]))
        canvas.setFont("Helvetica-Bold", 6.5)
        canvas.drawString(36*mm, A4[1]-24*mm, "ANÁLISIS ODONTOLÓGICO INTEGRAL")
        canvas.setStrokeColor(colors.HexColor(palette["accent"]))
        canvas.setLineWidth(1.2)
        canvas.line(15*mm, A4[1]-31*mm, A4[0]-15*mm, A4[1]-31*mm)
        canvas.setFillColor(colors.HexColor(palette["muted"]))
        canvas.setFont("Helvetica", 7)
        canvas.setFont("Helvetica-Bold", 6.5)
        canvas.drawString(15*mm, 15*mm, "YomDental · Generado por la Dra. Yomira Salgado Martínez")
        canvas.setFont("Helvetica", 5.8)
        canvas.drawString(15*mm, 9*mm, "Cirujano Dentista · Especialidad en Ortodoncia · Maestría en Ciencias Odontológicas · Doctorado en Educación")
        canvas.setFont("Helvetica", 7)
        canvas.drawRightString(A4[0]-15*mm, 15*mm, f"Página {doc.page}")
        canvas.restoreState()

    return draw_page


def export_patient_pdf(path,patient,media,analyses,palette_id="colibri"):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    palette = REPORT_PALETTES.get(palette_id, REPORT_PALETTES["colibri"])["colors"]
    styles=getSampleStyleSheet()
    styles["Title"].textColor = colors.HexColor(palette["primary"])
    styles["Heading2"].textColor = colors.HexColor(palette["primary"])
    styles["Heading3"].textColor = colors.HexColor(palette["primary"])
    styles.add(ParagraphStyle(name="SmallClinical",parent=styles["BodyText"],fontSize=8,leading=10,textColor=colors.HexColor(palette["text"])))
    story=[Paragraph("Expediente odontológico",styles["Title"]),
      Paragraph("AVIS · Análisis Odontológico Integral · Resumen de estudios y registros",styles["Normal"]),Spacer(1,6*mm),
      Paragraph("Datos del paciente",styles["Heading2"])]
    rows=[["Paciente",escape(patient.get("full_name","")),"Expediente",escape(patient.get("record_number",""))],
      ["Nacimiento",escape(patient.get("birth_date") or "No registrado"),"Sexo",escape(patient.get("sex") or "No especificado")],
      ["Teléfono",escape(patient.get("phone") or "—"),"Correo",escape(patient.get("email") or "—")]]
    t=Table(rows,colWidths=[25*mm,64*mm,25*mm,64*mm])
    t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.35,colors.HexColor(palette["border"])),
      ("BACKGROUND",(0,0),(0,-1),colors.HexColor(palette["soft"])),("BACKGROUND",(2,0),(2,-1),colors.HexColor(palette["soft"])),
      ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8)]))
    story += [t,Spacer(1,5*mm),Paragraph("Estudios cargados",styles["Heading2"])]
    if media:
        data=[["Vista","Archivo original","Fecha"]]
        for m in media:
            slot=SLOTS.get(m["slot_key"]); data.append([slot.label if slot else m["slot_key"],escape(m["filename"]),m["created_at"][:10]])
        tab=Table(data,colWidths=[55*mm,100*mm,24*mm],repeatRows=1)
        tab.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor(palette["primary"])),
          ("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.3,colors.HexColor(palette["border"])),
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
    SimpleDocTemplate(str(path),pagesize=A4,rightMargin=15*mm,leftMargin=15*mm,topMargin=34*mm,bottomMargin=18*mm).build(
        story, onFirstPage=_report_page_decorator(palette_id), onLaterPages=_report_page_decorator(palette_id)
    )
    return path


def _safe_paragraph(value, style):
    text = escape(str(value)).replace("\n", "<br/>")
    return Paragraph(text if text else "—", style)


def _analysis_display_rows(key, record):
    """Return readable label/value pairs, omitting internal image coordinates."""
    values = record.get("values", {}) or {}
    rows = []
    if key == "panoramic_systematic":
        phases = values.get("Fases", {}) or {}
        for phase_key in sorted(phases):
            phase = phases[phase_key] or {}
            phase_title = phase.get("Apartado", f"Fase {phase_key}")
            responses = phase.get("Respuestas", {}) or {}
            for label, value in responses.items():
                if value in (None, ""):
                    continue
                if isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
                    for index, item in enumerate(value, start=1):
                        for sublabel, subvalue in item.items():
                            rows.append((
                                f"{phase_title} · {label} {index} · {sublabel}",
                                subvalue,
                            ))
                elif isinstance(value, (list, tuple, set)):
                    rows.append((f"{phase_title} · {label}", " · ".join(str(item) for item in value)))
                elif isinstance(value, dict):
                    import json
                    rows.append((f"{phase_title} · {label}", json.dumps(value, ensure_ascii=False)))
                else:
                    rows.append((f"{phase_title} · {label}", value))
        legacy = values.get("Registro previo (formato anterior)", {}) or {}
        for label, value in legacy.items():
            if value not in (None, "", [], {}):
                if isinstance(value, (list, tuple, dict)):
                    import json
                    value = json.dumps(value, ensure_ascii=False)
                rows.append((f"Registro previo · {label}", value))
        return rows, False

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

    if key == "nance_carey":
        rows.append(("Método", values.get("Método", "—")))
        rows.append(("Unidad", "Píxeles relativos; no son milímetros"))
        arches = values.get("Arcadas", {}) or {}
        for arch in ("superior", "inferior"):
            data = arches.get(arch, {}) or {}
            rows.append((f"Arcada {arch}", ""))
            calculated = None
            if not data.get("Conclusión automática"):
                from .space_analysis import CAREY_TEETH, calculate_carey_arch
                calculated = calculate_carey_arch(
                    data.get("Puntos", {}) or {},
                    data.get("Recorrido disponible", []) or [],
                    CAREY_TEETH[arch],
                )
            derived = {}
            if calculated:
                derived = {
                    "Cobertura dentaria (%)": calculated["coverage_percent"],
                    "Déficit relativo (%)": calculated["deficit_percent"],
                    "Excedente relativo (%)": calculated["excess_percent"],
                    "Resultado": calculated["classification"],
                    "Conclusión automática": calculated["conclusion"],
                }
            for label, key_name in (
                ("Espacio disponible (px)", "Espacio disponible px"),
                ("Espacio requerido (px)", "Espacio requerido px"),
                ("Discrepancia disponible − requerido (px)", "Discrepancia px"),
                ("Cobertura del material dentario (%)", "Cobertura dentaria (%)"),
                ("Déficit relativo respecto al material dentario (%)", "Déficit relativo (%)"),
                ("Excedente relativo respecto al material dentario (%)", "Excedente relativo (%)"),
                ("Resultado", "Resultado"),
                ("Conclusión automática", "Conclusión automática"),
            ):
                value = data.get(key_name, derived.get(key_name))
                if value not in (None, ""):
                    rows.append((f"{arch.capitalize()} · {label}", value))
                elif label == "Resultado":
                    rows.append((f"{arch.capitalize()} · {label}", "Pendiente"))
        if values.get("Limitación"):
            rows.append(("Alcance", values["Limitación"]))
        legacy = values.get("Registro previo (formato anterior)", {}) or {}
        for label, value in legacy.items():
            if isinstance(value, (dict, list, tuple)):
                import json
                value = json.dumps(value, ensure_ascii=False)
            rows.append((f"Registro previo · {label}", value))
        return rows, False

    if key in ("baume", "intermaxillary"):
        evaluations = values.get("Evaluación estructurada", {}) or {}
        for label, value in evaluations.items():
            if value not in (None, ""):
                rows.append((label, value))
        legacy = values.get("Registro previo (formato anterior)", {}) or {}
        for label, value in legacy.items():
            if isinstance(value, (dict, list, tuple)):
                import json
                value = json.dumps(value, ensure_ascii=False)
            rows.append((f"Registro previo · {label}", value))
        if not rows:
            rows.append(("Registro", "Pendiente"))
        return rows, False

    if key in ("moyers", "tanaka_johnston"):
        results = values.get("Resultado por hemiarcada", {}) or {}
        for label, classification in results.items():
            rows.append((label, classification))
        if not rows:
            rows.append(("Resultado", "Pendiente"))
        return rows, False

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


def _image_bytes(path, cephalometric_points=None):
    """Load a stored image for the PDF and optionally overlay saved cephalometric tracing."""
    from io import BytesIO
    from PIL import Image as PILImage, ImageDraw, ImageFont

    buffer = BytesIO()
    try:
        with PILImage.open(path) as source:
            image = source.convert("RGB")
    except Exception:
        from .imaging import load_image
        import cv2
        raw = load_image(path)
        if raw.ndim == 2:
            rgb = cv2.cvtColor(raw, cv2.COLOR_GRAY2RGB)
        else:
            rgb = cv2.cvtColor(raw[:, :, :3], cv2.COLOR_BGR2RGB)
        image = PILImage.fromarray(rgb)

    if cephalometric_points:
        from .cephalometry import project_to_line
        points = {
            key: (float(value[0]), float(value[1]))
            for key, value in cephalometric_points.items()
            if isinstance(value, (list, tuple)) and len(value) == 2
        }
        calculated = {}
        try:
            if all(key in points for key in ("S", "N", "Pog")):
                calculated["L"] = project_to_line(points["Pog"], points["S"], points["N"])
            if all(key in points for key in ("S", "N", "Co")):
                calculated["E"] = project_to_line(points["Co"], points["S"], points["N"])
        except ValueError:
            calculated = {}
        displayed = {**points, **calculated}
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        pairs = (
            ("S", "N"), ("N", "A"), ("N", "B"), ("N", "D"),
            ("Ar", "Go"), ("Go", "Me"), ("Go", "Gn"), ("A", "B"),
            ("U1_apex", "U1_tip"), ("Pog", "L"), ("Co", "E"),
        )
        for start, end in pairs:
            if start in displayed and end in displayed:
                draw.line(
                    [displayed[start], displayed[end]],
                    fill=(53, 107, 114), width=max(2, round(image.width / 900)),
                )
        radius = max(3, round(image.width / 180))
        for key, (x, y) in displayed.items():
            x, y = int(round(x)), int(round(y))
            draw.ellipse(
                (x-radius, y-radius, x+radius, y+radius),
                fill=(217, 154, 114), outline=(39, 59, 67), width=1,
            )
            draw.text((x+radius+2, y-radius-2), key, fill=(39, 59, 67), font=font)

    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def export_academic_report(path, patient, student_name, teacher_email,
                           selected_modules, analyses_snapshot, media, palette_id="colibri"):
    """Create a PDF containing only selected modules and completed analysis records."""
    from io import BytesIO
    from datetime import datetime
    from reportlab.platypus import Image as ReportImage, PageBreak, KeepTogether
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.styles import ParagraphStyle
    from .reports import REPORT_MODULES

    palette = REPORT_PALETTES.get(palette_id, REPORT_PALETTES["colibri"])["colors"]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not selected_modules:
        raise ValueError("Selecciona al menos un módulo.")
    if not analyses_snapshot:
        raise ValueError("No hay análisis completos para incluir.")

    styles = getSampleStyleSheet()
    styles["Heading2"].textColor = colors.HexColor(palette["primary"])
    styles["Heading3"].textColor = colors.HexColor(palette["primary"])
    styles.add(ParagraphStyle(
        name="YSMSubtitle", parent=styles["Normal"], alignment=TA_CENTER,
        textColor=colors.HexColor(palette["muted"]), fontSize=9, leading=12,
    ))
    styles.add(ParagraphStyle(
        name="YSMSection", parent=styles["Heading1"],
        textColor=colors.HexColor(palette["primary"]), spaceBefore=8*mm, spaceAfter=3*mm,
    ))
    styles.add(ParagraphStyle(
        name="YSMBody", parent=styles["BodyText"], fontSize=8.5, leading=11,
        spaceAfter=1.5*mm,
    ))
    styles.add(ParagraphStyle(
        name="YSMCaption", parent=styles["BodyText"], fontSize=7.5, leading=9,
        textColor=colors.HexColor(palette["muted"]), alignment=TA_CENTER,
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
        Paragraph("INFORME ACADÉMICO", ParagraphStyle(
            name="YSMTitle", parent=styles["Title"],
            textColor=colors.HexColor(palette["primary"]), fontSize=22, leading=26,
        )),
        Paragraph("ANÁLISIS ODONTOLÓGICO INTEGRAL · REGISTRO ACADÉMICO", styles["YSMSubtitle"]),
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
        ("GRID", (0, 0), (-1, -1), .35, colors.HexColor(palette["border"])),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor(palette["soft"])),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor(palette["soft"])),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor(palette["text"])),
        ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor(palette["text"])),
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
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(palette["primary"])),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), .3, colors.HexColor(palette["border"])),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                     [colors.white, colors.HexColor(palette["background"])]),
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
                ceph_points = None
                if module_id == "ceph" and slot_key == "ceph_lateral":
                    ceph_record = module_analyses.get("steiner", {})
                    ceph_points = (ceph_record.get("values", {}) or {}).get("Puntos")
                buffer = _image_bytes(image_path, cephalometric_points=ceph_points)
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
            styles["YSMBody"],
        ),
    ])

    SimpleDocTemplate(
        str(path), pagesize=A4, rightMargin=15*mm, leftMargin=15*mm,
        topMargin=34*mm, bottomMargin=18*mm,
        title="AVIS · Informe académico",
        author=student_name,
    ).build(story, onFirstPage=_report_page_decorator(palette_id), onLaterPages=_report_page_decorator(palette_id))
    return path
