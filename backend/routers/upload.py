from fastapi import APIRouter, UploadFile, File, HTTPException
from services.parser import parse_statement
from services.categorizer import categorize_transactions
from models.schemas import UploadResponse

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_statement(file: UploadFile = File(...)):
    """
    Upload a bank statement PDF.
    Returns parsed and categorized transactions.
    """
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Validate file size (max 10MB)
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")

    try:
        # Step 1: Parse PDF → structured transactions
        statement = parse_statement(file_bytes)

        if not statement.transactions:
            return UploadResponse(
                success=False,
                message="No transactions found in the document.",
                error="The parser could not detect any transactions. Please check the PDF format."
            )

        # Step 2: Categorize transactions
        statement.transactions = categorize_transactions(statement.transactions)

        return UploadResponse(
            success=True,
            message=f"Successfully parsed {len(statement.transactions)} transactions from {statement.bank_name}.",
            statement=statement
        )

    except ValueError as e:
        return UploadResponse(
            success=False,
            message="Failed to parse statement.",
            error=str(e)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
