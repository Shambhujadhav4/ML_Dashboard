from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from PIL import Image

from app.schemas.results import DatasetInsights, DatasetSummary, ProjectSnapshot, WorkflowRecommendation
from app.services.dataset_service import dataset_store
from app.services.recommendation_service import recommendation_service


router = APIRouter(prefix="/upload", tags=["upload"])


def _build_image_frame(content: bytes, filename: str | None) -> pd.DataFrame:
    try:
        with Image.open(io.BytesIO(content)) as image:
            image.load()
            width, height = image.size
            format_name = image.format or (Path(filename).suffix.lstrip(".").upper() if filename else "IMAGE")
            records = [
                {
                    "file_name": filename or "image",
                    "format": format_name,
                    "width": width,
                    "height": height,
                    "mode": image.mode,
                    "aspect_ratio": round(width / height, 4) if height else None,
                    "pixel_count": int(width * height),
                    "file_size_bytes": len(content),
                }
            ]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to read image file: {exc}") from exc

    return pd.DataFrame(records)


def _detect_file_kind(file: UploadFile) -> str:
    filename = (file.filename or "").lower()
    content_type = (file.content_type or "").lower()
    suffix = Path(filename).suffix

    if suffix == ".csv" or content_type in {"text/csv", "application/vnd.ms-excel"}:
        return "csv"
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"} or content_type.startswith("image/"):
        return "image"
    return "unsupported"


def _create_session_from_upload(
    *,
    dataframe: pd.DataFrame,
    input_kind: str,
    filename: str | None,
    content_type: str | None,
    file_size_bytes: int,
) -> DatasetSummary:
    session = dataset_store.create_project(
        dataframe,
        input_kind=input_kind,
        source_filename=filename,
        source_mime_type=content_type,
        file_size_bytes=file_size_bytes,
    )
    return dataset_store.build_summary(session)


from app.core.executor import run_in_process

def _read_csv_sync(content_bytes, sep, encoding, header):
    return pd.read_csv(io.BytesIO(content_bytes), sep=sep, encoding=encoding, header=header)

@router.post("/csv", response_model=DatasetSummary)
async def upload_csv(
    file: UploadFile = File(...),
    separator: str = Form(","),
    encoding: str = Form("utf-8"),
    header_row: int = Form(0),
) -> DatasetSummary:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A CSV file is required.")

    content = await file.read()
    actual_separator = "\t" if separator == "\\t" else separator
    try:
        dataframe = await run_in_process(_read_csv_sync, content, actual_separator, encoding, header_row)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to parse CSV: {exc}") from exc

    return _create_session_from_upload(
        dataframe=dataframe,
        input_kind="csv",
        filename=file.filename,
        content_type=file.content_type,
        file_size_bytes=len(content),
    )


@router.post("/file", response_model=DatasetSummary)
async def upload_file(
    file: UploadFile = File(...),
    encoding: str = Form("utf-8"),
    separator: str = Form(","),
    header_row: int = Form(0),
) -> DatasetSummary:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file is required.")

    content = await file.read()
    input_kind = _detect_file_kind(file)
    suffix = Path(file.filename).suffix.lower()

    if input_kind == "csv":
        actual_separator = "\t" if separator == "\\t" else separator
        try:
            dataframe = await run_in_process(_read_csv_sync, content, actual_separator, encoding, header_row)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Unable to parse CSV: {exc}") from exc
        detected_kind = "csv"
    elif input_kind == "image":
        dataframe = await run_in_process(_build_image_frame, content, file.filename)
        detected_kind = "image"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a CSV or image file.")

    return _create_session_from_upload(
        dataframe=dataframe,
        input_kind=detected_kind,
        filename=file.filename,
        content_type=file.content_type,
        file_size_bytes=len(content),
    )

def _get_insights_sync(session):
    dataframe = session.processed_data
    column_info = [
        {
            "column": str(column),
            "dtype": str(dataframe[column].dtype),
            "non_null": int(dataframe[column].count()),
            "null": int(dataframe[column].isnull().sum()),
            "unique": int(dataframe[column].nunique(dropna=True)),
        }
        for column in dataframe.columns
    ]

    descriptive_statistics = (
        dataframe.describe(include="all")
        .transpose()
        .replace({np.nan: None})
        .reset_index()
        .rename(columns={"index": "column"})
        .to_dict(orient="records")
    )
    return column_info, descriptive_statistics

@router.get("/{project_id}/insights", response_model=DatasetInsights)
async def get_dataset_insights(project_id: str) -> DatasetInsights:
    try:
        session = dataset_store.get_project(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    column_info, descriptive_statistics = await run_in_process(_get_insights_sync, session)

    return DatasetInsights(
        project_id=session.project_id,
        summary=dataset_store.build_summary(session),
        column_info=column_info,
        descriptive_statistics=descriptive_statistics,
    )


@router.get("/{project_id}/workflow-recommendation", response_model=WorkflowRecommendation)
async def get_workflow_recommendation(
    project_id: str,
    benchmark_metric: str | None = Query(default=None),
) -> WorkflowRecommendation:
    try:
        session = dataset_store.get_project(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return await run_in_process(recommendation_service.recommend, session, benchmark_metric)


@router.get("/{project_id}", response_model=ProjectSnapshot)
def get_project(project_id: str) -> ProjectSnapshot:
    try:
        session = dataset_store.get_project(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return dataset_store.build_snapshot(session)


@router.post("/{project_id}/reset", response_model=ProjectSnapshot)
def reset_project(project_id: str) -> ProjectSnapshot:
    try:
        session = dataset_store.get_project(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    dataset_store.reset_to_raw(session)
    return dataset_store.build_snapshot(session)
