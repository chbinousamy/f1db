import os
import json
import pandas as pd
import fastf1

# 1. Définir le nom du dossier de cache
CACHE_DIR = 'fastf1_cache'

# 2. Créer le dossier s'il n'existe pas (évite l'erreur NotADirectoryError)
os.makedirs(CACHE_DIR, exist_ok=True)

# 3. Activer le cache
fastf1.Cache.enable_cache(CACHE_DIR)

def clean_for_nosql(df):
    clean_df = df.copy()
    for col in clean_df.columns:
        if pd.api.types.is_timedelta64_dtype(clean_df[col]):
            clean_df[col] = clean_df[col].dt.total_seconds()
        elif pd.api.types.is_datetime64_any_dtype(clean_df[col]):
            clean_df[col] = clean_df[col].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    clean_df = clean_df.where(pd.notnull(clean_df), None)
    return clean_df

def generate_static_json(year, location, session_type):
    try:
        session = fastf1.get_session(year, location, session_type)
        session.load()
        
        # Données des tours (Laps)
        laps_cleaned = clean_for_nosql(session.laps)
        laps_data = laps_cleaned.to_dict(orient="records")
        
        # S'assurer que le dossier de sortie existe
        os.makedirs('docs/api', exist_ok=True)
        
        # Nom du fichier : docs/api/2026_monaco_r.json
        filename = f"docs/api/{year}_{location.lower()}_{session_type.lower()}.json"
        
        with open(filename, 'w') as f:
            json.dump(laps_data, f, indent=2)
            
        print(f"✅ Fichier généré avec succès : {filename}")
    except Exception as e:
        print(f"❌ Erreur pour {year} {location} : {e}")

if __name__ == "__main__":
    # Exemple : Générer les données pour Monaco 2024 (Course)
    # Dans un vrai projet, tu peux automatiser le choix de la dernière course
    generate_static_json(2024, 'Monaco', 'R')
