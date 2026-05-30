class AnalyticsEngine:
    @staticmethod
    def calculate_bmi(weight, height_cm):
        """Calcula IMC"""
        if not weight or not height_cm: return 0
        height_m = height_cm / 100
        return round(weight / (height_m ** 2), 1)

    @staticmethod
    def get_bmi_category(bmi):
        if bmi < 18.5: return "Abaixo", "⚠️"
        if bmi < 24.9: return "Normal", "✅"
        if bmi < 29.9: return "Sobrepeso", "⚠️"
        return "Obesidade", "🚨"

    @staticmethod
    def calculate_tmb(weight, height_cm, age, gender, activity):
        """Taxa Metabólica Basal (Mifflin-St Jeor)"""
        if not all([weight, height_cm, age, gender]): return 0
        base = 10 * weight + 6.25 * height_cm - 5 * age
        if gender == 'M': base += 5
        else: base -= 161
        
        multipliers = {
            'Sedentario': 1.2, 'Leve': 1.375, 
            'Moderado': 1.55, 'Intenso': 1.725
        }
        return round(base * multipliers.get(activity, 1.2))

    @staticmethod
    def analyze_correlations(logs):
        """Simulação de análise simples para o portfólio"""
        if len(logs) < 5: return "Dados insuficientes para análise."
        # Aqui você poderia usar pandas/numpy para correlações reais
        return "Seus dados estão sendo processados. Mais registros geram insights melhores!"
