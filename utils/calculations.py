import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class AnalyticsEngine:
    """Motor de análises estatísticas para o EmagreSim"""
    
    @staticmethod
    def calculate_bmi(weight, height_cm):
        if not weight or not height_cm: return None
        height_m = height_cm / 100
        return round(weight / (height_m ** 2), 1)
    
    @staticmethod
    def get_bmi_category(bmi):
        if bmi is None: return "N/D", ""
        if bmi < 18.5: return "Abaixo", "⚠️"
        if bmi < 24.9: return "Normal", "✅"
        if bmi < 29.9: return "Sobrepeso", "⚠️"
        return "Obesidade", ""
    
    @staticmethod
    def calculate_tmb(weight, height_cm, age, gender, activity):
        if not all([weight, height_cm, age, gender]): return None
        base = (10 * weight) + (6.25 * height_cm) - (5 * age)
        base += 5 if gender == 'M' else -161
        
        multipliers = {'Sedentario': 1.2, 'Leve': 1.375, 'Moderado': 1.55, 'Intenso': 1.725}
        return round(base * multipliers.get(activity, 1.2))
    
    @staticmethod
    def calculate_weight_trend(logs):
        """Calcula tendência de peso usando numpy"""
        df = pd.DataFrame(logs)
        df = df.dropna(subset=['weight_kg']).sort_values('log_date')
        
        if len(df) < 3: return None
        
        # Converte datas para numérico
        df['date_num'] = pd.to_datetime(df['log_date']).apply(lambda x: x.toordinal())
        
        # Regressão Linear
        slope, intercept = np.polyfit(df['date_num'], df['weight_kg'], 1)
        
        # Calcula R²
        y_pred = slope * df['date_num'] + intercept
        ss_res = np.sum((df['weight_kg'] - y_pred) ** 2)
        ss_tot = np.sum((df['weight_kg'] - np.mean(df['weight_kg'])) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        return {
            'slope': round(slope, 4),
            'r_squared': round(r_squared, 2),
            'trend_text': "Caindo 📉" if slope < -0.01 else "Subindo " if slope > 0.01 else "Estável ➡️"
        }