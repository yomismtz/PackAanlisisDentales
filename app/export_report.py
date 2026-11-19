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
    t=Table(rows,colWidths=[25*mm,66*mm,25*mm,68*mm])
    t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.35,colors.HexColor("#cbd5df")),
      ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#edf2f7")),("BACKGROUND",(2,0),(2,-1),colors.HexColor("#edf2f7")),
      ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8)]))
    story += [t,Spacer(1,5*mm),Paragraph("Estudios cargados",styles["Heading2"])]
    if media:
        data=[["Vista","Archivo original","Fecha"]]
        for m in media:
            slot=SLOTS.get(m["slot_key"]); data.append([slot.label if slot else m["slot_key"],escape(m["filename"]),m["created_at"][:10]])
        tab=Table(data,colWidths=[60*mm,100*mm,24*mm],repeatRows=1)
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
