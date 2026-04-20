from fastapi import APIRouter


router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("")
def predict_placeholder() -> dict[str, str]:
    return {
        "message": "Prediction endpoint placeholder. Add batch and single-row inference here next.",
    }
