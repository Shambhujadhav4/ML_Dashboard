from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.schemas.results import ModelRecommendation, WorkflowRecommendation
from app.services.dataset_service import ProjectSession


@dataclass
class _BenchmarkModel:
    name: str
    estimator: object


class RecommendationService:
    TARGET_HINTS = {"target", "label", "class", "y", "output", "result", "outcome"}
    CLASSIFICATION_BENCHMARK_METRICS = ["f1_weighted", "accuracy"]
    REGRESSION_BENCHMARK_METRICS = ["r2"]

    CLASSIFICATION_MODELS = [
        _BenchmarkModel("Logistic Regression", LogisticRegression(max_iter=1000, random_state=42)),
        _BenchmarkModel("Random Forest", RandomForestClassifier(n_estimators=120, random_state=42)),
        _BenchmarkModel("Gradient Boosting", GradientBoostingClassifier(random_state=42)),
    ]

    REGRESSION_MODELS = [
        _BenchmarkModel("Ridge Regression", Ridge(random_state=42)),
        _BenchmarkModel("Random Forest", RandomForestRegressor(n_estimators=120, random_state=42)),
        _BenchmarkModel("Gradient Boosting", GradientBoostingRegressor(random_state=42)),
    ]

    def _is_categorical_like(self, series: pd.Series) -> bool:
        return bool(
            pd.api.types.is_object_dtype(series)
            or pd.api.types.is_string_dtype(series)
            or isinstance(series.dtype, pd.CategoricalDtype)
        )

    def recommend(
        self,
        session: ProjectSession,
        benchmark_metric: str | None = None,
    ) -> WorkflowRecommendation:
        df = session.processed_data.copy()

        if session.input_kind != "csv":
            return WorkflowRecommendation(
                project_id=session.project_id,
                notes=[
                    "Workflow recommendation is available for CSV datasets only.",
                    "Upload a tabular CSV with a target column for model benchmarking.",
                ],
            )

        if df.shape[0] < 12 or df.shape[1] < 2:
            return WorkflowRecommendation(
                project_id=session.project_id,
                notes=[
                    "Dataset is too small for reliable model recommendation.",
                    "Try at least 12 rows and at least 2 columns.",
                ],
            )

        target_column = self._select_target_column(df)
        if target_column is None:
            return WorkflowRecommendation(
                project_id=session.project_id,
                notes=["Could not infer a target column from this dataset."],
            )

        feature_columns = [column for column in df.columns if column != target_column]
        if not feature_columns:
            return WorkflowRecommendation(
                project_id=session.project_id,
                recommended_target_column=target_column,
                notes=["No feature columns remain after target selection."],
            )

        task_type = self._infer_task_type(df[target_column])
        suggested_steps = self._suggest_workflow_steps(df, feature_columns)
        available_metrics = (
            self.CLASSIFICATION_BENCHMARK_METRICS
            if task_type == "classification"
            else self.REGRESSION_BENCHMARK_METRICS
        )
        selected_metric, metric_note = self._resolve_benchmark_metric(
            task_type,
            benchmark_metric,
        )
        candidate_models, notes = self._benchmark_models(
            df,
            feature_columns,
            target_column,
            task_type,
            selected_metric,
            available_metrics,
        )
        if metric_note:
            notes.append(metric_note)

        best_model = candidate_models[0] if candidate_models else None
        if best_model is None:
            notes.append("No model could be benchmarked successfully on this dataset.")

        return WorkflowRecommendation(
            project_id=session.project_id,
            recommended_task_type=task_type,
            recommended_target_column=target_column,
            benchmark_metric=selected_metric,
            available_benchmark_metrics=available_metrics,
            best_model=best_model,
            candidate_models=candidate_models,
            suggested_preprocessing_steps=suggested_steps,
            notes=notes,
        )

    def _resolve_benchmark_metric(self, task_type: str, requested: str | None) -> tuple[str, str | None]:
        available = (
            self.CLASSIFICATION_BENCHMARK_METRICS
            if task_type == "classification"
            else self.REGRESSION_BENCHMARK_METRICS
        )
        default_metric = available[0]
        if not requested:
            return default_metric, None
        requested_clean = requested.strip().lower()
        if requested_clean in available:
            return requested_clean, None
        return default_metric, f"Unsupported benchmark metric '{requested}'. Using '{default_metric}'."

    def _select_target_column(self, df: pd.DataFrame) -> str | None:
        lowered = {str(column).strip().lower(): str(column) for column in df.columns}
        for hint in self.TARGET_HINTS:
            if hint in lowered:
                return lowered[hint]
        if len(df.columns):
            return str(df.columns[-1])
        return None

    def _infer_task_type(self, target: pd.Series) -> str:
        if pd.api.types.is_numeric_dtype(target):
            unique_count = int(target.nunique(dropna=True))
            ratio = unique_count / max(1, len(target))
            if unique_count <= 12 or ratio <= 0.12:
                return "classification"
            return "regression"
        return "classification"

    def _suggest_workflow_steps(self, df: pd.DataFrame, feature_columns: list[str]) -> list[str]:
        steps: list[str] = []

        if int(df.isnull().sum().sum()) > 0:
            steps.append("Handle missing values (median for numeric, mode for categorical).")

        categorical_cols = [
            col
            for col in feature_columns
            if self._is_categorical_like(df[col])
        ]
        numeric_cols = [col for col in feature_columns if col not in categorical_cols]

        if categorical_cols:
            steps.append("Encode categorical features with one-hot encoding.")

        if numeric_cols:
            steps.append("Scale numeric features for distance-based and linear models.")

        if int(df.duplicated().sum()) > 0:
            steps.append("Remove or review duplicate rows before final training.")

        if not steps:
            steps.append("Dataset looks clean. You can proceed directly to model training.")

        return steps

    def _build_preprocessor(self, df: pd.DataFrame, feature_columns: list[str]) -> ColumnTransformer:
        categorical_cols = [
            col
            for col in feature_columns
            if self._is_categorical_like(df[col])
        ]
        numeric_cols = [col for col in feature_columns if col not in categorical_cols]

        transformers = []
        if numeric_cols:
            transformers.append(
                (
                    "num",
                    Pipeline(
                        steps=[
                            ("imputer", SimpleImputer(strategy="median")),
                            ("scaler", StandardScaler()),
                        ]
                    ),
                    numeric_cols,
                )
            )

        if categorical_cols:
            transformers.append(
                (
                    "cat",
                    Pipeline(
                        steps=[
                            ("imputer", SimpleImputer(strategy="most_frequent")),
                            (
                                "encoder",
                                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                            ),
                        ]
                    ),
                    categorical_cols,
                )
            )

        return ColumnTransformer(transformers=transformers)

    def _classification_cv(self, y: pd.Series) -> tuple[StratifiedKFold | KFold, list[str]]:
        notes: list[str] = []
        class_counts = y.value_counts(dropna=True)
        min_count = int(class_counts.min()) if not class_counts.empty else 0
        if min_count >= 2:
            folds = max(2, min(5, min_count))
            return StratifiedKFold(n_splits=folds, shuffle=True, random_state=42), notes

        notes.append("Class distribution is very sparse; using non-stratified validation.")
        folds = max(2, min(5, len(y)))
        return KFold(n_splits=folds, shuffle=True, random_state=42), notes

    def _benchmark_models(
        self,
        df: pd.DataFrame,
        feature_columns: list[str],
        target_column: str,
        task_type: str,
        benchmark_metric: str,
        available_metrics: list[str],
    ) -> tuple[list[ModelRecommendation], list[str]]:
        notes: list[str] = []

        data = df[feature_columns + [target_column]].dropna(subset=[target_column]).copy()
        if len(data) < 10:
            return [], ["Target column has too many missing values after filtering."]

        X = data[feature_columns]
        y = data[target_column]

        preprocessor = self._build_preprocessor(data, feature_columns)

        if task_type == "classification":
            models = self.CLASSIFICATION_MODELS
            cv, cv_notes = self._classification_cv(y)
            notes.extend(cv_notes)
        else:
            models = self.REGRESSION_MODELS
            folds = max(2, min(5, len(y)))
            cv = KFold(n_splits=folds, shuffle=True, random_state=42)

        results: list[ModelRecommendation] = []

        for model in models:
            pipeline = Pipeline(
                steps=[
                    ("preprocessor", preprocessor),
                    ("model", model.estimator),
                ]
            )
            try:
                scores = cross_val_score(pipeline, X, y, cv=cv, scoring=benchmark_metric)
            except Exception as exc:
                notes.append(f"Skipped {model.name}: {exc}")
                continue

            metric_scores = {benchmark_metric: float(scores.mean())}
            for metric in available_metrics:
                if metric == benchmark_metric:
                    continue
                try:
                    extra_scores = cross_val_score(pipeline, X, y, cv=cv, scoring=metric)
                    metric_scores[metric] = float(extra_scores.mean())
                except Exception:
                    continue

            results.append(
                ModelRecommendation(
                    model_name=model.name,
                    mean_score=float(scores.mean()),
                    std_score=float(scores.std()),
                    metric_scores=metric_scores,
                )
            )

        results.sort(key=lambda item: item.mean_score, reverse=True)
        return results[:5], notes


recommendation_service = RecommendationService()
