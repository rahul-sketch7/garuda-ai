# ============================================================
# Garuda AI - Vector Store
# ============================================================

import chromadb


# ============================================================
# CHROMA DATABASE
# ============================================================

client = chromadb.PersistentClient(
    path="./chroma_db"
)


# ============================================================
# GARUDA AI KNOWLEDGE COLLECTION
# ============================================================

collection = client.get_or_create_collection(
    name="garuda_ai_knowledge"
)