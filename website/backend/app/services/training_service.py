from __future__ import annotations

from typing import Any
from pathlib import Path
import pickle
import tempfile

import numpy as np

from modules.models import ModelTrainer

from app.schemas.training import TrainRequest
from app.services.dataset_service import ProjectSession


def _serialize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


class TrainingService:
    def _artifact_path(self, session: ProjectSession) -> Path:
        safe_model_name = "".join(
            character if character.isalnum() or character in {"-", "_"} else "-"
            for character in (session.model_trainer.model_name or "model")
        ).strip("-") or "model"
        # Store in the persistent models directory relative to project root
        # In Docker this maps to /app/models
        artifact_dir = Path("models") / session.project_id
        artifact_dir.mkdir(parents=True, exist_ok=True)
        return artifact_dir / f"{safe_model_name}.pkl"

    def _save_artifact(self, session: ProjectSession) -> None:
        if session.model_trainer is None or session.model_trainer.model is None:
            return

        artifact_path = self._artifact_path(session)
        payload = {
            "project_id": session.project_id,
            "input_kind": session.input_kind,
            "source_filename": session.source_filename,
            "source_mime_type": session.source_mime_type,
            "task_type": session.task_type,
            "model_name": session.model_trainer.model_name,
            "feature_names": session.model_trainer.feature_names,
            "target_column": session.target_column,
            "model": session.model_trainer.model,
        }

        with artifact_path.open("wb") as artifact_file:
            pickle.dump(payload, artifact_file)

        session.artifact_path = str(artifact_path)
        session.artifact_filename = artifact_path.name

    def train(self, session: ProjectSession, request: TrainRequest) -> ProjectSession:
        trainer = ModelTrainer()
        trainer.prepare_data(
            session.processed_data,
            request.target_column,
            request.feature_columns,
            request.test_size,
            request.random_state,
            request.task_type,
        )
        trainer.train(request.task_type, request.model_name)
        metrics = trainer.get_metrics()
        if request.run_cv:
            metrics["cv_scores"] = trainer.get_cross_val_scores(cv=5)

        session.model_trainer = trainer
        session.model_results = _serialize(metrics)
        session.target_column = request.target_column
        session.feature_columns = request.feature_columns.copy()
        session.task_type = request.task_type
        self._save_artifact(session)
        return session


training_service = TrainingService()
