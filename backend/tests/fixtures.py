"""
Test fixtures — generates a realistic multi-page contract PDF on the fly.

Keeping the fixture as code rather than a committed binary means the expected
section numbers, page numbers and clause values are visible right here, next to
the assertions that depend on them.
"""

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

_PAGE_BREAK = (None, None)

# (heading, body). A (None, None) entry forces a page break, which is how the
# fixture pins specific clauses to specific pages.
SAMPLE_MSA = [
    ("MASTER SERVICES AGREEMENT", None),
    (None,
     'This Master Services Agreement (the "Agreement") is entered into as of '
     'October 1, 2026 (the "Effective Date") by and between Acme Enterprise '
     'Solutions Inc., a Delaware corporation with offices at 100 Innovation Way, '
     'New York, NY 10001 ("Provider"), and Global Logistics Corp., an Illinois '
     'corporation with offices at 500 Commerce Blvd, Chicago, IL 60601 ("Client").'),
    ("1. Scope of Services",
     "1.1 Provider shall furnish software architecture consulting and code audit "
     'deliverables as described in one or more Statements of Work ("SOW") executed '
     "by both parties. 1.2 Client shall have ten (10) business days to accept or "
     "reject any deliverable; deliverables not rejected in writing within that "
     "period are deemed accepted."),
    ("2. Term and Renewal",
     "2.1 The initial term of this Agreement commences on the Effective Date and "
     "continues for twenty-four (24) months, expiring September 30, 2028. 2.2 This "
     "Agreement renews automatically for successive twelve (12) month periods unless "
     "either party delivers written notice of non-renewal at least sixty (60) days "
     "before the end of the then-current term."),
    _PAGE_BREAK,
    ("3. Fees and Payment",
     "3.1 Client shall pay Provider a monthly retainer of Ten Thousand Dollars "
     "($10,000 USD), for a total estimated contract value of Two Hundred Forty "
     "Thousand Dollars ($240,000 USD) over the initial term. 3.2 Invoices are "
     "payable within thirty (30) days of receipt. 3.3 Past due balances shall accrue "
     "interest at one and one-half percent (1.5%) per month or the maximum rate "
     "permitted by law, whichever is lower."),
    ("4. Confidentiality",
     "4.1 Each party shall hold the other party's Confidential Information in strict "
     "confidence. 4.2 Confidential Information shall remain protected for three (3) "
     "years following termination or expiration of this Agreement. 4.3 The receiving "
     "party may disclose Confidential Information if compelled by law, provided it "
     "gives prompt notice to the disclosing party."),
    ("5. Termination",
     "5.1 Either party may terminate this Agreement for convenience at any time upon "
     "thirty (30) calendar days prior written notice to the other party. 5.2 Either "
     "party may terminate immediately upon a material breach that remains uncured "
     "fourteen (14) days after written notice. 5.3 Provider may suspend services "
     "immediately upon any payment being more than forty-five (45) days overdue, "
     "without liability."),
    _PAGE_BREAK,
    ("6. Intellectual Property",
     "6.1 All pre-existing intellectual property of each party remains its sole "
     "property. 6.2 Upon full payment, Provider assigns to Client all right, title "
     "and interest in the deliverables, excluding Provider's pre-existing tools, "
     "libraries and know-how, for which Client receives a perpetual, non-exclusive "
     "licence."),
    ("7. Limitation of Liability",
     "7.1 EXCEPT AS SET FORTH IN SECTION 8, NEITHER PARTY'S AGGREGATE LIABILITY "
     "ARISING OUT OF THIS AGREEMENT SHALL EXCEED THE TOTAL FEES PAID BY CLIENT IN "
     "THE TWELVE (12) MONTHS IMMEDIATELY PRECEDING THE CLAIM. 7.2 NEITHER PARTY "
     "SHALL BE LIABLE FOR INDIRECT, INCIDENTAL, CONSEQUENTIAL, SPECIAL OR PUNITIVE "
     "DAMAGES, INCLUDING LOST PROFITS, EVEN IF ADVISED OF THE POSSIBILITY THEREOF."),
    ("8. Indemnification",
     "8.1 Provider shall defend, indemnify and hold harmless Client against any "
     "third-party claim alleging that the deliverables infringe a patent, copyright "
     "or trade secret. 8.2 Client shall indemnify Provider against claims arising "
     "from Client data or Client's use of the deliverables in violation of applicable "
     "law. 8.3 Indemnification obligations under this Section are not subject to the "
     "cap in Section 7.1."),
    _PAGE_BREAK,
    ("9. Governing Law and Dispute Resolution",
     "9.1 This Agreement shall be governed by and construed in accordance with the "
     "laws of the State of New York, without regard to its conflict of laws "
     "principles. 9.2 Any dispute arising under this Agreement shall be finally "
     "resolved by binding arbitration administered by the American Arbitration "
     "Association in New York County, New York. 9.3 Each party waives any right to a "
     "jury trial and to participate in a class action."),
    ("10. Miscellaneous",
     "10.1 Neither party may assign this Agreement without the other party's prior "
     "written consent, except to a successor in a merger or sale of substantially all "
     "assets. 10.2 This Agreement constitutes the entire agreement between the "
     "parties and supersedes all prior discussions."),
    ("11. Signatures",
     "IN WITNESS WHEREOF, the parties have executed this Agreement as of the "
     "Effective Date. ACME ENTERPRISE SOLUTIONS INC. By: John Doe, Chief Executive "
     "Officer. GLOBAL LOGISTICS CORP. By: Jane Smith, Vice President of Operations."),
]

# What the processor is expected to find, asserted by the tests.
EXPECTED_SECTIONS = [
    ("", "Master Services Agreement", 1),
    ("1", "Scope of Services", 1),
    ("2", "Term and Renewal", 1),
    ("3", "Fees and Payment", 2),
    ("4", "Confidentiality", 2),
    ("5", "Termination", 2),
    ("6", "Intellectual Property", 3),
    ("7", "Limitation of Liability", 3),
    ("8", "Indemnification", 3),
    ("9", "Governing Law and Dispute Resolution", 4),
    ("10", "Miscellaneous", 4),
    ("11", "Signatures", 4),
]


def write_sample_contract(path: str) -> str:
    """Render the sample MSA to `path` and return that path."""
    styles = getSampleStyleSheet()
    heading = ParagraphStyle("h", parent=styles["Heading2"], spaceAfter=6)
    body = ParagraphStyle("b", parent=styles["BodyText"], spaceAfter=8, leading=14)

    flow = []
    for head, text in SAMPLE_MSA:
        if head is None and text is None:
            flow.append(PageBreak())
            continue
        if head:
            style = styles["Title"] if head.isupper() and len(head) < 40 else heading
            flow.append(Paragraph(head, style))
        if text:
            flow.append(Paragraph(text, body))
        flow.append(Spacer(1, 4))

    SimpleDocTemplate(path, pagesize=LETTER).build(flow)
    return path
