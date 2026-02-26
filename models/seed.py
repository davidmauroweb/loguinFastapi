from sqlalchemy.orm import Session
from models.db import SessionLocal, engine, Base, User, Client
from core.security import get_password_hash

def seed_db():
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Verificar si ya existen usuarios para no duplicar
        if db.query(User).count() == 0:
            admin = User(
                username="david",
                rol="admin",
                hashed_password=get_password_hash("cecisa")
            )
            operador1 = User(
                username="santi",
                rol="usuario",
                hashed_password=get_password_hash("santisanti")
            )
            operador2 = User(
                username="lautaro",
                rol="usuario",
                hashed_password=get_password_hash("lautaro1234")
            )
            
            db.add_all([admin, operador1, operador2])
            db.commit()
            print("✅ Seeders cargados: admin y 2 operadores")
    except Exception as e:
        print(f"❌ Error en seeders: {e}")
    finally:
        db.close()