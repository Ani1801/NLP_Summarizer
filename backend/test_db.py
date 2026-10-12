import asyncio
from datetime import datetime
from app.models.audit import Audit
from app.services.database import save_audit
from bson import ObjectId

async def test_save_audit():
    print("🚀 Starting Database Connection Test...")
    
    # 1. Create Mock Audit Data (Matching your Pydantic Schema)
    # Note: In a real flow, user_id comes from your JWT token
    mock_audit = {
        "user_id": str(ObjectId()), # Generates a fake valid MongoDB ID
        "file_name": "test_contract_v1.pdf",
        "status": "Completed",
        "risk_score": 75,
        "summary": "This is a test summary for the legal audit system.",
        "risks": [
            {
                "title": "Indemnity Gap",
                "severity": "High",
                "description": "The contract lacks mutual indemnification clauses."
            },
            {
                "title": "Governing Law",
                "severity": "Low",
                "description": "Jurisdiction is set to Delaware."
            }
        ],
        "created_at": datetime.now()
    }

    try:
        # 2. Attempt to save to MongoDB
        result_id = await save_audit(mock_audit)
        
        if result_id:
            print(f"✅ Success! Audit saved with ID: {result_id}")
            print("📥 Check your MongoDB Compass 'audits' collection now.")
        else:
            print("❌ Failed: Save function returned None.")
            
    except Exception as e:
        print(f"💥 Connection Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_save_audit())