# app/core/ethics_monitor.py
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import logging
from sklearn.metrics import confusion_matrix
from fairlearn.metrics import MetricFrame, selection_rate
from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference

logger = logging.getLogger(__name__)

class EthicsMonitor:
    """
    Monitor de ética y sesgos para RoomMatchAI
    Garantiza equidad y transparencia en las predicciones
    """
    
    def __init__(self):
        self.bias_thresholds = {
            'demographic_parity': 0.1,  # Max 10% diferencia entre grupos
            'equalized_odds': 0.1,
            'selection_rate': 0.15
        }
        
    def analyze_bias(self, y_true: np.ndarray, y_pred: np.ndarray, 
                     sensitive_features: Dict[str, np.ndarray]) -> Dict:
        """
        Analiza sesgos en predicciones por grupos demográficos
        """
        bias_report = {
            'overall_accuracy': (y_true == y_pred).mean(),
            'groups_analysis': {},
            'bias_detected': False,
            'recommendations': []
        }
        
        for feature_name, feature_values in sensitive_features.items():
            try:
                # Demographic Parity
                dp_diff = demographic_parity_difference(
                    y_true, y_pred, sensitive_features=feature_values
                )
                
                # Equalized Odds
                eo_diff = equalized_odds_difference(
                    y_true, y_pred, sensitive_features=feature_values
                )
                
                # Selection Rate por grupo
                unique_groups = np.unique(feature_values)
                selection_rates = {}
                
                for group in unique_groups:
                    mask = feature_values == group
                    if np.sum(mask) > 0:
                        selection_rates[str(group)] = np.mean(y_pred[mask])
                
                # Análisis por grupo
                group_analysis = {
                    'demographic_parity_diff': float(dp_diff),
                    'equalized_odds_diff': float(eo_diff),
                    'selection_rates': selection_rates,
                    'bias_detected': abs(dp_diff) > self.bias_thresholds['demographic_parity']
                }
                
                bias_report['groups_analysis'][feature_name] = group_analysis
                
                # Detectar sesgos significativos
                if abs(dp_diff) > self.bias_thresholds['demographic_parity']:
                    bias_report['bias_detected'] = True
                    bias_report['recommendations'].append(
                        f"Sesgo detectado en {feature_name}: diferencia {dp_diff:.3f}"
                    )
                    
            except Exception as e:
                logger.error(f"Error analizando sesgo en {feature_name}: {e}")
                
        return bias_report
    
    def privacy_check(self, data: pd.DataFrame) -> Dict:
        """
        Verifica cumplimiento de privacidad de datos
        """
        privacy_report = {
            'pii_detected': False,
            'anonymization_score': 0.0,
            'issues': [],
            'recommendations': []
        }
        
        # Campos sensibles a verificar
        sensitive_fields = ['nombre', 'telefono', 'email', 'direccion', 'cedula']
        
        for field in sensitive_fields:
            if field in data.columns:
                privacy_report['pii_detected'] = True
                privacy_report['issues'].append(f"Campo sensible detectado: {field}")
                
        # Score de anonimización (simplificado)
        total_fields = len(data.columns)
        sensitive_count = len([f for f in sensitive_fields if f in data.columns])
        privacy_report['anonymization_score'] = 1.0 - (sensitive_count / total_fields)
        
        # Recomendaciones
        if privacy_report['pii_detected']:
            privacy_report['recommendations'].extend([
                "Anonimizar o encriptar campos sensibles",
                "Implementar hash para identificadores únicos",
                "Considerar técnicas de differential privacy"
            ])
            
        return privacy_report
    
    def generate_ethics_report(self, model, X: np.ndarray, y: np.ndarray, 
                              demographics: Dict[str, np.ndarray]) -> Dict:
        """
        Genera reporte completo de ética del modelo
        """
        y_pred = model.predict(X)
        
        # Análisis de sesgos
        bias_analysis = self.analyze_bias(y, y_pred, demographics)
        
        # Métricas de equidad
        equity_metrics = self._calculate_equity_metrics(y, y_pred, demographics)
        
        # Distribución de predicciones
        prediction_distribution = self._analyze_prediction_distribution(y_pred, demographics)
        
        ethics_report = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'model_version': getattr(model, 'version', 'unknown'),
            'bias_analysis': bias_analysis,
            'equity_metrics': equity_metrics,
            'prediction_distribution': prediction_distribution,
            'overall_ethics_score': self._calculate_ethics_score(bias_analysis, equity_metrics),
            'action_required': bias_analysis['bias_detected']
        }
        
        return ethics_report
    
    def _calculate_equity_metrics(self, y_true: np.ndarray, y_pred: np.ndarray,
                                 demographics: Dict[str, np.ndarray]) -> Dict:
        """Calcula métricas de equidad detalladas"""
        equity_metrics = {}
        
        for feature_name, feature_values in demographics.items():
            try:
                # Usar MetricFrame de fairlearn
                mf = MetricFrame(
                    metrics={'accuracy': lambda y_t, y_p: (y_t == y_p).mean(),
                           'selection_rate': lambda y_t, y_p: y_p.mean()},
                    y_true=y_true,
                    y_pred=y_pred,
                    sensitive_features=feature_values
                )
                
                equity_metrics[feature_name] = {
                    'by_group': mf.by_group.to_dict(),
                    'overall': mf.overall.to_dict(),
                    'difference': mf.difference().to_dict()
                }
                
            except Exception as e:
                logger.error(f"Error calculando métricas de equidad para {feature_name}: {e}")
                
        return equity_metrics
    
    def _analyze_prediction_distribution(self, y_pred: np.ndarray, 
                                       demographics: Dict[str, np.ndarray]) -> Dict:
        """Analiza distribución de predicciones por grupos demográficos"""
        distribution = {}
        
        for feature_name, feature_values in demographics.items():
            unique_groups = np.unique(feature_values)
            group_distributions = {}
            
            for group in unique_groups:
                mask = feature_values == group
                group_pred = y_pred[mask]
                
                group_distributions[str(group)] = {
                    'count': int(np.sum(mask)),
                    'positive_rate': float(np.mean(group_pred)),
                    'predictions': {
                        '0': int(np.sum(group_pred == 0)),
                        '1': int(np.sum(group_pred == 1))
                    }
                }
                
            distribution[feature_name] = group_distributions
            
        return distribution
    
    def _calculate_ethics_score(self, bias_analysis: Dict, equity_metrics: Dict) -> float:
        """
        Calcula score general de ética (0-100)
        100 = Sin sesgos detectados, distribución equitativa
        """
        base_score = 100.0
        
        # Penalizar sesgos detectados
        if bias_analysis['bias_detected']:
            base_score -= 30.0
            
        # Penalizar por número de recomendaciones
        recommendation_penalty = len(bias_analysis.get('recommendations', [])) * 5
        base_score -= recommendation_penalty
        
        # Bonificar alta precisión general
        accuracy_bonus = bias_analysis.get('overall_accuracy', 0) * 20
        base_score += accuracy_bonus
        
        return max(0.0, min(100.0, base_score))
    
    def monitor_model_predictions(self, predictions: List[Dict], 
                                 demographics: List[Dict]) -> Dict:
        """
        Monitorea predicciones en tiempo real para detectar sesgos emergentes
        """
        if len(predictions) != len(demographics):
            return {'error': 'Longitudes de predicciones y demografía no coinciden'}
            
        # Convertir a arrays numpy
        y_pred = np.array([p['prediction'] for p in predictions])
        
        demo_features = {}
        if demographics:
            demo_keys = demographics[0].keys()
            for key in demo_keys:
                demo_features[key] = np.array([d.get(key, 'unknown') for d in demographics])
                
        # Análisis simplificado para tiempo real
        monitoring_report = {
            'total_predictions': len(predictions),
            'positive_rate': float(np.mean(y_pred)),
            'timestamp': pd.Timestamp.now().isoformat(),
            'alerts': []
        }
        
        # Verificar rates por grupo
        for feature_name, feature_values in demo_features.items():
            unique_groups = np.unique(feature_values)
            if len(unique_groups) > 1:
                group_rates = {}
                for group in unique_groups:
                    mask = feature_values == group
                    if np.sum(mask) > 0:
                        group_rates[str(group)] = np.mean(y_pred[mask])
                        
                # Detectar diferencias significativas
                rates_values = list(group_rates.values())
                if max(rates_values) - min(rates_values) > 0.15:
                    monitoring_report['alerts'].append(
                        f"Diferencia significativa en {feature_name}: {group_rates}"
                    )
                    
        return monitoring_report