"""
Export API Route — GET /api/export/{audit_id}

Generates and downloads a branded PDF or DOCX audit report.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from app.api.deps import get_current_user, get_db
from app.services.export_service import ExportService

router = APIRouter()
export_service = ExportService()


@router.get("/export/{audit_id}")
async def export_audit_report(
    audit_id: str,
    format: str = Query("pdf", pattern="^(pdf|docx)$"),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Export an audit report as PDF or DOCX.
    Query params: ?format=pdf or ?format=docx
    """
    user_id = str(current_user["_id"])
    audits_collection = db["audits"]

    # Validate audit ownership
    audit = await audits_collection.find_one({"_id": audit_id, "user_id": user_id})
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found or you don't have access to it."
        )

    # Fetch chat history if available
    chat_collection = db["chat_history"]
    chat_docs = await chat_collection.find(
        {"audit_id": audit_id, "user_id": user_id}
    ).sort("created_at", 1).to_list(length=100)

    chat_history = []
    for c in chat_docs:
        chat_history.append({"role": c.get("role", "user"), "content": c.get("content", "")})

    file_name = audit.get("file_name", "audit_report")
    base_name = file_name.rsplit(".", 1)[0] if "." in file_name else file_name

    if format == "docx":
        buffer = export_service.generate_docx(audit, chat_history or None)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ext = "docx"
    else:
        buffer = export_service.generate_pdf(audit, chat_history or None)
        media_type = "application/pdf"
        ext = "pdf"

    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{base_name}_audit_report.{ext}"'
        }
    )
