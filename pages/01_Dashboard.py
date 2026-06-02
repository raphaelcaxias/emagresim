# MUDE DE:
from components import card_metric, progress_bar, empty_state

# PARA (se não criou components.py):
def card_metric(valor, label, icon="📊"):
    st.markdown(f"""
    <div class="data-card">
        <div class="data-value">{valor}</div>
        <div class="data-label">{icon} {label}</div>
    </div>
    """, unsafe_allow_html=True)
