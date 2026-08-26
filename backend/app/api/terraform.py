from fastapi import APIRouter, HTTPException, Request, UploadFile

from app.services.reconciliation import ReconciliationService
from app.services.terraform import TerraformStateParser

router = APIRouter()
parser = TerraformStateParser()
reconcile = ReconciliationService(parser)


@router.post("/terraform/analyze")
async def analyze_terraform(request: Request, file: UploadFile | None = None) -> dict:
    if file is None:
        raise HTTPException(status_code=400, detail="terraform.tfstate file is required")
    raw = await file.read()
    try:
        import json

        state = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=400, detail="Invalid terraform state JSON") from exc
    tf_resources = parser.parse(state)
    snapshot = await request.app.state.inventory.get_snapshot()
    rows = reconcile.classify(snapshot.resources, tf_resources)
    return {
        "terraform_resources": len(tf_resources),
        "rows": rows,
    }
