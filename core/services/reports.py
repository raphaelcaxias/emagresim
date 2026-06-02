from datetime import date, timedelta

class ReportGenerator:
    def __init__(self, db, nutrition):
        self.db = db
        self.nutrition = nutrition
    
    def gerar_relatorio_semanal(self):
        semanal = self.nutrition.get_weekly_summary()
        if semanal.empty:
            return "Sem dados suficientes."
        
        total = semanal['calories'].sum()
        media = semanal['calories'].mean()
        
        return f"""
## Relatório Semanal
- Total: {total:.0f} kcal
- Média: {media:.0f} kcal/dia
- Dias registrados: {len(semanal)}
        """
    
    def exportar_csv_refeicoes(self, dias=30):
        import pandas as pd
        meals = self.db.get_meals(days=dias)
        if not meals:
            return None
        df = pd.DataFrame(meals)
        return df.to_csv(index=False).encode('utf-8')
    
    def calcular_projecao_meta(self, user):
        peso_atual = user.get("current_weight", 75.0)
        meta = user.get("goal_weight", 70.0)
        diff = peso_atual - meta
        
        weights = self.db.get_weights(days=60)
        if len(weights) < 2:
            return {"mensagem": "Precisa de mais dados de peso"}
        
        import numpy as np
        slope = np.polyfit(range(len(weights)), weights['weight'].astype(float).values, 1)[0]
        
        if slope >= 0:
            return {"mensagem": "Peso não está diminuindo ainda"}
        
        dias = int(diff / abs(slope))
        return {"dias": dias, "mensagem": f"Projeção: ~{dias} dias"}
