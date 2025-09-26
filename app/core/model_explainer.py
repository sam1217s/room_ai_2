# app/core/model_explainer.py
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import shap
import logging

logger = logging.getLogger(__name__)

class ModelExplainer:
    """
    Explica predicciones del modelo de compatibilidad
    Cumple requisitos de explicabilidad para SENASoft 2025
    """
    
    def __init__(self, model=None, feature_names: List[str] = None):
        self.model = model
        self.feature_names = feature_names or []
        self.explainer = None
        
    def initialize_explainer(self, X_train: np.ndarray):
        """Inicializa explicador SHAP"""
        if self.model is None:
            logger.warning("Modelo no disponible para explicaciones")
            return False
            
        try:
            if hasattr(self.model, 'estimators_'):
                self.explainer = shap.TreeExplainer(self.model)
            else:
                background = shap.kmeans(X_train, 10)
                self.explainer = shap.KernelExplainer(self.model.predict, background)
            logger.info("Explicador SHAP inicializado")
            return True
        except Exception as e:
            logger.error(f"Error inicializando explicador: {e}")
            return False

    def explain_prediction(self, X_instance: np.ndarray, inquilino_data: Dict = None) -> Dict:
        """Explica una predicción específica con factores positivos y negativos"""
        if self.explainer is None:
            return self._simple_explanation(X_instance, inquilino_data)

        try:
            # Normalizar SIEMPRE: convertir a 2D numpy array
            X_instance = np.array(X_instance).reshape(1, -1)

            shap_values = self.explainer.shap_values(X_instance)

            if isinstance(shap_values, list):
                shap_values = shap_values[1][0]
            else:
                shap_values = np.array(shap_values).reshape(-1)

            feature_impacts = []
            for feature, impact, value in zip(self.feature_names, shap_values, X_instance.flatten()):
                feature_impacts.append({
                    'feature': feature,
                    'impact': float(impact),
                    'direction': 'positivo' if impact > 0 else 'negativo',
                    'magnitude': abs(float(impact)),
                    'value': float(value)
                })

            feature_impacts.sort(key=lambda x: x['magnitude'], reverse=True)
            positive_factors = [f for f in feature_impacts[:5] if f['impact'] > 0]
            negative_factors = [f for f in feature_impacts[:5] if f['impact'] < 0]

            human_explanation = self._generate_human_explanation(
                positive_factors, negative_factors, inquilino_data
            )

            return {
                'prediction_confidence': float(self.model.predict_proba(X_instance)[0][1]),
                'top_positive_factors': positive_factors,
                'top_negative_factors': negative_factors,
                'all_feature_impacts': feature_impacts,
                'human_explanation': human_explanation,
                'explanation_method': 'SHAP'
            }

        except Exception as e:
            logger.error(f"Error en explicación SHAP: {e}")
            return self._simple_explanation(X_instance, inquilino_data)

    def _simple_explanation(self, X_instance: np.ndarray, inquilino_data: Dict = None) -> Dict:
        """Explicación simplificada basada en importancia de features"""
        if self.model is None:
            return {'error': 'Modelo no disponible'}

        try:
            X_instance = np.array(X_instance).reshape(1, -1)

            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
            else:
                return {'explanation_method': 'Modelo sin feature importance disponible'}

            prediction = self.model.predict(X_instance)[0]
            confidence = self.model.predict_proba(X_instance)[0].max()

            feature_rankings = []
            for feature, importance, value in zip(self.feature_names, importances, X_instance.flatten()):
                feature_rankings.append({
                    'feature': feature,
                    'importance': float(importance),
                    'value': float(value)
                })

            feature_rankings.sort(key=lambda x: x['importance'], reverse=True)

            return {
                'prediction': int(prediction),
                'prediction_confidence': float(confidence),
                'top_factors': feature_rankings[:8],
                'human_explanation': f"Predicción basada en {feature_rankings[0]['feature']} y otros factores clave",
                'explanation_method': 'Feature Importance'
            }

        except Exception as e:
            logger.error(f"Error en explicación simple: {e}")
            return {'error': str(e)}

    def _generate_human_explanation(self, positive_factors: List[Dict], 
                                    negative_factors: List[Dict],
                                    inquilino_data: Dict = None) -> str:
        """Genera explicación en lenguaje natural"""
        explanation_parts = []
        
        if len(positive_factors) > len(negative_factors):
            explanation_parts.append("🔮 La IA predice ALTA compatibilidad porque:")
        else:
            explanation_parts.append("🔮 La IA predice BAJA compatibilidad porque:")
            
        if positive_factors:
            explanation_parts.append("✅ Factores favorables:")
            for factor in positive_factors[:3]:
                feature_name = self._humanize_feature_name(factor['feature'])
                explanation_parts.append(f"   • {feature_name}")
                
        if negative_factors:
            explanation_parts.append("⚠️ Aspectos que pueden generar conflictos:")
            for factor in negative_factors[:3]:
                feature_name = self._humanize_feature_name(factor['feature'])
                explanation_parts.append(f"   • {feature_name}")
                
        explanation_parts.append("💡 Recomendación:")
        if len(positive_factors) > len(negative_factors):
            explanation_parts.append("   Es una buena combinación. Consideren establecer reglas claras de convivencia.")
        else:
            explanation_parts.append("   Hablen sobre expectativas y hábitos antes de decidir.")
            
        return "\n".join(explanation_parts)

    def _humanize_feature_name(self, feature_name: str) -> str:
        """Convierte nombres técnicos de features a lenguaje humano"""
        humanized_names = {
            'fumador_no': 'Ambos no fumadores',
            'fumador_si': 'Al menos uno fuma',
            'orden_ordenada': 'Preferencia por orden y limpieza',
            'orden_desordenada': 'Más relajados con el orden',
            'mascotas_sin mascotas': 'Sin mascotas',
            'mascotas_con mascotas': 'Con mascotas',
            'deporte_si': 'Estilo de vida activo/deportivo',
            'deporte_no': 'Menos orientados al deporte',
            'bioritmo_madrugador': 'Horarios matutinos',
            'bioritmo_nocturno': 'Horarios nocturnos',
            'visitas_si': 'Reciben visitas frecuentes',
            'visitas_no': 'Pocas visitas',
            'instrumento_si': 'Tocan algún instrumento',
            'genero_masculino': 'Género masculino',
            'genero_femenino': 'Género femenino',
            'edad': 'Compatibilidad de edad'
        }
        
        for key, value in humanized_names.items():
            if key in feature_name.lower():
                return value
                
        clean_name = feature_name.replace('_', ' ').title()
        return clean_name

    def explain_compatibility_factors(self, id1: int, id2: int, df: pd.DataFrame) -> Dict:
        """Explica factores específicos de compatibilidad entre dos inquilinos"""
        try:
            row1 = df[df['id_inquilino'] == id1].iloc[0]
            row2 = df[df['id_inquilino'] == id2].iloc[0]
            
            compatibility_factors = {
                'inquilino_1': {'id': id1, 'nombre': row1.get('nombre', 'Inquilino 1')},
                'inquilino_2': {'id': id2, 'nombre': row2.get('nombre', 'Inquilino 2')},
                'factors_comparison': [],
                'compatibility_score': 0.0,
                'summary': ''
            }
            
            key_factors = ['fumador', 'mascotas', 'orden', 'deporte', 'bioritmo', 'visitas']
            compatible_count = 0
            
            for factor in key_factors:
                if factor in row1.index and factor in row2.index:
                    val1 = row1[factor]
                    val2 = row2[factor]
                    is_compatible = val1 == val2
                    
                    compatibility_factors['factors_comparison'].append({
                        'factor': factor.title(),
                        'inquilino_1_value': str(val1),
                        'inquilino_2_value': str(val2),
                        'compatible': is_compatible,
                        'impact': 'Alto' if factor in ['fumador', 'orden', 'bioritmo'] else 'Medio'
                    })
                    
                    if is_compatible:
                        compatible_count += 1
            
            compatibility_factors['compatibility_score'] = compatible_count / len(key_factors) * 100
            
            if compatibility_factors['compatibility_score'] >= 75:
                compatibility_factors['summary'] = "🎯 Excelente compatibilidad en la mayoría de aspectos clave"
            elif compatibility_factors['compatibility_score'] >= 50:
                compatibility_factors['summary'] = "👍 Compatibilidad moderada, algunos aspectos a considerar"
            else:
                compatibility_factors['summary'] = "⚠️ Baja compatibilidad, recomendable evaluar otros candidatos"
                
            return compatibility_factors
            
        except Exception as e:
            logger.error(f"Error explicando compatibilidad: {e}")
            return {'error': str(e)}

    def generate_global_explanations(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Genera explicaciones globales del comportamiento del modelo"""
        if self.model is None:
            return {'error': 'Modelo no disponible'}
            
        try:
            global_importance = {}
            
            if hasattr(self.model, 'feature_importances_'):
                importance_scores = self.model.feature_importances_
                
                for feature, importance in zip(self.feature_names, importance_scores):
                    global_importance[feature] = {
                        'importance': float(importance),
                        'rank': 0,
                        'human_name': self._humanize_feature_name(feature)
                    }
                    
                sorted_features = sorted(global_importance.items(), 
                                         key=lambda x: x[1]['importance'], reverse=True)
                
                for rank, (feature, info) in enumerate(sorted_features, 1):
                    global_importance[feature]['rank'] = rank
            
            high_compatibility_features = []
            low_compatibility_features = []
            
            positive_samples = X[y == 1]
            negative_samples = X[y == 0]
            
            if len(positive_samples) > 0 and len(negative_samples) > 0:
                pos_means = np.mean(positive_samples, axis=0)
                neg_means = np.mean(negative_samples, axis=0)
                differences = pos_means - neg_means
                
                for i, diff in enumerate(differences):
                    if i < len(self.feature_names):
                        feature = self.feature_names[i]
                        if diff > 0.1:
                            high_compatibility_features.append({
                                'feature': feature,
                                'human_name': self._humanize_feature_name(feature),
                                'difference': float(diff)
                            })
                        elif diff < -0.1:
                            low_compatibility_features.append({
                                'feature': feature,
                                'human_name': self._humanize_feature_name(feature),
                                'difference': float(abs(diff))
                            })
            
            return {
                'global_feature_importance': global_importance,
                'high_compatibility_patterns': high_compatibility_features[:5],
                'low_compatibility_patterns': low_compatibility_features[:5],
                'model_insights': self._generate_model_insights(global_importance)
            }
            
        except Exception as e:
            logger.error(f"Error en explicación global: {e}")
            return {'error': str(e)}

    def _generate_model_insights(self, importance_dict: Dict) -> List[str]:
        """Genera insights sobre el comportamiento del modelo"""
        insights = []
        
        if not importance_dict:
            return ["No hay datos suficientes para generar insights"]
            
        top_features = sorted(importance_dict.items(), 
                              key=lambda x: x[1]['importance'], reverse=True)[:3]
        
        insights.append("🔍 Insights del Modelo de Compatibilidad:")
        
        for i, (feature, info) in enumerate(top_features, 1):
            human_name = info['human_name']
            insights.append(f"{i}. {human_name} es un factor crítico para la compatibilidad")
            
        insights.append("📋 El modelo prioriza hábitos de vida y preferencias de convivencia")
        insights.append("🎯 La precisión mejora con más datos de comportamiento")
        
        return insights
