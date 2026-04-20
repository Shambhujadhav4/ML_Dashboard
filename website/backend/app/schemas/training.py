from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TrainRequest(BaseModel):
    project_id: str
    task_type: Literal["classification", "regression"]
    model_name: str
    target_column: str
    feature_columns: list[str] = Field(min_length=1)
    test_size: float = 0.2
    random_state: int = 42
    run_cv: bool = True
