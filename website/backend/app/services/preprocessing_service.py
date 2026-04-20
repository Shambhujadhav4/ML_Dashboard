from __future__ import annotations

from modules.preprocessing import DataPreprocessor

from app.schemas.preprocess import (
    DropColumnsRequest,
    EncodeRequest,
    MissingValuesRequest,
    OutlierRequest,
    ScaleRequest,
)
from app.services.dataset_service import ProjectSession, dataset_store


class PreprocessingService:
    def drop_columns(self, session: ProjectSession, request: DropColumnsRequest) -> ProjectSession:
        processor = DataPreprocessor(session.processed_data)
        session.processed_data = processor.drop_columns(request.columns)
        session.preprocessing_log.append(f"Dropped columns: {request.columns}")
        dataset_store.clear_model_state(session)
        return session

    def handle_missing_values(
        self,
        session: ProjectSession,
        request: MissingValuesRequest,
    ) -> ProjectSession:
        processor = DataPreprocessor(session.processed_data)
        columns = request.columns or None
        session.processed_data = processor.handle_missing_values(
            request.strategy,
            columns,
            request.fill_value,
        )
        session.preprocessing_log.append(
            f"Missing values -> {request.strategy} on {columns or 'all columns'}"
        )
        dataset_store.clear_model_state(session)
        return session

    def encode(self, session: ProjectSession, request: EncodeRequest) -> ProjectSession:
        processor = DataPreprocessor(session.processed_data)
        columns = request.columns or None
        session.processed_data = processor.encode_categorical(request.method, columns)
        session.preprocessing_log.append(
            f"Encoding -> {request.method} on {columns or 'all categorical'}"
        )
        dataset_store.clear_model_state(session)
        return session

    def scale(self, session: ProjectSession, request: ScaleRequest) -> ProjectSession:
        processor = DataPreprocessor(session.processed_data)
        columns = request.columns or None
        session.processed_data = processor.scale_features(request.method, columns)
        session.preprocessing_log.append(
            f"Scaling -> {request.method} on {columns or 'all numeric'}"
        )
        dataset_store.clear_model_state(session)
        return session

    def handle_outliers(self, session: ProjectSession, request: OutlierRequest) -> ProjectSession:
        processor = DataPreprocessor(session.processed_data)
        columns = request.columns or None
        session.processed_data = processor.handle_outliers(
            request.method,
            columns,
            request.threshold,
        )
        session.preprocessing_log.append(
            f"Outliers -> {request.method} on {columns or 'all numeric'}"
        )
        dataset_store.clear_model_state(session)
        return session


preprocessing_service = PreprocessingService()
