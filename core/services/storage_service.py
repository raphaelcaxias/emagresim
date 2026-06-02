import streamlit as st
import logging
from supabase import create_client, Client
from datetime import datetime
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class StorageService:
    """Serviço de upload de fotos via Supabase Storage."""
    
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)
        self.bucket_name = "meal-photos"
    
    def upload_photo(self, photo, user_id: str, meal_id: str) -> Optional[str]:
        """Faz upload da foto e retorna URL pública."""
        try:
            # Gera nome único para o arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{user_id}/{meal_id}_{timestamp}.jpg"
            
            # Upload para o bucket
            self.client.storage.from_(self.bucket_name).upload(
                file_name,
                photo.read(),
                {"content-type": "image/jpeg"}
            )
            
            # Obtém URL pública
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_name)
            
            logger.info(f"Foto uploadada: {file_name}")
            return public_url
            
        except Exception as e:
            logger.error(f"Erro no upload de foto: {e}")
            return None
    
    def delete_photo(self, file_path: str) -> bool:
        """Remove foto do storage."""
        try:
            self.client.storage.from_(self.bucket_name).remove([file_path])
            logger.info(f"Foto removida: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover foto: {e}")
            return False
    
    def get_photo_url(self, file_path: str) -> Optional[str]:
        """Retorna URL pública da foto."""
        try:
            return self.client.storage.from_(self.bucket_name).get_public_url(file_path)
        except Exception as e:
            logger.error(f"Erro ao obter URL: {e}")
            return None
