from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.services.dataset_service import dataset_store
from app.services.visualization_service import visualization_service


router = APIRouter(prefix="/visualize", tags=["visualize"])


def _get_session(project_id: str):
    try:
        return dataset_store.get_project(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{project_id}/metadata")
def visualization_metadata(project_id: str) -> dict[str, object]:
    session = _get_session(project_id)
    return {
        "project_id": project_id,
        "numeric_columns": visualization_service.available_numeric_columns(session),
        "categorical_columns": visualization_service.available_categorical_columns(session),
    }


@router.get("/{project_id}/missing-values")
def missing_values_chart(project_id: str) -> dict[str, object]:
    session = _get_session(project_id)
    return {
        "project_id": project_id,
        "figure": visualization_service.build_missing_values_figure(session),
    }


@router.get("/{project_id}/correlation")
def correlation_chart(project_id: str) -> dict[str, object]:
    session = _get_session(project_id)
    return {
        "project_id": project_id,
        "figure": visualization_service.build_correlation_figure(session),
    }


@router.get("/{project_id}/distribution")
def distribution_chart(project_id: str, column: str = Query(...)) -> dict[str, object]:
    session = _get_session(project_id)
    return {
        "project_id": project_id,
        "figure": visualization_service.build_distribution_figure(session, column),
    }


@router.get("/{project_id}/boxplot")
def boxplot_chart(project_id: str, column: str = Query(...)) -> dict[str, object]:
    session = _get_session(project_id)
    return {
        "project_id": project_id,
        "figure": visualization_service.build_boxplot_figure(session, column),
    }


@router.get("/{project_id}/countplot")
def countplot_chart(project_id: str, column: str = Query(...)) -> dict[str, object]:
    session = _get_session(project_id)
    return {
        "project_id": project_id,
        "figure": visualization_service.build_countplot_figure(session, column),
    }


@router.get("/{project_id}/scatter")
def scatter_chart(
    project_id: str,
    x_col: str = Query(...),
    y_col: str = Query(...),
    color_col: str | None = Query(default=None),
) -> dict[str, object]:
    session = _get_session(project_id)
    return {
        "project_id": project_id,
        "figure": visualization_service.build_scatter_figure(
            session,
            x_col=x_col,
            y_col=y_col,
            color_col=color_col,
        ),
    }


@router.get("/{project_id}/model-evaluation")
def model_evaluation_charts(project_id: str) -> dict[str, object]:
    session = _get_session(project_id)
    return {
        "project_id": project_id,
        "task_type": session.task_type,
        "confusion_matrix": visualization_service.build_confusion_matrix_figure(session),
        "roc_curve": visualization_service.build_roc_curve_figure(session),
        "actual_vs_predicted": visualization_service.build_actual_vs_predicted_figure(session),
        "residuals": visualization_service.build_residuals_figure(session),
    }
