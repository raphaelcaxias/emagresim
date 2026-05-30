import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats

class AnalyticsEngine:
    """Motor de análises estatísticas para o EmagreSim"""
    
    @staticmethod
    def calculate_bmi(weight, height_cm):
        if not weight or not height_cm: return None
        height_m = height_cm / 100
        return round(weight / (height_m ** 2), 1)
    
    @staticmethod
    def get_bmi_category(bmi):
        if bmi is None: return "N/D", "⚪"
        if bmi < 18.5: return "Abaixo do peso", "⚠️"
        if bmi < 24.9: return "Peso normal", "✅"
        if bmi < 29.9: return "Sobrepeso", "⚠️"
        return "Obesidade", "🚨"
    
    @staticmethod
    def calculate_tmb(weight, height_cm, age, gender, activity):
        """Taxa Metabólica Basal - Fórmula Mifflin-St Jeor"""
        if not all([weight, height_cm, age, gender]): return None
        base = (10 * weight) + (6.25 * height_cm) - (5 * age)
        base += 5 if gender == 'M' else -161
        
        multipliers = {'Sedentario': 1.2, 'Leve': 1.375, 'Moderado': 1.55, 'Intenso': 1.725}
        return round(base * multipliers.get(activity, 1.2))
    
    @staticmethod
    def calculate_weight_trend(logs, days=30):
        """Regressão linear para projetar tendência de peso"""
        if len(logs) < 5: return None
        
        df = pd.DataFrame(logs)
        df = df.dropna(subset=['weight_kg']).sort_values('log_date')
        if len(df) < 5: return None
        
        # Converter datas para numérico
        df['date_num'] = pd.to_datetime(df['log_date']).map(datetime.toordinal)
        
        # Regressão linear
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            df['date_num'], df['weight_kg']
        )
        
        # Projetar próximos 30 dias        future_dates = [df['date_num'].max() + i for i in range(1, 31)]
        projections = [slope * x + intercept for x in future_dates]
        
        # Calcular meta estimada
        daily_change = slope
        current_weight = df['weight_kg'].iloc[-1]
        days_to_goal = None
        
        return {
            'slope': round(slope * 1000, 2),  # kg por dia * 1000 = g/dia
            'r_squared': round(r_value**2, 3),
            'current_trend': 'perdendo' if slope < 0 else 'ganhando' if slope > 0 else 'estável',
            'projection_30d': round(projections[-1], 1),
            'daily_change_g': round(slope * 1000, 1)
        }
    
    @staticmethod
    def analyze_correlations(logs):
        """Análise de correlação entre variáveis"""
        if len(logs) < 10: return {}
        
        df = pd.DataFrame(logs).dropna()
        correlations = {}
        
        # Sono vs Energia
        if 'sleep_hours' in df.columns and 'energy_level' in df.columns:
            corr = df[['sleep_hours', 'energy_level']].corr().iloc[0,1]
            correlations['sono_energia'] = {
                'correlation': round(corr, 2),
                'interpretation': 'forte' if abs(corr) > 0.7 else 'moderada' if abs(corr) > 0.4 else 'fraca'
            }
        
        # Água vs Humor (codificar humor como numérico)
        if 'water_intake_liters' in df.columns and 'mood' in df.columns:
            df_temp = df.copy()
            df_temp['mood_num'] = df_temp['mood'].map({
                'Feliz': 5, 'Neutro': 3, 'Triste': 1, 'Ansioso': 2, 'Cansado': 2
            }).fillna(3)
            corr = df_temp[['water_intake_liters', 'mood_num']].corr().iloc[0,1]
            correlations['agua_humor'] = {
                'correlation': round(corr, 2),
                'interpretation': 'forte' if abs(corr) > 0.7 else 'moderada' if abs(corr) > 0.4 else 'fraca'
            }
        
        # Exercício vs Estresse
        if 'exercise_minutes' in df.columns and 'stress_level' in df.columns:
            corr = df[['exercise_minutes', 'stress_level']].corr().iloc[0,1]
            correlations['exercicio_estresse'] = {
                'correlation': round(corr, 2),
                'interpretation': 'forte' if abs(corr) > 0.7 else 'moderada' if abs(corr) > 0.4 else 'fraca'            }
        
        return correlations
    
    @staticmethod
    def generate_consistency_heatmap(logs, weeks=4):
        """Gera dados para heatmap de consistência estilo GitHub"""
        if not logs: return []
        
        df = pd.DataFrame(logs)
        today = datetime.now().date()
        start_date = today - timedelta(days=weeks*7)
        
        heatmap_data = []
        for i in range(weeks*7):
            check_date = start_date + timedelta(days=i)
            date_str = check_date.isoformat()
            
            # Verifica se há registro neste dia
            has_record = any(log.get('log_date') == date_str for log in logs)
            
            # Intensidade baseada em múltiplos registros
            intensity = 0
            if has_record:
                day_logs = [l for l in logs if l.get('log_date') == date_str]
                score = sum([
                    1 if l.get('weight_kg') else 0,
                    1 if l.get('water_intake_liters', 0) >= 2 else 0,
                    1 if l.get('sleep_hours', 0) >= 7 else 0,
                    1 if l.get('exercise_minutes', 0) > 0 else 0
                ])
                intensity = min(score, 4)
            
            heatmap_data.append({
                'date': date_str,
                'count': intensity,
                'level': intensity
            })
        
        return heatmap_data