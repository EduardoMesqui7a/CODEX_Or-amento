from fastapi import APIRouter, Depends

from ..auth import get_current_user

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/plans")
def list_plans(_user=Depends(get_current_user)):
    return {
        "plans": [
            {"code": "free", "name": "Free", "price_brl": 0, "max_file_mb": 30, "max_jobs_month": 50},
            {"code": "pro", "name": "Pro", "price_brl": 14900, "max_file_mb": 80, "max_jobs_month": 400},
        ],
        "provider": "stripe",
        "checkout_enabled": False,
    }


@router.post("/webhook/stripe")
def stripe_webhook_placeholder():
    return {"received": True, "mode": "placeholder"}

