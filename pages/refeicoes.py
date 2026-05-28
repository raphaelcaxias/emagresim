# pages/refeicoes.py
import streamlit as st

def mostrar_refeicoes():
    st.markdown('<div class="section-card"><div class="section-title">🍽️ Registro de Refeições</div>', unsafe_allow_html=True)
    
    st.info("📌 Em desenvolvimento. Em breve você poderá registrar suas refeições com fotos.")
    
    st.markdown("### Refeições do dia (exemplo)")
    
    refeicoes = [
        {"hora": "08:00", "tipo": "Café da manhã", "desc": "Ovos mexidos, café sem açúcar", "cal": 320},
        {"hora": "12:30", "tipo": "Almoço", "desc": "Arroz, feijão, frango grelhado", "cal": 580},
        {"hora": "16:00", "tipo": "Lanche", "desc": "Iogurte com whey e aveia", "cal": 240},
    ]
    
    for ref in refeicoes:
        st.markdown(f"""
        <div style="background: #F7FAFC; border-left: 3px solid #008080; padding: 12px; border-radius: 8px; margin-bottom: 12px;">
            <span style="font-size: 0.8rem; color: #718096;">{ref['hora']} - {ref['tipo']}</span>
            <p style="margin: 4px 0; font-size: 0.9rem;">{ref['desc']}</p>
            <span style="font-size: 0.85rem; color: #FF6F61;">🔥 {ref['cal']} kcal</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
