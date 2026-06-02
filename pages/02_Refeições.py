import streamlit as st
from datetime import datetime
from core.database import AppDatabase
from core.nutrition import NutritionService
from utils.food_db import FOOD_DB, buscar_alimento

# Verifica autenticação
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

# Inicializa serviços
@st.cache_resource(show_spinner=False)
def init():
    db = AppDatabase()
    return db, NutritionService(db)

db, nutrition = init()
user = st.session_state.user

# Título e header
st.title("🍽️ Registro Alimentar")
st.markdown(f"**{user.get('name', 'Usuário')}** - {datetime.now().strftime('%d/%m/%Y')}")

# Seleção do tipo de refeição
st.subheader("📋 Tipo de Refeição")
tipo_refeicao = st.selectbox(
    "O que você vai registrar?",
    ["☕ Café da Manhã", "🍴 Almoço", "🌙 Jantar", "🥪 Lanche da Tarde", "🌃 Ceia"],
    index=0
)

# Mapeia tipo para categoria
mapeamento_categoria = {
    "☕ Café da Manhã": "cafe_manha",
    "🍴 Almoço": "almoco_jantar",
    "🌙 Jantar": "almoco_jantar",
    "🥪 Lanche da Tarde": "lanche",
    "🌃 Ceia": "ceia"
}
categoria_selecionada = mapeamento_categoria[tipo_refeicao]

# Filtro de alimentos por categoria
def get_alimentos_por_categoria(categoria):
    return {k: v for k, v in FOOD_DB.items() if v.get("category") == categoria}

# Busca inteligente com autocomplete
st.subheader("🔍 Buscar Alimento")
termo_busca = st.text_input("Digite o nome do alimento...", placeholder="Ex: arroz, frango, banana...")

if termo_busca:
    resultados = buscar_alimento(termo_busca)
    if resultados:
        opcoes = {f"{r['name']} - {r['cal']} kcal": r['key'] for r in resultados}
        alimento_selecionado = st.selectbox(
            "Selecione o alimento:",
            list(opcoes.keys()),
            format_func=lambda x: x
        )
        food_key = opcoes[alimento_selecionado]
    else:
        st.warning("Nenhum alimento encontrado. Tente outro termo.")
        food_key = None
else:
    # Mostra alimentos da categoria selecionada
    alimentos_categoria = get_alimentos_por_categoria(categoria_selecionada)
    if alimentos_categoria:
        opcoes_categoria = {
            f"{v['name']} - {v['cal']} kcal ({v['portion']})": k 
            for k, v in alimentos_categoria.items()
        }
        alimento_selecionado = st.selectbox(
            "Ou escolha da categoria:",
            list(opcoes_categoria.keys()),
            format_func=lambda x: x
        )
        food_key = opcoes_categoria[alimento_selecionado]
    else:
        st.info("Nenhum alimento nesta categoria.")
        food_key = None

# Quantidade e horário
col1, col2 = st.columns(2)
with col1:
    quantidade = st.number_input(
        "Quantidade (multiplicador)",
        min_value=0.1,
        max_value=10.0,
        value=1.0,
        step=0.1
    )
with col2:
    hora_registro = st.time_input(
        "Horário do registro",
        value=datetime.now().time()
    )

# Observações (para almoço/jantar)
observacoes = ""
if categoria_selecionada == "almoco_jantar":
    st.subheader("📝 Detalhes da Refeição")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Proteína Principal:**")
        proteinas = [k for k, v in FOOD_DB.items() if v.get("category") == "almoco_jantar" and any(p in v["name"].lower() for p in ["frango", "carne", "peixe", "camarão"])]
        if proteinas:
            opcoes_proteinas = {FOOD_DB[p]["name"]: p for p in proteinas}
            proteina_escolhida = st.selectbox("Selecione:", list(opcoes_proteinas.keys()))
    
    with col2:
        st.markdown("**Acompanhamentos:**")
        opcoes_acomp = []
        if st.checkbox("Arroz"): opcoes_acomp.append("arroz")
        if st.checkbox("Feijão"): opcoes_acomp.append("feijao")
        if st.checkbox("Salada"): opcoes_acomp.append("salada")
        if st.checkbox("Batata"): opcoes_acomp.append("batata")
        if st.checkbox("Legumes"): opcoes_acomp.append("legumes")
    
    st.markdown("**Bebida:**")
    bebidas = [k for k, v in FOOD_DB.items() if v.get("category") == "almoco_jantar" and any(b in v["name"].lower() for b in ["suco", "refrigerante", "agua", "cerveja"])]
    if bebidas:
        opcoes_bebidas = {FOOD_DB[b]["name"]: b for b in bebidas}
        bebida_escolhida = st.selectbox("Selecione:", list(opcoes_bebidas.keys()))
    
    observacoes = st.text_area(
        "Observações adicionais",
        placeholder="Ex: arroz integral, salada de alface e tomate, suco de laranja natural..."
    )

# Botão de registro
st.markdown("---")
col1, col2 = st.columns([3, 1])
with col1:
    if st.button("✅ Registrar Refeição", type="primary", use_container_width=True):
        if food_key:
            ok, nome, calorias = nutrition.register_food(
                food_key, 
                quantidade, 
                hora_registro.strftime("%H:%M")
            )
            if ok:
                st.success(f"✅ {nome} registrado com sucesso!")
                st.info(f"🔥 {calorias * quantidade:.0f} kcal adicionadas")
                st.rerun()
        else:
            st.error("❌ Selecione um alimento primeiro!")

with col2:
    if st.button("🔄 Limpar", use_container_width=True):
        st.rerun()

# Histórico do dia
st.markdown("---")
st.subheader("📋 Refeições de Hoje")

summary = nutrition.get_daily_summary()
if summary['meals']:
    total_calorias = 0
    for i, meal in enumerate(summary['meals']):
        col1, col2, col3 = st.columns([4, 2, 1])
        with col1:
            st.markdown(f"**{meal.get('meal_time', '--:--')}** - {meal.get('food', '?')}")
            if meal.get('notes'):
                st.caption(f"📝 {meal.get('notes')}")
        with col2:
            st.markdown(f"🔥 {meal.get('calories', 0)} kcal")
            total_calorias += meal.get('calories', 0)
        with col3:
            if st.button("🗑️", key=f"del_{i}"):
                # Aqui implementaria exclusão
                st.info("Função de exclusão em desenvolvimento")
    
    st.markdown("---")
    st.markdown(f"**Total de calorias hoje: {total_calorias} kcal**")
else:
    st.info("📭 Nenhuma refeição registrada hoje. Comece agora!")

# Dicas rápidas
st.markdown("---")
st.markdown("### 💡 Dicas")
if categoria_selecionada == "cafe_manha":
    st.info("☕ Um bom café da manhã inclui: proteína + carboidrato + fruta")
elif categoria_selecionada == "almoco_jantar":
    st.info("🍽️ Monte seu prato ideal: 50% salada/legumes, 25% proteína, 25% carboidrato")
elif categoria_selecionada == "lanche":
    st.info("🥪 Prefira lanches naturais: frutas, iogurte, sanduíches integrais")
elif categoria_selecionada == "ceia":
    st.info("🌙 Evite refeições pesadas antes de dormir. Prefira chás e alimentos leves")
