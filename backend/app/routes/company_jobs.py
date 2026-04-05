import base64
import os

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.company_job_search import (
    DEFAULT_MAX_COMPANIES,
    extract_companies_from_xlsx,
    fill_xlsx_with_job_links,
    search_jobs_for_company_list,
)

router = APIRouter()


@router.post("/jobs-from-companies")
async def jobs_from_company_excel(
    file: UploadFile = File(...),
    fill_spreadsheet: str = Form("false"),
):
    """
    Upload a .xlsx with a Company column (or company names in column C).
    Searches job boards for data / business analyst roles at those companies.
    """
    filename = (file.filename or "").lower()
    if not filename.endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Please upload an Excel file in .xlsx format.",
        )

    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read file: {e}")

    if not content:
        raise HTTPException(status_code=400, detail="Empty file.")

    try:
        companies = extract_companies_from_xlsx(content)
    except Exception as e:
        print(f"❌ Excel parse error: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Could not read spreadsheet: {str(e)}. Use .xlsx with a 'Company' column or names in column C.",
        )

    if not companies:
        raise HTTPException(
            status_code=422,
            detail="No company names found. Add a header 'Company' or put names in column C.",
        )

    max_c = int(os.getenv("COMPANY_LIST_MAX", str(DEFAULT_MAX_COMPANIES)))

    try:
        results, meta = await search_jobs_for_company_list(
            companies, max_companies=max_c, concurrency=4
        )
    except Exception as e:
        print(f"❌ Company job search error: {e}")
        raise HTTPException(status_code=500, detail=f"Job search failed: {str(e)}")

    want_fill = fill_spreadsheet.lower() in ("true", "1", "yes", "on")

    payload = {
        "total": len(results),
        "results": results,
        "meta": meta,
    }

    if want_fill:
        try:
            filled = fill_xlsx_with_job_links(content, results)
            payload["filled_xlsx_base64"] = base64.standard_b64encode(filled).decode("ascii")
            base_name = (file.filename or "companies.xlsx").rsplit("/", 1)[-1]
            stem = base_name[:-5] if base_name.lower().endswith(".xlsx") else base_name
            payload["filled_filename"] = f"{stem}_with_job_links.xlsx"
        except Exception as e:
            print(f"❌ Fill spreadsheet: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Could not write job links into the Excel file: {str(e)}",
            )

    return payload
