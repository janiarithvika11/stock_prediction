import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_supabase_client = None

def get_supabase_client() -> Client:
    global _supabase_client

    if _supabase_client is None:
        url = os.getenv('VITE_SUPABASE_URL')
        key = os.getenv('VITE_SUPABASE_SUPABASE_ANON_KEY')

        if not url or not key:
            raise ValueError('Supabase URL or Key not found in environment variables')

        _supabase_client = create_client(url, key)

    return _supabase_client
