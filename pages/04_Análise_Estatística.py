import streamlit as st
from core.database import AppDatabase
from core.nutrition import NutritionService
from core.analytics import AnalyticsService
from core.services.gamification_advanced import GamificationAdvanced
from components import card_metric, empty_state

if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

@st.cache_resource(show_spinner=False)
def init():
    db = AppDatabase()
    return db, NutritionService(db), AnalyticsService(db)

db, nutrition, analytics = init()
user = st.session_state.user

st.title("📊 Análise Estatística")

tab1, tab2, tab3, tab4 = st.tabs(["Padrões", "Tendências", "Gamificação", "Relatórios"])

with tab1:
    st.subheader("🍽️ Padrões de Consumo")
    patterns = analytics.analyze_meal_patterns(30)
    if patterns.get("has_data"):
        col1, col2 = st.columns(2)
        with col1: st.metric("Média/refeição", f"{patterns['avg_calories_per_meal']:.0f} kcal")
        with col2: st.metric("Após 20h", f"{patterns['percent_after_8pm']}%")
        
        st.markdown("**Divisão por período:**")
        for periodo, cal in patterns.get('period_calories', {}).items():
            st.markdown(f"- {periodo.capitalize()}: {cal:.0f} kcal")
    else:
        empty_state("", "Dados insuficientes", "Registre mais refeições")

with tab2:
    st.subheader("⚖️ Tendência de Peso")
    trend = analytics.analyze_weight_trend(60)
    if trend.get("has_data"):
        if trend.get("insufficient_data"):
            st.info("Precisa de mais pesagens")
        else:
            col1, col2 = st.columns(2)
            with col1: st.metric("Variação total", f"{trend['total_change']:+.1f} kg")
            with col2: st.metric("Velocidade", f"{trend['trend_rate']:+.2f} kg/semana")
    else:
        empty_state("⚖️", "Sem dados de peso")

with tab3:
    st.subheader("🏆 Gamificação")
    
    # Sistema de níveis
    nivel_info = GamificationAdvanced.calcular_nivel(150)  # XP inicial demo
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Nível", f"{nivel_info['nivel']} - {nivel_info['titulo']}")
    with col2: st.metric("XP Total", nivel_info['xp_total'])
    with col3: st.metric("Próximo nível", f"{nivel_info['xp_proximo'] - nivel_info['xp_atual']} XP")
    
    st.markdown(f"**Progresso para nível {nivel_info['nivel']+1}:**")
    from components import progress_bar
    progress_bar(nivel_info['progresso'])
    
    st.markdown("### 🎯 Conquistas")
    achs = db.get_achievements()
    if achs:
        for a in achs:
            st.markdown(f"- 🏅 {a.get('title')} ({a.get('unlocked_at', '')})")
    else:
        st.info("Nenhuma conquista ainda. Continue registrando!")

with tab4:
    st.subheader("📄 Relatórios")
    from core.services.reports import ReportGenerator
    report_gen = ReportGenerator(db, nutrition)
    
    if st.button("Gerar Relatório Semanal"):
        relatorio = report_gen.gerar_relatorio_semanal()
        st.markdown(relatorio)
    
    if st.button("Exportar CSV (30 dias)"):
        csv = report_gen.exportar_csv_refeicoes(30)
        if csv:
            st.download_button("⬇️ Baixar CSV", csv, "refeicoes.csv", "text/csv")
        else:
            st.warning("Sem dados para exportar")
    
    if st.button("Calcular Projeção de Meta"):
        proj = report_gen.calcular_projecao_meta(user)
        st.info(proj['mensagem'])
