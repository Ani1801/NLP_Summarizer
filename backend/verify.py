from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Count 1 /Kids [3 0 R] >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n5 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 24 Tf\n100 100 Td\n(Hello World) Tj\nET\nendstream\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"

with open("dummy.pdf", "wb") as f:
    f.write(pdf_content)

with open("dummy.pdf", "rb") as f:
    response = client.post("/api/test/process", files={"file": ("dummy.pdf", f, "application/pdf")})
    print("STATUS_CODE:", response.status_code)
    print("RESPONSE:", response.json())

os.remove("dummy.pdf")
