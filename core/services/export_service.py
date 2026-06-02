import pandas as pd
import io
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ExportService:
    """Serviço de exportação de dados em múltiplos formatos."""
    
    def __init__(self, db):
        self.db = db
    
    def export_meals_to_csv(self, days: int = 30, user_id: Optional[str] = None) -> str:
        """Exporta refeições para CSV."""
        try:
            meals = self.db.get_meals(days=days)
            if not meals:
                return ""
            
            df = pd.DataFrame(meals)
            
            # Seleciona colunas relevantes
            cols = ['meal_date', 'meal_time', 'food', 'calories', 'protein', 'carbs', 'fat', 'fiber', 'quantity']
            df = df[[col for col in cols if col in df.columns]]
            
            # Converte para CSV
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, sep=';', encoding='utf-8')
            
            logger.info(f"CSV exportado: {len(meals)} refeições de {days} dias")
            return csv_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Erro ao exportar CSV: {e}")
            return ""
    
    def export_weight_to_csv(self, days: int = 90) -> str:
        """Exporta histórico de peso para CSV."""
        try:
            weights_df = self.db.get_weights(days=days)
            if weights_df.empty:
                return ""
            
            csv_buffer = io.StringIO()
            weights_df.to_csv(csv_buffer, index=False, sep=';', encoding='utf-8')
            
            logger.info(f"CSV de peso exportado: {len(weights_df)} registros")
            return csv_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Erro ao exportar peso CSV: {e}")
            return ""
    
    def generate_summary_report(self, days: int = 30) -> Dict:
        """Gera relatório resumido para exibição ou PDF."""
        try:
            meals = self.db.get_meals(days=days)
            weights_df = self.db.get_weights(days=days)
            
            if not meals:
                return {"error": "Sem dados suficientes"}
            
            df = pd.DataFrame(meals)
            
            report = {
                "period": f"Últimos {days} dias",
                "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "meals": {
                    "total": len(meals),
                    "avg_calories": int(df['calories'].mean()) if 'calories' in df.columns else 0,
                    "total_calories": int(df['calories'].sum()) if 'calories' in df.columns else 0,
                    "avg_protein": round(df['protein'].mean(), 1) if 'protein' in df.columns else 0,
                    "avg_carbs": round(df['carbs'].mean(), 1) if 'carbs' in df.columns else 0,
                    "avg_fat": round(df['fat'].mean(), 1) if 'fat' in df.columns else 0,
                },
                "weight": {
                    "records": len(weights_df),
                    "current": float(weights_df.iloc[-1]['weight']) if not weights_df.empty else None,
                    "change": None
                }
            }
            
            if len(weights_df) >= 2:
                first = weights_df.iloc[0]['weight']
                last = weights_df.iloc[-1]['weight']
                report["weight"]["change"] = round(last - first, 1)
            
            logger.info(f"Relatório gerado: {days} dias")
            return report
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            return {"error": str(e)}
    
    def download_csv_button(self, csv_content: str, filename: str, label: str):
        """Cria botão de download no Streamlit."""
        if csv_content:
            st.download_button(
                label=f"⬇️ {label}",
                data=csv_content.encode('utf-8'),
                file_name=filename,
                mime='text/csv',
                use_container_width=True
            )
        else:
            st.info("📭 Sem dados para exportar no período selecionado.")
