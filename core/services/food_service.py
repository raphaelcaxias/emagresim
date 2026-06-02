import streamlit as st
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class FoodService:
    """Serviço para gerenciar alimentos do banco Supabase."""
    
    def __init__(self, supabase_client):
        self.client = supabase_client
        self.is_online = supabase_client is not None
    
    def get_categories(self) -> List[Dict]:
        """Retorna todas as categorias de refeição."""
        if not self.is_online:
            return self._get_fallback_categories()
        
        try:
            response = self.client.table("meal_categories").select("*").order("display_order").execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Erro ao buscar categorias: {e}")
            return self._get_fallback_categories()
    
    def search_foods(self, term: str, category_code: str = None, limit: int = 20) -> List[Dict]:
        """Busca alimentos por nome (com filtro opcional de categoria)."""
        if not self.is_online:
            return self._get_fallback_foods(term, category_code, limit)
        
        try:
            # Usa a função SQL search_foods
            response = self.client.rpc(
                "search_foods",
                {
                    "search_term": term,
                    "category_code": category_code,
                    "limit_results": limit
                }
            ).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Erro ao buscar alimentos: {e}")
            return self._get_fallback_foods(term, category_code, limit)
    
    def get_foods_by_category(self, category_code: str) -> List[Dict]:
        """Retorna todos os alimentos de uma categoria."""
        return self.search_foods("", category_code, limit=100)
    
    def create_custom_food(self, user_id: str, food_data: Dict) -> Optional[Dict]:
        """Cria um alimento customizado do usuário."""
        if not self.is_online:
            logger.warning("Sem conexão Supabase - não é possível criar alimento customizado")
            return None
        
        try:
            food_data["created_by"] = user_id
            food_data["is_custom"] = True
            food_data["is_active"] = True
            
            response = self.client.table("foods").insert(food_data).execute()
            logger.info(f"Alimento customizado criado: {food_data.get('name')}")
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"Erro ao criar alimento customizado: {e}")
            return None
    
    def _get_fallback_categories(self) -> List[Dict]:
        """Fallback local quando Supabase não está disponível."""
        return [
            {"id": "1", "name": "Café da Manhã", "code": "cafe_manha", "icon": "☕"},
            {"id": "2", "name": "Almoço/Jantar", "code": "almoco_jantar", "icon": "🍴"},
            {"id": "3", "name": "Lanche", "code": "lanche", "icon": "🥪"},
            {"id": "4", "name": "Ceia", "code": "ceia", "icon": "🌙"},
            {"id": "5", "name": "Frutas", "code": "frutas", "icon": "🍎"},
        ]
    
    def _get_fallback_foods(self, term: str, category_code: str, limit: int) -> List[Dict]:
        """Fallback local quando Supabase não está disponível."""
        # Retorna alimentos básicos do food_db.py
        from utils.food_db import FOOD_DB
        
        foods = []
        for key, info in FOOD_DB.items():
            if category_code and info.get("category") != category_code:
                continue
            if term and term.lower() not in info["name"].lower():
                continue
            
            foods.append({
                "id": key,
                "name": info["name"],
                "calories": info["calories"],
                "protein": info.get("protein", 0),
                "carbs": info.get("carbs", 0),
                "fat": info.get("fat", 0),
                "fiber": info.get("fiber", 0),
                "portion_size": info.get("portion", "100g"),
                "portion_grams": 100,
                "category_name": info.get("category", "geral")
            })
        
        return foods[:limit]
