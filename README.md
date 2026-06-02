# 💪 EmagreSim - Sistema de Monitoramento Nutricional

![Versão](https://img.shields.io/badge/versão-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.35.0-red)
![Licença](https://img.shields.io/badge/licença-MIT-yellow)

Sistema inteligente de monitoramento nutricional e controle de peso, desenvolvido para o público brasileiro com base em dados científicos e gamificação comportamental.

## 🚀 Features

### ✅ Core
- **Registro Alimentar Inteligente**: Busca por texto, filtros por período, 200+ alimentos brasileiros
- **Controle Calórico Automatizado**: Cálculo de TMB/TDEE baseado em Mifflin-St Jeor
- **Macronutrientes Detalhados**: Proteínas, carboidratos, gorduras e fibras
- **Evolução de Peso**: Gráficos interativos e análise de tendências
- **Gamificação**: Sistema de XP, níveis e conquistas

### 📊 Análises Avançadas
- Padrões de consumo por período do dia
- Velocidade de perda/ganho de peso
- Consistência de registro
- Desafios semanais personalizados

### 🔧 Técnico
- **Arquitetura Modular**: Separação clara de responsabilidades
- **Supabase Integration**: Banco de dados real com RLS
- **Modo Mock**: Funciona 100% offline para desenvolvimento
- **Logging Estruturado**: Diagnóstico preciso de erros
- **Type Hints**: Código documentado e tipado

## ️ Instalação

### Pré-requisitos
- Python 3.11+
- Conta no Supabase (opcional, para produção)
- Conta no Streamlit Cloud (para deploy)

### Passo a Passo

1. **Clone o repositório**:
```bash
git clone https://github.com/seu-usuario/emagresim.git
cd emagresim
