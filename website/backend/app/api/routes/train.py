from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.schemas.results import ProjectSnapshot
from app.schemas.training import TrainRequest
from app.services.dataset_service import dataset_store
from app.services.training_service import training_service
from app.services.visualization_service import visualization_service


router = APIRouter(prefix="/train", tags=["train"])


from app.core.executor import run_in_process

@router.post("", response_model=ProjectSnapshot)
async def train_model(request: TrainRequest) -> ProjectSnapshot:
    try:
        session = dataset_store.get_project(request.project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        # Run training in a background thread so it doesn't block FastAPI
        session = await run_in_process(training_service.train, session, request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return dataset_store.build_snapshot(session)


@router.get("/{project_id}/feature-importance")
def feature_importance(project_id: str) -> dict[str, object]:
    try:
        session = dataset_store.get_project(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {
        "project_id": project_id,
        "feature_importance": visualization_service.feature_importance(session),
    }


@router.get("/{project_id}/artifact")
def download_artifact(project_id: str) -> FileResponse:
    try:
        session = dataset_store.get_project(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if not session.artifact_path:
        raise HTTPException(status_code=404, detail="No saved model artifact is available for this project.")

    artifact_path = Path(session.artifact_path)
    if not artifact_path.exists():
        raise HTTPException(status_code=404, detail="The saved model artifact could not be found on disk.")

    download_name = session.artifact_filename or artifact_path.name
    return FileResponse(
        path=artifact_path,
        media_type="application/octet-stream",
        filename=download_name,
    )
