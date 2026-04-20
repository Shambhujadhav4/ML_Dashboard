from __future__ import annotations

import json
from typing import Any

import plotly.io as pio
from modules.visualizations import DataVisualizer

from app.services.dataset_service import ProjectSession


class VisualizationService:
    def feature_importance(self, session: ProjectSession) -> list[dict[str, Any]] | None:
        if session.model_trainer is None:
            return None

        importance = session.model_trainer.get_feature_importance()
        if importance is None:
            return None
        return importance.to_dict(orient="records")

    def available_numeric_columns(self, session: ProjectSession) -> list[str]:
        return session.processed_data.select_dtypes(include=["number"]).columns.tolist()

    def available_categorical_columns(self, session: ProjectSession) -> list[str]:
        return session.processed_data.select_dtypes(include=["object", "category"]).columns.tolist()

    def build_missing_values_figure(
        self,
        session: ProjectSession,
    ) -> dict[str, Any] | None:
        figure = DataVisualizer.plot_missing_values(session.processed_data)
        return self._serialize_figure(figure)

    def build_correlation_figure(
        self,
        session: ProjectSession,
    ) -> dict[str, Any] | None:
        figure = DataVisualizer.plot_correlation_heatmap(session.processed_data)
        return self._serialize_figure(figure)

    def build_distribution_figure(
        self,
        session: ProjectSession,
        column: str,
    ) -> dict[str, Any] | None:
        if column not in session.processed_data.columns:
            return None
        figure = DataVisualizer.plot_distribution(session.processed_data, column)
        return self._serialize_figure(figure)

    def build_boxplot_figure(
        self,
        session: ProjectSession,
        column: str,
    ) -> dict[str, Any] | None:
        if column not in session.processed_data.columns:
            return None
        figure = DataVisualizer.plot_boxplot(session.processed_data, column)
        return self._serialize_figure(figure)

    def build_countplot_figure(
        self,
        session: ProjectSession,
        column: str,
    ) -> dict[str, Any] | None:
        if column not in session.processed_data.columns:
            return None
        figure = DataVisualizer.plot_countplot(session.processed_data, column)
        return self._serialize_figure(figure)

    def build_scatter_figure(
        self,
        session: ProjectSession,
        x_col: str,
        y_col: str,
        color_col: str | None = None,
    ) -> dict[str, Any] | None:
        figure = DataVisualizer.plot_scatter(
            session.processed_data,
            x_col,
            y_col,
            color_col=color_col,
        )
        return self._serialize_figure(figure)

    def build_confusion_matrix_figure(
        self,
        session: ProjectSession,
    ) -> dict[str, Any] | None:
        trainer = session.model_trainer
        if trainer is None or trainer.task_type != "classification":
            return None
        figure = DataVisualizer.plot_confusion_matrix(
            trainer.y_test,
            trainer.y_pred,
            labels=getattr(trainer.model, "classes_", None),
        )
        return self._serialize_figure(figure)

    def build_roc_curve_figure(
        self,
        session: ProjectSession,
    ) -> dict[str, Any] | None:
        trainer = session.model_trainer
        if (
            trainer is None
            or trainer.task_type != "classification"
            or trainer.y_pred_proba is None
        ):
            return None
        classes = list(getattr(trainer.model, "classes_", trainer.y_test.unique().tolist()))
        figure = DataVisualizer.plot_roc_curve(
            trainer.y_test,
            trainer.y_pred_proba,
            classes,
        )
        return self._serialize_figure(figure)

    def build_actual_vs_predicted_figure(
        self,
        session: ProjectSession,
    ) -> dict[str, Any] | None:
        trainer = session.model_trainer
        if trainer is None or trainer.task_type != "regression":
            return None
        figure = DataVisualizer.plot_actual_vs_predicted(
            trainer.y_test,
            trainer.y_pred,
        )
        return self._serialize_figure(figure)

    def build_residuals_figure(
        self,
        session: ProjectSession,
    ) -> dict[str, Any] | None:
        trainer = session.model_trainer
        if trainer is None or trainer.task_type != "regression":
            return None
        figure = DataVisualizer.plot_residuals(trainer.y_test, trainer.y_pred)
        return self._serialize_figure(figure)

    def _serialize_figure(self, figure: Any) -> dict[str, Any] | None:
        if figure is None:
            return None
        return json.loads(pio.to_json(figure))


visualization_service = VisualizationService()
