#!/usr/bin/env python3
"""Generate DOCX note on Maharashtra GRs for tribal-to-tribal land transfer under MLRC."""

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def set_cell_shading(cell, color="D9E2F3"):
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), color)
    cell._tc.get_or_add_tcPr().append(shading)


def add_table(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    hdr_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        hdr_cells[i].text = header
        set_cell_shading(hdr_cells[i], "1F4E79")
        for p in hdr_cells[i].paragraphs:
            for run in p.runs:
                run.bold = True
                run.font.color.rgb = None
    for r_idx, row in enumerate(rows):
        row_cells = table.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row):
            row_cells[c_idx].text = str(val)
    if col_widths:
        for row in table.rows:
            for i, width in enumerate(col_widths):
                row.cells[i].width = Inches(width)
    doc.add_paragraph()
    return table


doc = Document()

# Title
title = doc.add_heading(
    "Maharashtra Government Resolutions on Transfer of Tribal Land",
    level=0,
)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

subtitle = doc.add_paragraph(
    "Transfer of Land from Tribal to Tribal under the Maharashtra Land Revenue Code, 1966 (MLRC)"
)
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
subtitle.runs[0].italic = True

doc.add_paragraph("Prepared: August 7, 2026")
doc.add_paragraph()

# Disclaimer
doc.add_heading("Disclaimer", level=1)
doc.add_paragraph(
    "This note is compiled from official notifications, Revenue Department circulars, court "
    "records, and government resolution databases. There is no single official consolidated "
    "'master list' published by the Revenue & Forest Department in one document. For certified "
    "copies of Government Resolutions, refer to the Maharashtra GR portal "
    "(https://gr.maharashtra.gov.in/) or the Revenue & Forest Department, Mantralaya, Mumbai."
)

# Section 1
doc.add_heading("1. Legal Framework under MLRC", level=1)
doc.add_paragraph(
    "The Maharashtra Land Revenue Code, 1966 (MLRC) protects tribal land rights through "
    "Sections 36, 36A, and 36B. For transfers from one tribal person to another tribal person, "
    "the governing provision is Section 36(2) — not Section 36A, which applies only to "
    "transfers from tribal to non-tribal persons."
)

add_table(
    doc,
    ["Provision", "Subject"],
    [
        ["Section 36(2)", "Restricts transfer of tribal occupancy; requires Collector's prior sanction for ALL tribal transfers"],
        ["Section 36(3)", "Restoration of land if transferred without Collector sanction"],
        ["Section 36A", "Restricts transfer of tribal land to NON-TRIBALS only (sale, gift, lease, mortgage, exchange, etc.)"],
        ["Section 36B", "Damages for unauthorized use/occupation by non-tribals"],
        ["Maharashtra Restoration of Lands to Scheduled Tribes Act, 1974", "Restoration of tribal land alienated before 6 July 1974"],
        ["Maharashtra Land Revenue (Restoration of Occupancy transferred by members of Scheduled Tribes) Rules, 1969", "Procedure for applications under Section 36(3)"],
    ],
    [1.5, 4.5],
)

# Section 2
doc.add_heading("2. Legal Position: Tribal to Tribal Transfer", level=1)

add_table(
    doc,
    ["Aspect", "Position"],
    [
        ["Governing Section", "Section 36(2) MLRC, 1966"],
        ["Sanction Required", "Collector's prior sanction — mandatory even if buyer is also tribal"],
        ["State Government Approval", "NOT required (unlike tribal to non-tribal sales)"],
        ["Gram Sabha Sanction", "NOT required (2016 notification applies only to tribal to non-tribal)"],
        ["Section 36A", "Does NOT apply to tribal to tribal transfers"],
        ["1975 Transfer Rules", "Do NOT directly govern tribal to tribal transfers (framed under Section 36A for non-tribal transferees)"],
    ],
    [2.0, 4.0],
)

doc.add_paragraph(
    "Section 36(2) provides that occupancies of persons belonging to Scheduled Tribes shall "
    "not be transferred except with the previous sanction of the Collector. The proviso to "
    "Section 36(2) carves out an exception: it does not apply to transfers made in favour of "
    "non-tribals on or after 6 July 1974 — those are governed separately by Section 36A."
)

doc.add_heading("2.1 Key Judicial Authority", level=2)
doc.add_paragraph(
    "Vijay Anandrao Moghe v. Additional Collector, Bombay High Court (Nagpur Bench), "
    "Writ Petition No. 1556 of 2022, decided on 11 April 2022:"
)
quote = doc.add_paragraph(
    '"Section 36(2) does not make any distinction based on the status of the purchaser… '
    'if the transfer is between tribal and tribal, the previous sanction of the Collector is a must."'
)
quote.runs[0].italic = True

doc.add_paragraph(
    "The Court held that the Legislature did not exempt tribal-to-tribal transfers from the "
    "requirement of Collector sanction, as a tribal transferor could still be exploited by a "
    "fellow tribal in a dominating position."
)

# Section 3
doc.add_heading("3. Comparison: Tribal to Tribal vs Tribal to Non-Tribal", level=1)

add_table(
    doc,
    ["Aspect", "Tribal → Tribal", "Tribal → Non-Tribal"],
    [
        ["Governing Provision", "Section 36(2)", "Section 36A"],
        ["Collector Sanction", "Required", "Required"],
        ["State Government Approval", "Not required", "Required (except lease/mortgage ≤ 5 years)"],
        ["Gram Sabha Sanction (Scheduled Areas)", "Not required", "Required (2016 notification)"],
        ["Public Notice to Other Tribals", "Not under 1975 Rules", "Required under 1975 Rules"],
        ["Preference to Tribals within 5 km", "Not applicable", "Mandatory before non-tribal approval"],
        ["Transfer Without Sanction", "Void; restoration under Section 36(3)", "Void; inquiry under Section 36A(4)-(5)"],
    ],
    [1.8, 2.1, 2.1],
)

# Section 4
doc.add_heading("4. Government Resolutions — Tribal to Tribal Transfer", level=1)

doc.add_heading("4.1 Directly on Transfer Permission (Section 36(2))", level=2)
add_table(
    doc,
    ["Sr.", "GR / CR No.", "Date", "Subject"],
    [
        ["1", "क्र.मशा/कार्या-4/टेनन्सी-2/सी.आर.18/2011", "16-09-2011", "Instructions on transfers of tribal land under Section 36(2) MLRC (covers tribal to tribal and other transfers by tribals)"],
        ["2", "REV. 1070/62448-C", "15-03-1971", "Appointment of Committee to study effectiveness of MLRC/tenancy laws in protecting Scheduled Tribes (led to 1974 amendments including Section 36(2))"],
    ],
    [0.4, 1.8, 0.9, 3.4],
)

doc.add_heading("4.2 Occupant Class-II Tribal Land (Ceiling / Inam / Restricted Tenure)", level=2)
doc.add_paragraph(
    "Many tribal lands are held as Occupant Class-II (restricted tenure). For tribal to tribal "
    "sale of such land, the following GRs apply:"
)
add_table(
    doc,
    ["Sr.", "GR / CR No.", "Date", "Subject"],
    [
        ["1", "LND/1083/27925/CR-3671/C-6", "08-09-1983", "Permission for sale, gift, mortgage of Occupant Class-II agricultural land; premium/unearned income on NA conversion"],
        ["2", "Land-10/2002/M.No.387/L-1", "29-05-2006", "Valuation methodology (Ready Reckoner rates) for Class-II land transfers"],
        ["3", "Land-11/2013/M.No.502/L-1", "28-01-2014", "Clarification on unearned income calculation for Class-II land sales"],
        ["4", "Vatan-1099/CR-223/L-4", "09-07-2002", "Conversion of Occupant Class-II inam vatan lands to Class-I (except Mahar vatan)"],
    ],
    [0.4, 1.8, 0.9, 3.4],
)
doc.add_paragraph(
    "District revenue offices process these as 'Occupant Class 2 — Tribal to Tribal Land Sale "
    "Permit' applications (Ceiling, Inam Varg 6B, Tribal to Tribal)."
)

doc.add_heading("4.3 Land Records and Identification", level=2)
add_table(
    doc,
    ["Sr.", "GR / CR No.", "Date", "Subject"],
    [
        ["1", "GR (Revenue Dept.)", "17-03-2012", "Mandatory marking in 7/12 extract that land belongs to a tribal (within 2 months); cited in Bombay High Court judgments"],
        ["2", "Adivasi-1009/CR.323/L-9", "31-05-2012", "Extension of restoration period under Sections 36(3) & 36A(4) to 30 years with retrospective effect (Circular dated 14-02-2012)"],
    ],
    [0.4, 1.8, 0.9, 3.4],
)

doc.add_heading("4.4 Restoration if Transfer Done Without Sanction", level=2)
doc.add_paragraph(
    "If a tribal to tribal transfer occurs without Collector sanction, restoration can be sought "
    "under Section 36(3):"
)
add_table(
    doc,
    ["Sr.", "GR / CR No.", "Date", "Subject"],
    [
        ["1", "UNF. 1567(h)-R (Rules, 1969)", "10-04-1969", "Maharashtra Land Revenue (Restoration of Occupancy transferred by members of Scheduled Tribes) Rules, 1969 — procedure for applications under Section 36(3)"],
        ["2", "Adivasi 2002/Pr.Kr.831/L-9", "11-01-2002", "Preservation of records relating to tribal land transfer/restoration"],
        ["3", "Adivasi 1008/Pr.Kr.18/L-9", "14-07-2009", "Collector to inquire and restore tribal land illegally transferred"],
        ["4", "REV. 6775/44738/L-8", "04-06-1979", "Implementation of Maharashtra Land Revenue (Restoration of Occupancy) Rules, 1969"],
    ],
    [0.4, 1.8, 0.9, 3.4],
)

# Section 5
doc.add_heading("5. GRs That Do NOT Apply to Tribal to Tribal Transfer", level=1)
doc.add_paragraph(
    "The following Government Resolutions and notifications govern tribal to NON-TRIBAL "
    "transfers only and do not apply to tribal to tribal transactions:"
)
add_table(
    doc,
    ["Sr.", "GR / CR No.", "Date", "Subject"],
    [
        ["1", "REV/1074/208094-L-9", "02-10-1975", "Maharashtra Land Revenue (Transfer of Occupancy by Tribals to Non-Tribals) Rules, 1975"],
        ["2", "Adivasi-3010/Pr.Kr.313/L-9", "15-09-2010", "Permission for transfer of tribal land under Section 36A"],
        ["3", "NO/MISC-2010/1812/CR.309/L-9", "02-04-2012", "Guidelines on granting permission for tribal land transfer under Section 36A"],
        ["4", "Adivasi-2013/Pr.Kr.25/L-9", "26-03-2013", "No permission for development agreements/POA/NA conversion by non-tribals on tribal land"],
        ["5", "LND.1067/126110-G-6", "26-04-1976", "Restriction on alienation of tribal land to non-tribals"],
        ["6", "Governor Notification", "14-06-2016", "Prior Gram Sabha sanction required for tribal to non-tribal transfer in Scheduled Areas"],
        ["7", "Governor Notification", "14-11-2017", "Exemption for vital government projects (no Gram Sabha sanction for State purchase by mutual agreement)"],
        ["8", "Jamin-2023/C.R.416/J-1", "24-12-2024", "Divisional Commissioner can approve tribal land transfer up to 3 ares for mobile towers to non-tribals"],
    ],
    [0.4, 1.8, 0.9, 3.4],
)

# Section 6 - Historical GRs
doc.add_heading("6. Historical GRs on Tribal Land (Restoration & Implementation)", level=1)
doc.add_paragraph(
    "The following older GRs relate primarily to restoration of tribal land and implementation "
    "of the Maharashtra Restoration of Lands to Scheduled Tribes Act, 1974. They are relevant "
    "background for tribal land transfer law but apply mainly to tribal to non-tribal alienation "
    "and restoration proceedings:"
)

historical = [
    ("REV.1378/23112-L-8", "07-07-1978", "Implementation of MLRC Amendment Act 1974 and Restoration Act 1974"),
    ("REV.1378/13475/L-8", "13-06-1978", "Restoration of lands to tribals under Acts of 1974 and 1975"),
    ("REV.1377/264775(a)-L-8", "12-04-1978", "Implementation of measures for restoration of lands to tribals"),
    ("REV.1077/17133-L-8", "22-08-1977", "Amendment to 1975 Rules (transfer to non-tribals and restoration)"),
    ("REV.1076/30284-L-8", "16-08-1977", "Implementation of MLRC Amendment Act 1976 and Restoration Act"),
    ("REV.1377/1099-L-8", "28-06-1977", "Implementation of MLRC and Restoration Acts 1974"),
    ("REV.1075/49247-L-9", "10-11-1975", "Maharashtra Restoration of Lands to Scheduled Tribes Rules, 1975"),
    ("REV/1074/208094-L-9", "11-10-1975", "Maharashtra Land Revenue (Transfer of Occupancy by Tribals to Non-Tribals) Rules, 1975"),
    ("Adivasi-1901/Pr.Kr.779/L-9", "01-08-2003", "Revival of closed cases under Restoration Act, 1974"),
    ("Adivasi 1087/684/L-9", "02-10-1987", "Implementation of laws for restoration of alienated tribal land"),
    ("Adivasi 1985/CR/3425/L-9", "28-08-1985", "Implementation of restoration laws"),
    ("REV.1379/6059-L-9", "31-08-1981", "Procedure for deposit and expenditure of amounts from tribal transferors"),
]

add_table(
    doc,
    ["GR / CR No.", "Date", "Subject"],
    historical,
    [2.0, 1.0, 3.5],
)

doc.add_paragraph(
    "A comprehensive list of 70+ GRs from 1974–2013 is available at: "
    "https://govtgr.com/adiwasi-jamin-parat-gr/"
)

# Section 7
doc.add_heading("7. Practical Procedure for Tribal to Tribal Sale", level=1)
steps = [
    "Verify tribal status of both transferor and transferee (caste certificate and revenue records).",
    "Check land tenure — Occupant Class-I vs Class-II, ceiling land, inam land, etc.",
    "Apply to the Collector (through Tahsildar/Sub-Divisional Officer) for prior sanction under Section 36(2).",
    "For Occupant Class-II land, also comply with GR dated 08-09-1983 and subsequent valuation GRs if non-agricultural use is involved.",
    "Collector examines the application, verifies that transfer does not render the transferor landless, and checks compliance with tenure conditions.",
    "Upon grant of sanction, execute a registered sale deed.",
    "Apply for mutation (ferfar) in revenue records.",
    "Ensure 7/12 extract reflects tribal ownership status (as per GR dated 17-03-2012).",
]
for i, step in enumerate(steps, 1):
    doc.add_paragraph(f"{i}. {step}", style="List Number")

doc.add_heading("7.1 Typical Documents Required", level=2)
docs_required = [
    "Application for sale permission to Collector",
    "Draft sale deed",
    "7/12 extract (Satbara Utara)",
    "8A extract",
    "Caste certificates of transferor and transferee",
    "Mutation entries / title documents",
    "Survey map / property description",
    "Affidavit regarding consideration and purpose of transfer",
    "NOCs from relevant departments (if applicable)",
    "Identity and address proof of both parties",
]
for item in docs_required:
    doc.add_paragraph(item, style="List Bullet")

# Section 8
doc.add_heading("8. Important Conditions and Restrictions", level=1)
conditions = [
    "Economic Holding Limit: Under Section 36A(6) Explanation (applicable when land is restored/re-granted), economic holding means 6.48 hectares (16 acres) of jirayat land, or 3.24 hectares (8 acres) of seasonally irrigated/paddy land, or 1.62 hectares (4 acres) of perennially irrigated land.",
    "Landless Transferor: Sale should not render the tribal transferor landless; Collector may refuse sanction.",
    "Occupant Class-II Restrictions: Additional conditions under GR of 1983 including payment of premium/unearned income for NA conversion.",
    "Restoration Period: Applications for restoration of illegally transferred land can be made within 30 years from 6 July 2004 (extended by Adivasi-1009/CR.323/L-9, 2012).",
    "Heritability: Tribal occupancy remains heritable; transfer restrictions do not affect inheritance to legal heirs in accordance with law.",
]
for item in conditions:
    doc.add_paragraph(item, style="List Bullet")

# Section 9
doc.add_heading("9. Official Sources and References", level=1)
sources = [
    ("Maharashtra GR Portal (Official)", "https://gr.maharashtra.gov.in/"),
    ("Tribal Land GR Database (Unofficial)", "https://govtgr.com/adiwasi-jamin-parat-gr/"),
    ("MLRC Text (Updated April 2025)", "https://lj.maharashtra.gov.in/document/the-maharashtra-land-revenue-code-1966-text-as-on-2nd-april-2025/"),
    ("Nashik Division — Land Reform Branch Circulars", "https://divcomnashik.maharashtra.gov.in/en/land-reform-branch/"),
    ("Governor Notifications (Section 36A)", "https://rajbhavan-maharashtra.gov.in/en/document-category/notifications-issued-by-honble-governor/"),
    ("Section 36 — Indian Kanoon", "https://indiankanoon.org/doc/166429499/"),
    ("Section 36A — Indian Kanoon", "https://indiankanoon.org/doc/127847697/"),
    ("1975 Transfer Rules", "https://www.latestlaws.com/bare-acts/state-acts-rules/maharashtra-state-laws/maharashtra-land-revenue-code-1966/maharashtra-land-revenue-transfer-of-occupancy-by-tribals-to-non-tribals-rules-1975/"),
]
add_table(
    doc,
    ["Source", "URL"],
    sources,
    [2.5, 4.0],
)

# Section 10 - Summary
doc.add_heading("10. Executive Summary", level=1)
doc.add_paragraph(
    "For transfer of land from one tribal person to another tribal person under the Maharashtra "
    "Land Revenue Code, 1966:"
)
summary_points = [
    "The governing statutory provision is Section 36(2), NOT Section 36A.",
    "Prior sanction of the Collector is mandatory — no exemption for tribal-to-tribal transfers.",
    "State Government approval is NOT required (unlike tribal-to-non-tribal transfers).",
    "Gram Sabha sanction is NOT required for tribal-to-tribal transfers.",
    "The key Government Resolution is क्र.मशा/कार्या-4/टेनन्सी-2/सी.आर.18/2011 dated 16-09-2011.",
    "For Occupant Class-II (restricted tenure) tribal land, GR LND/1083/27925/CR-3671/C-6 dated 08-09-1983 applies.",
    "Transfers without Collector sanction are invalid and subject to restoration under Section 36(3).",
    "The 1975 Transfer Rules and Section 36A GRs apply ONLY to tribal-to-non-tribal transfers.",
]
for point in summary_points:
    doc.add_paragraph(point, style="List Bullet")

doc.add_paragraph()
footer = doc.add_paragraph("— End of Document —")
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER

output_path = "/workspace/Maharashtra_Tribal_to_Tribal_Land_Transfer_GR_Note.docx"
doc.save(output_path)
print(f"Created: {output_path}")
