import os
import jwt
import datetime
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling
import pymongo
from pymongo import MongoClient
from pymongo.server_api import ServerApi
# Database connection configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Arthur-2002",
    "database": "projet",
    "pool_name": "mypool",
    "pool_size": 5
}

# Create connection pool
connection_pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)

def get_db():
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        return connection, cursor
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise e
    

# import pandas as pd

uri = "mongodb+srv://arthurgautier29480:lapin@cluster0.wuq03.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["projet"]

collection=db["ville"]



load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY", "Benford2023_Projet1_SecretKey_9876543210")
API_PASSWORD = os.getenv("API_PASSWORD", "lapin")


security = HTTPBearer(auto_error=False)

templates = Jinja2Templates(directory="templates")

class TokenRequest(BaseModel):
    password: str
    duration: Optional[int] = 3600  # Durée en secondes (1h par défaut)

def create_jwt(duration: int) -> str:
    """
    Génère un token JWT avec une durée de validité spécifiée.
    
    Args:
        duration (int): Durée de validité du token en secondes
        
    Returns:
        str: Token JWT encodé
    """
    expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=duration)
    return jwt.encode(
        {"exp": expiration},
        SECRET_KEY,
        algorithm="HS256"
    )

async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    Vérifie la validité du token JWT fourni.
    
    Args:
        credentials (Optional[HTTPAuthorizationCredentials]): Credentials fournis via le bearer token
        
    Returns:
        bool: True si le token est valide, False sinon
        
    Note:
        Ne lève pas d'exception pour permettre l'affichage de la page de login
    """
    if not credentials:
        return False
        
    try:
        jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return True
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return False

def get_login_page(request: Request, message: str = None):
    """
    Génère la page de login HTML.
    
    Args:
        request (Request): Requête FastAPI
        message (str, optional): Message à afficher sur la page de login
        
    Returns:
        HTMLResponse: Page HTML de login
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Authentification - Projet Benford</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .login-container {{
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                width: 350px;
            }}
            h1 {{
                color: #2c3e50;
                text-align: center;
                margin-bottom: 20px;
            }}
            .form-group {{
                margin-bottom: 15px;
            }}
            label {{
                display: block;
                margin-bottom: 5px;
                color: #555;
            }}
            input[type="password"] {{
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }}
            button {{
                width: 100%;
                padding: 10px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }}
            button:hover {{
                background-color: #2980b9;
            }}
            .message {{
                color: #e74c3c;
                text-align: center;
                margin-bottom: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="login-container">
            <h1>Authentification</h1>
            {f'<div class="message">{message}</div>' if message else ''}
            <form action="/login" method="post">
                <div class="form-group">
                    <label for="password">Mot de passe:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit">Se connecter</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

def setup_auth_routes(app):
    """
    Configure les routes d'authentification pour l'application FastAPI.
    
    Args:
        app (FastAPI): Application FastAPI
        
    Note:
        Cette fonction doit être appelée dans le fichier main.py
    """
    @app.get("/login")
    async def login_page(request: Request):
        """
        Affiche la page de login.
        
        Args:
            request (Request): Requête FastAPI
            
        Returns:
            HTMLResponse: Page HTML de login
        """
        return get_login_page(request)

    @app.post("/login")
    async def login(password: str = Form(...)):
        """
        Traite la soumission du formulaire de login.
        
        Args:
            password (str): Mot de passe soumis via le formulaire
            
        Returns:
            RedirectResponse: Redirection vers la page d'accueil ou la page de login
        """
        if password == API_PASSWORD:
            response = RedirectResponse(url="/", status_code=303)
            token = create_jwt(duration=3600)
            response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
            return response
        else:
            return get_login_page(request=None, message="Mot de passe incorrect")

    @app.get("/logout")
    async def logout():
        """
        Déconnecte l'utilisateur en supprimant le cookie de token.
        
        Returns:
            RedirectResponse: Redirection vers la page de login
        """
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie(key="access_token")
        return response

def auth_middleware(app):
    """
    Configure le middleware d'authentification pour l'application FastAPI.
    
    Args:
        app (FastAPI): Application FastAPI
        
    Note:
        Cette fonction doit être appelée dans le fichier main.py
    """
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        """
        Middleware qui vérifie l'authentification pour toutes les routes sauf /login.
        
        Args:
            request (Request): Requête HTTP
            call_next (Callable): Fonction pour appeler le prochain middleware
            
        Returns:
            Response: Réponse HTTP
        """
        # Exclure les routes d'authentification
        if request.url.path in ["/login", "/static"]:
            return await call_next(request)
            
        # Vérifier le token dans les cookies
        token_cookie = request.cookies.get("access_token")
        if not token_cookie or not token_cookie.startswith("Bearer "):
            return RedirectResponse(url="/login", status_code=303)
            
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_cookie[7:])
        is_valid = await verify_token(credentials)
        
        if not is_valid:
            return RedirectResponse(url="/login", status_code=303)
            
        return await call_next(request) 