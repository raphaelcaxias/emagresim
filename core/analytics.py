import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict
from core.database import AppDatabase

class AnalyticsService:
    def __init__(self, db: AppDatabase): 
        self.db = db
    
    def analyze_meal_patterns(self, days: int = 30) -> Dict:
        meals = self.db.get_meals(days=days)
        if not meals: return {"has_data": False}
        df = pd.DataFrame(meals)
        df['hour'] = pd.to_datetime(df['meal_time'], format='%H:%M').dt.hour
        df['period'] = pd.cut(df['hour'], bins=[-1, 6, 12, 18, 24], labels=['madrugada', 'manhã', 'tarde', 'noite'])
        period_calories = df.groupby('period', observed=False)['calories'].sum().to_dict()
        after_8pm = df[df['hour'] >= 20]['calories'].sum()
        total_calories = df['calories'].sum()
        percent_after_8pm = (after_8pm / total_calories * 100) if total_calories > 0 else 0
        
        return {
            "has_data": True, "period_calories": period_calories,
            "percent_after_8pm": round(percent_after_8pm, 1),
            "avg_calories_per_meal": round(df['calories'].mean(), 0),
            "most_common_hour": int(df['hour'].mode()[0]) if not df['hour'].empty else None
        }
    
    def analyze_weight_trend(self, days: int = 30) -> Dict:
        weights_df = self.db.get_weights(days=days)
        if weights_df.empty or len(weights_df) < 1: return {"has_data": False}
        last_weight = float(weights_df.iloc[-1]['weight'])
        if len(weights_df) >= 2:
            x = np.arange(len(weights_df))
            y = weights_df['weight'].astype(float).values
            slope = np.polyfit(x, y, 1)[0]
            first_weight = float(weights_df.iloc[0]['weight'])
            total_change = last_weight - first_weight
            
            return {
                "has_data": True, "total_change": round(total_change, 1),
                "trend": "up" if slope > 0.05 else "down" if slope < -0.05 else "stable",
                "trend_rate": round(slope * 7, 2),
                "current_weight": last_weight,
                "lowest_weight": round(weights_df['weight'].min(), 1),
                "highest_weight": round(weights_df['weight'].max(), 1)
            }
        return {"has_data": True, "current_weight": last_weight, "insufficient_data": True}
    
    def analyze_consistency(self, days: int = 30) -> Dict:
        meals = self.db.get_meals(days=days)
        if not meals: return {"has_data": False}
        df = pd.DataFrame(meals)
        df['meal_date'] = pd.to_datetime(df['meal_date'])
        unique_days = df['meal_date'].dt.date.nunique()
        total_days = min(days, (datetime.now().date() - df['meal_date'].min().date()).days + 1)
        consistency_rate = (unique_days / total_days * 100) if total_days > 0 else 0
        meals_per_day = df.groupby(df['meal_date'].dt.date).size()
        
        return {
            "has_data": True, "registered_days": unique_days,
            "total_days_analyzed": total_days,
            "consistency_rate": round(consistency_rate, 1),
            "avg_meals_per_day": round(meals_per_day.mean(), 1)
        }
    
    def get_full_report(self, days: int = 30) -> Dict:
        return {
            "meal_patterns": self.analyze_meal_patterns(days),
            "weight_trend": self.analyze_weight_trend(days),
            "consistency": self.analyze_consistency(days)
        }
