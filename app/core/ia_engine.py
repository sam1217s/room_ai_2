# app/core/ia_engine.py
import os
import joblib
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Machine Learning
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    silhouette_score,
)
from sklearn.decomposition import PCA

# Core
from app.core.database import DatabaseManager
from app.core.config import config
from app.core.ethics_monitor import EthicsMonitor
from app.core.model_explainer import ModelExplainer

logger = logging.getLogger(__name__)


# ============================================================================
# 📊 CLASES DE DATOS
# ============================================================================
@dataclass
class ModelMetrics:
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    cross_val_mean: float = 0.0
    cross_val_std: float = 0.0
    training_time: float = 0.0
    last_training: Optional[str] = None
    model_version: str = "2.0"


# ============================================================================
# 🧠 MOTOR DE IA
# ============================================================================
class RoomMatchIAEngine:
    """
    🎯 Motor de Inteligencia Artificial RoomMatchAI v2.0
    - RandomForest + GradientBoosting + Cosine Similarity
    - Clustering KMeans + PCA
    - Explicaciones, métricas y recomendaciones
    """

    def __init__(self):
         # Logger propio
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # ML Models
        self.encoder = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.compatibility_model = None
        self.satisfaction_model = None
        self.clustering_model = None
        self.dimensionality_reducer = None

        # Estado
        self.metrics = ModelMetrics()
        self.is_trained = False
        self.feature_names = []
        self.feature_importance = {}

        # Nuevos componentes para SENASoft 2025
        self.ethics_monitor = EthicsMonitor()
        self.model_explainer = ModelExplainer()

        # Config
        self.model_config = {
            "rf_params": {
                "n_estimators": config.N_ESTIMATORS,
                "max_depth": config.MAX_DEPTH,
                "random_state": 42,
                "class_weight": "balanced",
                "n_jobs": -1,
            },
            "gb_params": {
                "n_estimators": 50,
                "learning_rate": 0.1,
                "max_depth": 6,
                "random_state": 42,
            },
            "kmeans_params": {"n_clusters": 5, "random_state": 42, "n_init": 10},
        }

    # =========================================================================
    # 🔥 OBTENER DATASET
    # =========================================================================
    def obtener_dataset(self) -> pd.DataFrame:
        db = DatabaseManager()
        data = db.obtener_todos_inquilinos()
        return pd.DataFrame(data)


    # =========================================================================
    # 🚀 ENTRENAMIENTO
    # =========================================================================
    def entrenar_modelo_completo(self) -> Dict:
        """Entrena el modelo híbrido completo usando la BD - VERSIÓN MEJORADA"""
        df = self.obtener_dataset()
        if df.empty:
            return {"error": "No hay datos suficientes"}

        start_time = datetime.now()
        logger.info(f"📊 Dataset cargado: {len(df)} registros")

        # Preparar datos
        X, y, feature_names = self._preparar_datos(df)
        self.feature_names = feature_names

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=config.TEST_SIZE, random_state=42, stratify=y
        )

        # Modelos
        self._entrenar_compatibility_model(X_train, y_train)
        self._entrenar_satisfaction_model(X_train, y_train)
        self._entrenar_encoder(df)
        self._entrenar_clustering(X)
        self._entrenar_dimensionality_reduction(X)

        # Evaluar
        self._evaluar_modelos(X_test, y_test, X, y)

        # **NUEVO: Configurar componentes de explicabilidad y ética**
        self.model_explainer.model = self.compatibility_model
        self.model_explainer.feature_names = self.feature_names
        self.model_explainer.initialize_explainer(X_train)

        # **NUEVO: Análisis de sesgos post-entrenamiento**
        sensitive_features = {}
        if 'genero' in df.columns:
            sensitive_features['genero'] = df['genero'].values
        if 'edad' in df.columns:
            age_groups = pd.cut(df['edad'], bins=[0, 25, 35, 100], labels=['<25', '25-35', '>35'])
            sensitive_features['grupo_edad'] = age_groups.astype(str).values

        y_pred = self.compatibility_model.predict(X)
        bias_analysis = self.ethics_monitor.analyze_bias(y, y_pred, sensitive_features)

        # Guardar
        self._guardar_modelos()

        self.is_trained = True
        self.metrics.training_time = (datetime.now() - start_time).total_seconds()
        self.metrics.last_training = datetime.now().isoformat()

        # **NUEVO: Incluir métricas de ética en el resultado**
        result = self._get_metrics_dict()
        result['ethics_analysis'] = bias_analysis
        result['explainability_ready'] = True
        result['privacy_compliant'] = not self.ethics_monitor.privacy_check(df).get('pii_detected', False)

        return result

    def _preparar_datos(
        self, df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepara features y labels"""
        feature_cols = [
            col for col in df.columns if col not in ["_id", "id_inquilino", "nombre", "created_at"]
        ]
        if not feature_cols:
            raise ValueError("No hay columnas válidas para entrenar")

        X = df[feature_cols].fillna("desconocido").astype(str)

        # OneHot
        if self.encoder is None:
            self.encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
            X_encoded = self.encoder.fit_transform(X)
        else:
            X_encoded = self.encoder.transform(X)

        # Escalado
        X_scaled = self.scaler.fit_transform(X_encoded)

        # Labels → basado en campo compatible o reglas
        if "compatible" in df.columns:
            y = df["compatible"].astype(int).values
        else:
            y = self._generar_labels_reglas(df)

        feature_names = self.encoder.get_feature_names_out(feature_cols).tolist()
        return X_scaled, y, feature_names

    def _generar_labels_reglas(self, df: pd.DataFrame) -> np.ndarray:
        """Genera etiquetas basadas en reglas simples"""
        labels = []
        for _, row in df.iterrows():
            score = 0
            if str(row.get("fumador", "")).lower() == "no":
                score += 1
            if str(row.get("orden", "")).lower() == "ordenada":
                score += 1
            if str(row.get("mascotas", "")).lower() == "sin mascotas":
                score += 1
            labels.append(1 if score >= 2 else 0)
        return np.array(labels)

    # =========================================================================
    # 🗃️ ENTRENAR SUB-MODELOS
    # =========================================================================
    def _entrenar_compatibility_model(self, X_train, y_train):
        self.compatibility_model = RandomForestClassifier(**self.model_config["rf_params"])
        self.compatibility_model.fit(X_train, y_train)
        self.feature_importance = dict(
            zip(self.feature_names, self.compatibility_model.feature_importances_)
        )

    def _entrenar_satisfaction_model(self, X_train, y_train):
        self.satisfaction_model = GradientBoostingClassifier(**self.model_config["gb_params"])
        self.satisfaction_model.fit(X_train, y_train)

    def _entrenar_encoder(self, df: pd.DataFrame):
        feature_cols = [
            col for col in df.columns if col not in ["_id", "id_inquilino", "nombre", "created_at"]
        ]
        X = df[feature_cols].fillna("desconocido").astype(str)
        if self.encoder is None:
            self.encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
            self.encoder.fit(X)

    def _entrenar_clustering(self, X: np.ndarray):
        self.clustering_model = KMeans(**self.model_config["kmeans_params"])
        self.clustering_model.fit(X)

    def _entrenar_dimensionality_reduction(self, X: np.ndarray):
        self.dimensionality_reducer = PCA(n_components=2, random_state=42)
        self.dimensionality_reducer.fit(X)

    def _evaluar_modelos(self, X_test, y_test, X_full, y_full):
        y_pred = self.compatibility_model.predict(X_test)
        self.metrics.accuracy = accuracy_score(y_test, y_pred)
        self.metrics.precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        self.metrics.recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        self.metrics.f1_score = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        cv_scores = cross_val_score(self.compatibility_model, X_full, y_full, cv=config.CV_FOLDS)
        self.metrics.cross_val_mean = cv_scores.mean()
        self.metrics.cross_val_std = cv_scores.std()

    # =========================================================================
    # 🔮 COMPATIBILIDAD
    # =========================================================================
    def calcular_compatibilidad_avanzada(
        self, id1: int, id2: int, df: pd.DataFrame
    ) -> Dict:
        try:
            row1 = df[df["id_inquilino"] == id1].iloc[0]
            row2 = df[df["id_inquilino"] == id2].iloc[0]

            similitud = self._calcular_similitud_coseno(row1, row2, df)
            pred_ml = self._predecir_satisfaccion(row1, row2)

            compat = (0.5 * similitud + 0.5 * pred_ml) * 100
            compat = max(10.0, min(95.0, compat))

            return {
                "compatibilidad_porcentaje": round(compat, 1),
                "similitud_coseno": round(similitud * 100, 1),
                "prediccion_satisfaccion": round(pred_ml * 100, 1),
                "recomendacion": "✅ Buena combinación" if compat >= 60 else "⚠️ Poca compatibilidad",
            }
        except Exception as e:
            logger.error(f"Error compatibilidad: {e}")
            return {"error": str(e)}

    def _calcular_similitud_coseno(self, row1, row2, df) -> float:
        if not self.encoder:
            return 0.5
        feature_cols = [
            col for col in df.columns if col not in ["_id", "id_inquilino", "nombre", "created_at"]
        ]
        X = df[feature_cols].fillna("desconocido").astype(str)
        X_encoded = self.encoder.transform(X)

        idx1 = row1.name
        idx2 = row2.name
        return cosine_similarity([X_encoded[idx1]], [X_encoded[idx2]])[0][0]

    def _predecir_satisfaccion(self, row1, row2) -> float:
        if not self.compatibility_model:
            return 0.5
        feature_cols = [
            col for col in row1.index if col not in ["_id", "id_inquilino", "nombre", "created_at"]
        ]
        df_temp = pd.DataFrame([row1[feature_cols], row2[feature_cols]])
        X_enc = self.encoder.transform(df_temp.fillna("desconocido").astype(str))
        combined = X_enc.mean(axis=0)
        combined_scaled = self.scaler.transform([combined])[0]
        prob = self.compatibility_model.predict_proba([combined_scaled])[0][-1]
        return float(prob)

    # =========================================================================
    # 💾 MODELOS
    # =========================================================================
    def _guardar_modelos(self) -> bool:
        try:
            os.makedirs(config.MODEL_PATH, exist_ok=True)
            models = {
                "encoder.pkl": self.encoder,
                "scaler.pkl": self.scaler,
                "compatibility_model.pkl": self.compatibility_model,
                "satisfaction_model.pkl": self.satisfaction_model,
                "clustering_model.pkl": self.clustering_model,
                "dimensionality_reducer.pkl": self.dimensionality_reducer,
            }
            for filename, model in models.items():
                if model is not None:
                    joblib.dump(model, os.path.join(config.MODEL_PATH, filename))

            metadata = {
                "metrics": self._get_metrics_dict(),
                "feature_names": self.feature_names,
                "feature_importance": self.feature_importance,
                "is_trained": self.is_trained,
            }
            with open(os.path.join(config.MODEL_PATH, "metadata.json"), "w") as f:
                json.dump(metadata, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error guardando modelos: {e}")
            return False

    def cargar_modelos(self) -> bool:
        try:
            model_path = config.MODEL_PATH

            # Nuevo formato (archivos separados)
            encoder_path = os.path.join(model_path, "encoder.pkl")
            modelo_path = os.path.join(model_path, "compatibility_model.pkl")

            if os.path.exists(encoder_path) and os.path.exists(modelo_path):
                self.encoder = joblib.load(encoder_path)
                self.compatibility_model = joblib.load(modelo_path)

    # Restaurar metadata
            metadata_path = os.path.join(model_path, "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
                    self.feature_names = metadata.get("feature_names", [])
                    self.feature_importance = metadata.get("feature_importance", {})
                    metricas_dict = metadata.get("metrics", {})
                    self.metrics = ModelMetrics(
                    accuracy=metricas_dict.get("accuracy", 0.0),
                    precision=metricas_dict.get("precision", 0.0),
                    recall=metricas_dict.get("recall", 0.0),
                    f1_score=metricas_dict.get("f1_score", 0.0),
                    cross_val_mean=metricas_dict.get("cross_val_mean", 0.0),
                    cross_val_std=metricas_dict.get("cross_val_std", 0.0),
                    training_time=metricas_dict.get("training_time", 0.0),
                    last_training=metricas_dict.get("last_training"),
                )

                self.is_trained = True
                self.logger.info("✅ Modelos cargados en formato nuevo con metadata")
                return True


            # 🔄 Compatibilidad retro con modelo.pkl
            legacy_path = os.path.join(model_path, "modelo.pkl")
            if os.path.exists(legacy_path):
                paquete = joblib.load(legacy_path)
                self.compatibility_model = paquete.get("modelo")
                self.encoder = None
                self.feature_names = paquete.get("features", [])

                # 🔧 Normalizamos metricas: siempre usar ModelMetrics
                metricas_dict = paquete.get("metricas", {})
                if isinstance(metricas_dict, dict):
                    self.metrics = ModelMetrics(
                        accuracy=metricas_dict.get("accuracy", 0.0),
                        precision=metricas_dict.get("precision", 0.0),
                        recall=metricas_dict.get("recall", 0.0),
                        f1_score=metricas_dict.get("f1_score", 0.0),
                        cross_val_mean=metricas_dict.get("cross_val", 0.0),
                        cross_val_std=0.0,
                    )
                else:
                    self.metrics = ModelMetrics()

                self.is_trained = True
                self.logger.info("✅ Modelo cargado desde modelo.pkl (formato antiguo)")
                return True

            self.logger.warning("⚠️ No se encontró modelo entrenado")
            return False

        except Exception as e:
            self.logger.error(f"❌ Error cargando modelo: {e}")
            return False


    # =========================================================================
    # 📊 MÉTRICAS
    # =========================================================================
    def obtener_metricas_modelo(self) -> Dict:
        return self._get_metrics_dict()

    def _get_metrics_dict(self) -> Dict:
        return {
            "accuracy": self.metrics.accuracy,
            "precision": self.metrics.precision,
            "recall": self.metrics.recall,
            "f1_score": self.metrics.f1_score,
            "cross_val_mean": self.metrics.cross_val_mean,
            "cross_val_std": self.metrics.cross_val_std,
            "training_time": self.metrics.training_time,
            "last_training": self.metrics.last_training,
            "is_trained": self.is_trained,
        }

    # =========================================================================
    # 🛡️ NUEVOS MÉTODOS PARA SENASOFT 2025
    # =========================================================================
    
    def obtener_explicacion_prediccion(self, inquilino_data: Dict) -> Dict:
        """
        Obtiene explicación detallada de una predicción
        """
        try:
            if not self.is_trained:
                return {'error': 'Modelo no entrenado'}
                
            # Preparar datos para predicción
            df_temp = pd.DataFrame([inquilino_data])
            feature_cols = [col for col in df_temp.columns if col not in ["_id", "id_inquilino", "nombre", "created_at"]]
            X_temp = df_temp[feature_cols].fillna("desconocido").astype(str)
            
            if self.encoder:
                X_encoded = self.encoder.transform(X_temp)
                X_scaled = self.scaler.transform(X_encoded)
                
                # Configurar explainer si no está listo
                if self.model_explainer.model is None:
                    self.model_explainer.model = self.compatibility_model
                    self.model_explainer.feature_names = self.feature_names
                    
                # Obtener explicación
                explicacion = self.model_explainer.explain_prediction(X_scaled[0], inquilino_data)
                return explicacion
            else:
                return {'error': 'Encoder no disponible'}
                
        except Exception as e:
            logger.error(f"Error obteniendo explicación: {e}")
            return {'error': str(e)}

    def analizar_sesgos_modelo(self, df: pd.DataFrame = None) -> Dict:
        """
        Analiza sesgos del modelo en el dataset actual
        """
        try:
            if df is None:
                df = self.obtener_dataset()
                
            if df.empty or not self.is_trained:
                return {'error': 'Sin datos o modelo no entrenado'}
                
            # Preparar datos para análisis
            X, y, _ = self._preparar_datos(df)
            y_pred = self.compatibility_model.predict(X)
            
            # Características sensibles para análisis de sesgos
            sensitive_features = {}
            if 'genero' in df.columns:
                sensitive_features['genero'] = df['genero'].values
            if 'edad' in df.columns:
                # Crear grupos etarios
                age_groups = pd.cut(df['edad'], bins=[0, 25, 35, 100], labels=['<25', '25-35', '>35'])
                sensitive_features['grupo_edad'] = age_groups.astype(str).values
                
            # Análisis de sesgos
            bias_report = self.ethics_monitor.analyze_bias(y, y_pred, sensitive_features)
            
            return {
                'bias_analysis': bias_report,
                'recommendation': 'Revisar algoritmo si bias_detected=True' if bias_report.get('bias_detected') else 'Modelo dentro de umbrales éticos',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de sesgos: {e}")
            return {'error': str(e)}

    def obtener_metricas_eticas(self) -> Dict:
        """
        Obtiene métricas éticas actuales del modelo
        """
        try:
            df = self.obtener_dataset()
            if df.empty:
                return {'error': 'Sin datos para calcular métricas éticas'}
                
            bias_analysis = self.analizar_sesgos_modelo(df)
            privacy_check = self.ethics_monitor.privacy_check(df)
            
            ethics_score = 100.0
            if bias_analysis.get('bias_analysis', {}).get('bias_detected', False):
                ethics_score -= 30.0
                
            if privacy_check.get('pii_detected', False):
                ethics_score -= 20.0
                
            return {
                'ethics_score': max(0.0, ethics_score),
                'bias_status': 'detected' if bias_analysis.get('bias_analysis', {}).get('bias_detected') else 'clear',
                'privacy_score': privacy_check.get('anonymization_score', 1.0) * 100,
                'overall_compliance': ethics_score >= 80.0,
                'recommendations': bias_analysis.get('bias_analysis', {}).get('recommendations', [])
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas éticas: {e}")
            return {'error': str(e)}

    def explicar_compatibilidad_detallada(self, id1: int, id2: int, df: pd.DataFrame = None) -> Dict:
        """
        Explicación detallada de compatibilidad entre dos inquilinos
        """
        try:
            if df is None:
                df = self.obtener_dataset()
                
            # Configurar explainer
            if self.model_explainer.feature_names != self.feature_names:
                self.model_explainer.feature_names = self.feature_names
                
            # Obtener explicación de compatibilidad
            compatibility_explanation = self.model_explainer.explain_compatibility_factors(id1, id2, df)
            
            # Agregar predicción de compatibilidad estándar
            standard_compatibility = self.calcular_compatibilidad_avanzada(id1, id2, df)
            
            return {
                'detailed_explanation': compatibility_explanation,
                'ml_prediction': standard_compatibility,
                'recommendation_confidence': 'high' if standard_compatibility.get('compatibilidad_porcentaje', 0) > 70 else 'medium'
            }
            
        except Exception as e:
            logger.error(f"Error en explicación detallada: {e}")
            return {'error': str(e)}


# ============================================================================
# FACTORY
# ============================================================================
def MotorIA() -> RoomMatchIAEngine:
    motor = RoomMatchIAEngine()
    if motor.cargar_modelos():
        logger.info("✅ Motor IA inicializado con modelos pre-entrenados")
    else:
        logger.warning("⚠️ Motor IA sin modelos. Ejecutar entrenamiento.")
    return motor

