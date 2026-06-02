from datetime import date, datetime, timedelta

class ReportGenerator:
    def __init__(self, db, nutrition_service):
        self.db = db
        self.nutrition = nutrition_service
    
    def gerar_relatorio_semanal(self) -> str:
        """Gera relatório em Markdown"""
        summary = self.nutrition.get_daily_summary()
        semanal = self.nutrition.get_weekly_summary()
        
        if semanal.empty:
            return "Sem dados suficientes para o relatório."
        
        total_cal = semanal['calories'].sum()
        media = semanal['calories'].mean()
        pico = semanal['calories'].max()
        
        texto = f"""
## 📊 Relatório Semanal

**Período:** Últimos 7 dias

### 🔥 Calorias
- **Total consumido:** {total_cal:.0f} kcal
- **Média diária:** {media:.0f} kcal
- **Dia de maior consumo:** {pico:.0f} kcal

### 📈 Consistência
- **Dias registrados:** {len(semanal)} de 7
- **Taxa de adesão:** {(len(semanal)/7*100):.0f}%

_Gerado em {date.today().strftime('%d/%m/%Y')}_
        """
        return texto
    
    def exportar_csv_refeicoes(self, dias=30):
        """Exporta refeições em CSV"""
        import pandas as pd
        meals = self.db.get_meals(days=dias)
        if not meals:
            return None
        df = pd.DataFrame(meals)
        return df.to_csv(index=False).encode('utf-8')
    
    def calcular_projecao_meta(self, user) -> dict:
        """Projeta quando o usuário atingirá a meta"""
        peso_atual = user.get("current_weight", 75.0)
        meta = user.get("goal_weight", 70.0)
        
        weights_df = self.db.get_weights(days=60)
        if len(weights_df) < 2:
            return {"dias": None, "mensagem": "Precisa de mais dados de peso"}
        
        import numpy as np
        y = weights_df['weight'].astype(float).values
        slope = np.polyfit(range(len(y)), y, 1)[0]
        
        if slope >= 0:
            return {"dias": None, "mensagem": "Peso não está diminuindo ainda. Continue firme!"}
        
        diff = peso_atual - meta
        dias = int(diff / abs(slope))
        data_proj = date.today() + timedelta(days=dias)
        
        return {
            "dias": dias,
            "data_proj": data_proj.strftime('%d/%m/%Y'),
            "mensagem": f"Projeção: meta atingida em ~{dias} dias ({data_proj.strftime('%d/%m/%Y')})"
        }
