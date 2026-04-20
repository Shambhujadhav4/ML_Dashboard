from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class DropColumnsRequest(BaseModel):
    project_id: str
    columns: list[str] = Field(min_length=1)


class MissingValuesRequest(BaseModel):
    project_id: str
    strategy: Literal["drop_rows", "drop_columns", "mean", "median", "mode", "zero", "custom"]
    columns: list[str] = Field(default_factory=list)
    fill_value: str | float | int | None = None


class EncodeRequest(BaseModel):
    project_id: str
    method: Literal["label", "onehot"]
    columns: list[str] = Field(default_factory=list)


class ScaleRequest(BaseModel):
    project_id: str
    method: Literal["standard", "minmax", "robust"]
    columns: list[str] = Field(default_factory=list)


class OutlierRequest(BaseModel):
    project_id: str
    method: Literal["iqr_remove", "iqr_cap", "zscore_remove"]
    columns: list[str] = Field(default_factory=list)
    threshold: float = 1.5
