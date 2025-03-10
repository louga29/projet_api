from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import matplotlib.pyplot as plt
import io
import base64
# from database import get_db,collection
import pandas as pd
from collections import Counter
import requests
from auth import setup_auth_routes, auth_middleware, get_db,collection

#uvicorn main:app --reload 
#pour lancer le serveur

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#permet de gérer les routes d'authentification
setup_auth_routes(app)
auth_middleware(app)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Affiche la page d'accueil avec la documentation de l'API.
    
    Returns:
        HTMLResponse: Page HTML contenant la documentation de l'API
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Documentation - Projet Benford</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            h2 {
                color: #3498db;
                margin-top: 30px;
            }
            .endpoint {
                background-color: #f8f9fa;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                border-left: 4px solid #3498db;
            }
            .endpoint h3 {
                margin: 0;
                color: #2c3e50;
            }
            .method {
                display: inline-block;
                padding: 3px 8px;
                border-radius: 3px;
                background-color: #3498db;
                color: white;
                font-size: 0.9em;
            }
            .description {
                margin: 10px 0;
                color: #555;
            }
            .url {
                background-color: #eee;
                padding: 5px 10px;
                border-radius: 3px;
                font-family: monospace;
            }
            .note {
                font-style: italic;
                color: #666;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Documentation de l'API Benford</h1>
            
            <h2>Routes SQL</h2>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <h3>Liste des Recettes</h3>
                <div class="description">Récupère toutes les recettes de la base de données.</div>
                <div class="url">/sql/recipes/</div>
            </div>

            <div class="endpoint">
                <span class="method">GET</span>
                <h3>Détails d'une Recette</h3>
                <div class="description">Récupère les détails d'une recette spécifique.</div>
                <div class="url">/sql/recipe/{id}</div>
                <div class="note">Remplacez {id} par l'identifiant de la recette</div>
            </div>

            <div class="endpoint">
                <span class="method">GET</span>
                <h3>Ingrédients d'une Recette</h3>
                <div class="description">Liste tous les ingrédients d'une recette spécifique.</div>
                <div class="url">/sql/recipe/{recipe_id}/ingredients</div>
            </div>

            <h2>Analyse de Benford</h2>

            <div class="endpoint">
                <span class="method">GET</span>
                <h3>Analyse de Benford SQL</h3>
                <div class="description">Analyse la loi de Benford sur différentes tables SQL.</div>
                <div class="url">/sql/{table}/benford</div>
                <div class="note">Tables disponibles : etapes, ingredients, materiel, semi_total, total</div>
            </div>

            <div class="endpoint">
                <span class="method">GET</span>
                <h3>Analyse de Benford Villes (API)</h3>
                <div class="description">Analyse la loi de Benford sur les populations des villes françaises.</div>
                <div class="url">/api/{number}</div>
                <div class="note">Remplacez {number} par le nombre de villes à analyser</div>
            </div>

            <div class="endpoint">
                <span class="method">GET</span>
                <h3>Analyse de Benford Villes (MongoDB)</h3>
                <div class="description">Analyse la loi de Benford sur les populations des villes depuis MongoDB.</div>
                <div class="url">/mongodb/benford/{number}</div>
            </div>

            <h2>Opérations MongoDB</h2>

            <div class="endpoint">
                <span class="method">POST</span>
                <h3>Ajouter une Ville</h3>
                <div class="description">Ajoute une nouvelle ville dans MongoDB.</div>
                <div class="url">/mongodb/insert</div>
            </div>

            <div class="endpoint">
                <span class="method">PUT</span>
                <h3>Mettre à jour une Ville</h3>
                <div class="description">Met à jour les informations d'une ville existante.</div>
                <div class="url">/mongodb/update/{city_name}</div>
            </div>

            <div class="endpoint">  
                <span class="method">DELETE</span>
                <h3>Supprimer une Ville</h3>
                <div class="description">Supprime une ville existante.</div>
                <div class="url">/mongodb/delete/{city_name}</div>
            </div>  

            <h2>Opérations SQL</h2>

            <div class="endpoint">
                <span class="method">POST</span>
                <h3>Ajouter une Recette</h3>
                <div class="description">Ajoute une nouvelle recette dans la base de données SQL.</div>
                <div class="url">/sql/recipe/insert</div>
                <div class="note">Paramètres requis: nom, description, temps_preparation, temps_cuisson</div>
            </div>

            <div class="endpoint">
                <span class="method">PUT</span>
                <h3>Modifier une Recette</h3>
                <div class="description">Modifie les informations d'une recette existante.</div>
                <div class="url">/sql/recipe/{recipe_id}</div>
                <div class="note">Paramètres optionnels: nom, description, temps_preparation, temps_cuisson</div>
            </div>

            <div class="endpoint">
                <span class="method">DELETE</span>
                <h3>Supprimer une Recette</h3>
                <div class="description">Supprime une recette et ses relations avec les ingrédients.</div>
                <div class="url">/sql/recipe/{recipe_id}</div>
                <div class="note">Attention: cette action est irréversible</div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/sql/recipes/")
async def get_recipes():
    """
    Récupère toutes les recettes de la base de données SQL.
    
    Returns:
        list: Liste de toutes les recettes
        
    Raises:
        HTTPException: En cas d'erreur lors de la récupération des données
    """
    try:
        conn, cursor = get_db()
        cursor.execute("SELECT * FROM recette;")
        recipes = cursor.fetchall()
        cursor.close()
        conn.close()
        return recipes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/sql/recipe/{id}")
async def get_recipe_ingredients(id: int):
    """
    Récupère les détails d'une recette spécifique par son ID.
    
    Args:
        id (int): Identifiant de la recette
        
    Returns:
        dict: Détails de la recette
        
    Raises:
        HTTPException: En cas d'erreur lors de la récupération des données
    """
    try:
        conn, cursor = get_db()
        sql = "SELECT * FROM recette WHERE id = %s;"
        cursor.execute(sql, (id,))
        recipe = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return recipe
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sql/recipe/{recipe_id}/steps")
async def get_recipe_steps(recipe_id: int):
    """
    Récupère les étapes de préparation d'une recette spécifique.
    
    Args:
        recipe_id (int): Identifiant de la recette
        
    Returns:
        dict: Dictionnaire contenant l'ID de la recette et la liste des étapes
        
    Raises:
        HTTPException: Si la recette n'existe pas ou si aucune étape n'est trouvée
    """
    try:
        conn, cursor = get_db()
        
        # D'abord vérifier si la recette existe
        check_recipe = "SELECT id FROM recette WHERE id = %s"
        cursor.execute(check_recipe, (recipe_id,))
        recipe = cursor.fetchone()
        
        if not recipe:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Recette non trouvée")
        
        # Si la recette existe, récupérer ses étapes
        sql = """
            SELECT 
                e.id,
                e.numero,
                e.etape as description
            FROM etape e
            WHERE e.recette_id = %s
            ORDER BY e.numero ASC
        """
        cursor.execute(sql, (recipe_id,))
        steps = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not steps:
            raise HTTPException(status_code=404, detail="Aucune étape trouvée pour cette recette")
            
        return {
            "recipe_id": recipe_id,
            "steps": steps
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sql/recipe/{recipe_id}/ingredients")
async def get_recipe_ingredients(recipe_id: int):
    """
    Récupère la liste des ingrédients d'une recette spécifique.
    
    Args:
        recipe_id (int): Identifiant de la recette
        
    Returns:
        list: Liste des ingrédients de la recette
        
    Raises:
        HTTPException: Si la recette n'existe pas ou si aucun ingrédient n'est trouvé
    """
    try:
        conn, cursor = get_db()
        
        # First check if recipe exists
        check_recipe = "SELECT id FROM recette WHERE id = %s"
        cursor.execute(check_recipe, (recipe_id,))
        recipe = cursor.fetchone()
        
        if not recipe:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        # If recipe exists, get ingredients
        sql = """
            SELECT i.id, i.nom, i.quantite
            FROM ingredient i
            JOIN recette_ingredient ri ON i.id = ri.ingredient_id
            WHERE ri.recette_id = %s;
        """
        cursor.execute(sql, (recipe_id,))
        ingredients = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not ingredients:
            raise HTTPException(status_code=404, detail="No ingredients found for this recipe")
            
        return ingredients
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/{number}", response_class=HTMLResponse)
async def get_city_benford(number: int):
    """
    Analyse la loi de Benford sur les populations des villes françaises récupérées via API.
    
    Args:
        number (int): Nombre de villes à analyser
        
    Returns:
        HTMLResponse: Page HTML contenant l'analyse graphique et tabulaire
        
    Raises:
        HTTPException: Si le nombre est invalide ou en cas d'erreur lors de la récupération des données
    """
    try:
        # Vérifier que le nombre est valide
        if number <= 0 or number > 100000:
            raise HTTPException(
                status_code=400,
                detail="Cela doit être un nombre entre 1 et 100000"
            )
            
        # Récupérer les données des communes depuis l'API
        url = "https://geo.api.gouv.fr/communes?fields=population&boost=population"
        response = requests.get(url)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail="Erreur lors de la récupération des données de l'API"
            )
            
        # Trier les communes par population et prendre les n premières
        cities = sorted(
            [city for city in response.json() if city.get('population')],
            key=lambda x: x['population'],
            reverse=True
        )[:number]
        
        # Extraire le premier chiffre de chaque population
        first_digits = [int(str(city['population'])[0]) for city in cities]
        
        # Calculer les pourcentages observés
        digit_counts = Counter(first_digits)
        total_count = len(first_digits)
        observed_distribution = {
            str(digit): (count / total_count * 100)
            for digit, count in digit_counts.items()
        }
        
        # Valeurs attendues selon la loi de Benford
        benford_expected = {
            "1": 30.1, "2": 17.6, "3": 12.5, "4": 9.7,
            "5": 7.9, "6": 6.7, "7": 5.8, "8": 5.1, "9": 4.6
        }
        
        # Créer le graphique
        plt.figure(figsize=(10, 6))
        
        # Tracer les valeurs attendues (Benford)
        digits = list(benford_expected.keys())
        expected_values = list(benford_expected.values())
        plt.plot(digits, expected_values, 'b-', label='Loi de Benford', marker='o')
        
        # Tracer les valeurs observées
        observed_values = [observed_distribution.get(d, 0) for d in digits]
        plt.plot(digits, observed_values, 'r--', label=f'Top {number} villes', marker='x')
        
        plt.title(f"Loi de Benford - Population des {number} plus grandes villes")
        plt.xlabel("Premier chiffre")
        plt.ylabel("Pourcentage (%)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Sauvegarder le graphique en base64
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        plt.close()
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        
        # Créer une réponse HTML élégante
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Analyse de Benford - Top {number} villes</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1, h2 {{
                    color: #333;
                    text-align: center;
                }}
                .graph {{
                    text-align: center;
                    margin: 20px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #f8f9fa;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Analyse de la loi de Benford</h1>
                <h2>Population des {number} plus grandes villes de France</h2>
                
                <div class="graph">
                    <img src="data:image/png;base64,{plot_url}" alt="Graphique de la loi de Benford">
                </div>
                
                <table>
                    <tr>
                        <th>Premier chiffre</th>
                        <th>Nombre d'occurrences</th>
                        <th>Pourcentage observé</th>
                        <th>Pourcentage attendu (Benford)</th>
                        <th>Écart</th>
                    </tr>
                    {''.join(f"""
                    <tr>
                        <td>{digit}</td>
                        <td>{digit_counts.get(int(digit), 0)}</td>
                        <td>{observed_distribution.get(digit, 0):.2f}%</td>
                        <td>{benford_expected[digit]}%</td>
                        <td>{abs(observed_distribution.get(digit, 0) - benford_expected[digit]):.2f}%</td>
                    </tr>
                    """ for digit in digits)}
                </table>
                
                <h2>Liste des villes analysées</h2>
                <table>
                    <tr>
                        <th>Rang</th>
                        <th>Ville</th>
                        <th>Population</th>
                        <th>Premier chiffre</th>
                    </tr>
                    {''.join(f"""
                    <tr>
                        <td>{i+1}</td>
                        <td>{city['nom']}</td>
                        <td>{city['population']:,}</td>
                        <td>{str(city['population'])[0]}</td>
                    </tr>
                    """ for i, city in enumerate(cities))}
                </table>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sql/benford/{table}", response_class=HTMLResponse)
async def get_benford_analysis(table: str):
    """
    Analyse la loi de Benford sur différentes tables de la base de données SQL.
    
    Args:
        table (str): Nom de la table à analyser ('etapes', 'ingredients', 'materiel', 'semi_total' ou 'total')
        
    Returns:
        HTMLResponse: Page HTML contenant l'analyse graphique et tabulaire
        
    Raises:
        HTTPException: Si la table est invalide ou en cas d'erreur lors de la récupération des données
    """
    try:
        # Récupérer les données SQL
        conn, cursor = get_db()
        
        if table == "etapes":
            sql = """
                SELECT 
                    e.numero as Valeur,
                    CONCAT('Étape ', e.numero) as nom
                FROM etape e
                WHERE e.numero > 0
                ORDER BY e.numero
            """
        elif table == "ingredients":
            sql = """
                SELECT 
                    CAST(REGEXP_REPLACE(i.quantite, '[^0-9.]', '') AS DECIMAL) as Valeur,
                    i.nom
                FROM ingredient i
                WHERE i.quantite REGEXP '^[0-9]'
                ORDER BY CAST(REGEXP_REPLACE(i.quantite, '[^0-9.]', '') AS DECIMAL) DESC
            """
        elif table == "materiel":
            sql = """
                SELECT 
                    CAST(REGEXP_REPLACE(m.equipement, '[^0-9.]', '') AS DECIMAL) as Valeur,
                    m.equipement as nom
                FROM materiel m 
                WHERE m.equipement REGEXP '^[0-9]'
                ORDER BY CAST(REGEXP_REPLACE(m.equipement, '[^0-9.]', '') AS DECIMAL) DESC
            """
        elif table == "total":
            sql = """
                SELECT Valeur, nom FROM (
                    -- Étapes
                    SELECT 
                        e.numero as Valeur,
                        CONCAT('Étape ', e.numero) as nom,
                        'etapes' as source
                    FROM etape e
                    WHERE e.numero > 0
                    
                    UNION ALL
                    
                    -- Ingrédients
                    SELECT 
                        CAST(REGEXP_REPLACE(i.quantite, '[^0-9.]', '') AS DECIMAL) as Valeur,
                        CONCAT('Ingrédient: ', i.nom) as nom,
                        'ingredients' as source
                    FROM ingredient i
                    WHERE i.quantite REGEXP '^[0-9]'
                    
                    UNION ALL
                    
                    -- Matériel
                    SELECT 
                        CAST(REGEXP_REPLACE(m.equipement, '[^0-9.]', '') AS DECIMAL) as Valeur,
                        CONCAT('Matériel: ', m.equipement) as nom,
                        'materiel' as source
                    FROM materiel m
                    WHERE m.equipement REGEXP '^[0-9]'
                ) combined_data
                ORDER BY Valeur DESC
            
            """
        elif table == "semi_total":
            sql = """
                SELECT Valeur, nom FROM (
                    -- Étapes
                    SELECT 
                        e.numero as Valeur,
                        CONCAT('Étape ', e.numero) as nom,
                        'etapes' as source
                    FROM etape e
                    WHERE e.numero > 0
                    
                    UNION ALL
                    
                    -- Ingrédients
                    SELECT 
                        CAST(REGEXP_REPLACE(i.quantite, '[^0-9.]', '') AS DECIMAL) as Valeur,
                        CONCAT('Ingrédient: ', i.nom) as nom,
                        'ingredients' as source
                    FROM ingredient i
                    WHERE i.quantite REGEXP '^[0-9]'
                   
                ) combined_data
                ORDER BY Valeur DESC
            
            """
        else:
            raise HTTPException(
                status_code=400,
                detail="Table invalide. Utilisez 'etapes', 'ingredients', 'materiel', 'semi_total' ou 'total'"
            )
            
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"Aucune donnée numérique valide trouvée dans {table}"
            )

        # Extraire le premier chiffre de chaque nombre
        first_digits = [int(str(item['Valeur'])[0]) for item in data]
        
        # Calculer les pourcentages observés
        digit_counts = Counter(first_digits)
        total_count = len(first_digits)
        observed_distribution = {
            str(digit): (count / total_count * 100)
            for digit, count in digit_counts.items()
        }

        # Valeurs attendues selon la loi de Benford
        benford_expected = {
            "1": 30.1, "2": 17.6, "3": 12.5, "4": 9.7,
            "5": 7.9, "6": 6.7, "7": 5.8, "8": 5.1, "9": 4.6
        }
        
        # Créer le graphique
        plt.figure(figsize=(10, 6))
        digits = list(benford_expected.keys())
        
        # Tracer les valeurs attendues (Benford)
        plt.plot(digits, list(benford_expected.values()), 'b-', 
                label='Loi de Benford', marker='o')
        
        # Tracer les valeurs observées
        observed_values = [observed_distribution.get(d, 0) for d in digits]
        plt.plot(digits, observed_values, 'r--', 
                label=f'Données {table}', marker='x')

        plt.title(f"Loi de Benford - {table}")
        plt.xlabel("Premier chiffre")
        plt.ylabel("Pourcentage (%)")
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Convertir le graphique en base64
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        plt.close()
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        # Créer la réponse HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Analyse de Benford - {table}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1, h2 {{
                    color: #333;
                    text-align: center;
                }}
                .graph {{
                    text-align: center;
                    margin: 20px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #f8f9fa;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Analyse de la loi de Benford</h1>
                <h2>Table : {table}</h2>
                
                <div class="graph">
                    <img src="data:image/png;base64,{plot_url}" alt="Graphique de la loi de Benford">
                </div>
                
                <table>
                    <tr>
                        <th>Premier chiffre</th>
                        <th>Nombre d'occurrences</th>
                        <th>Pourcentage observé</th>
                        <th>Pourcentage attendu (Benford)</th>
                        <th>Écart</th>
                    </tr>
                    {''.join(f"""
                    <tr>
                        <td>{digit}</td>
                        <td>{digit_counts.get(int(digit), 0)}</td>
                        <td>{observed_distribution.get(digit, 0):.2f}%</td>
                        <td>{benford_expected[digit]}%</td>
                        <td>{abs(observed_distribution.get(digit, 0) - benford_expected[digit]):.2f}%</td>
                    </tr>
                    """ for digit in digits)}
                </table>
                
                <h2>Liste des données analysées</h2>
                <table>
                    <tr>
                        <th>Rang</th>
                        <th>Nom</th>
                        <th>Valeur</th>
                        <th>Premier chiffre</th>
                    </tr>
                    {''.join(f"""
                    <tr>
                        <td>{i+1}</td>
                        <td>{item['nom']}</td>
                        <td>{item['Valeur']:,}</td>
                        <td>{str(item['Valeur'])[0]}</td>
                    </tr>
                    """ for i, item in enumerate(data))}
                </table>
            </div>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mongodb/benford/{number}", response_class=HTMLResponse)
async def get_city_benford_mongodb(number: int):
    """
    Analyse la loi de Benford sur les populations des villes stockées dans MongoDB.
    
    Args:
        number (int): Nombre de villes à analyser
        
    Returns:
        HTMLResponse: Page HTML contenant l'analyse graphique et tabulaire
        
    Raises:
        HTTPException: Si le nombre est invalide ou en cas d'erreur lors de la récupération des données
    """
    try:
        # Vérifier que le nombre est valide
        if number <= 0 or number > 100000:
            raise HTTPException(
                status_code=400,
                detail="Cela doit être un nombre entre 1 et 100000"
            )
            
        # Récupérer les données des communes depuis MongoDB
        cities = list(collection.find(
            {"Population": {"$exists": True, "$ne": None}},  # Changé population -> Population
            {"Nom": 1, "Population": 1, "_id": 0}  # Changé nom -> Nom
        ).sort("Population", -1).limit(number))  # Changé population -> Population
        
        if not cities:
            raise HTTPException(
                status_code=404,
                detail="Aucune donnée trouvée dans la collection"
            )
        
        # Extraire le premier chiffre de chaque population
        first_digits = [int(str(city['Population'])[0]) for city in cities]  # Changé population -> Population
        
        # Calculer les pourcentages observés
        digit_counts = Counter(first_digits)
        total_count = len(first_digits)
        observed_distribution = {
            str(digit): (count / total_count * 100)
            for digit, count in digit_counts.items()
        }
        
        # Valeurs attendues selon la loi de Benford
        benford_expected = {
            "1": 30.1, "2": 17.6, "3": 12.5, "4": 9.7,
            "5": 7.9, "6": 6.7, "7": 5.8, "8": 5.1, "9": 4.6
        }
        
        # Créer le graphique
        plt.figure(figsize=(10, 6))
        
        # Tracer les valeurs attendues (Benford)
        digits = list(benford_expected.keys())
        expected_values = list(benford_expected.values())
        plt.plot(digits, expected_values, 'b-', label='Loi de Benford', marker='o')
        
        # Tracer les valeurs observées
        observed_values = [observed_distribution.get(d, 0) for d in digits]
        plt.plot(digits, observed_values, 'r--', label=f'Top {number} villes (MongoDB)', marker='x')
        
        plt.title(f"Loi de Benford - Population des {number} plus grandes villes (MongoDB)")
        plt.xlabel("Premier chiffre")
        plt.ylabel("Pourcentage (%)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Sauvegarder le graphique en base64
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        plt.close()
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        
        # Créer une réponse HTML élégante
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Analyse de Benford - Top {number} villes (MongoDB)</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1, h2 {{
                    color: #333;
                    text-align: center;
                }}
                .graph {{
                    text-align: center;
                    margin: 20px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #f8f9fa;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Analyse de la loi de Benford (MongoDB)</h1>
                <h2>Population des {number} plus grandes villes de France</h2>
                
                <div class="graph">
                    <img src="data:image/png;base64,{plot_url}" alt="Graphique de la loi de Benford">
                </div>
                
                <table>
                    <tr>
                        <th>Premier chiffre</th>
                        <th>Nombre d'occurrences</th>
                        <th>Pourcentage observé</th>
                        <th>Pourcentage attendu (Benford)</th>
                        <th>Écart</th>
                    </tr>
                    {''.join(f"""
                    <tr>
                        <td>{digit}</td>
                        <td>{digit_counts.get(int(digit), 0)}</td>
                        <td>{observed_distribution.get(digit, 0):.2f}%</td>
                        <td>{benford_expected[digit]}%</td>
                        <td>{abs(observed_distribution.get(digit, 0) - benford_expected[digit]):.2f}%</td>
                    </tr>
                    """ for digit in digits)}
                </table>
                
                <h2>Liste des villes analysées</h2>
                <table>
                    <tr>
                        <th>Rang</th>
                        <th>Ville</th>
                        <th>Population</th>
                        <th>Premier chiffre</th>
                    </tr>
                    {''.join(f"""
                    <tr>
                        <td>{i+1}</td>
                        <td>{city['Nom']}</td>
                        <td>{city['Population']:,}</td>
                        <td>{str(city['Population'])[0]}</td>
                    </tr>
                    """ for i, city in enumerate(cities))}
                </table>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/mongodb/insert/{nom}/{habitant}", response_class=JSONResponse)
async def insert_city(nom: str, habitant: int):
    """
    Ajoute une nouvelle ville dans la base de données MongoDB.
    
    Args:
        nom (str): Nom de la ville
        habitant (int): Nombre d'habitants
        
    Returns:
        dict: Message de confirmation et ID de la ville ajoutée
        
    Raises:
        HTTPException: Si les paramètres sont invalides ou en cas d'erreur lors de l'insertion
    """
    try:

        if not nom or habitant is None:
            raise HTTPException(
                status_code=400,
                detail="Les champs 'nom' et 'habitant' sont requis"
            )
        
        # Insérer la nouvelle ville
        city = {"nom": nom, "habitant": habitant}
        result = collection.insert_one(city)
        
        return {
            "message": f"Ville {nom} ajoutée avec succès",
            "id": str(result.inserted_id)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/mongodb/update/{city_id}/{field}/{value}", response_class=JSONResponse)
async def update_city(city_id: str, field: str, value: str):
    """
    Met à jour les informations d'une ville existante dans MongoDB.
    
    Args:
        city_id (str): Identifiant MongoDB de la ville
        field (str): Champ à modifier ('nom' ou 'habitant')
        value (str): Nouvelle valeur pour le champ
        
    Returns:
        dict: Message de confirmation de la mise à jour
        
    Raises:
        HTTPException: Si la ville n'existe pas, si le champ est invalide ou en cas d'erreur
    """
    try:
        existing_city = collection.find_one({"_id": ObjectId(city_id)})
        if not existing_city:
            raise HTTPException(
                status_code=404,
                detail=f"La ville avec l'ID {city_id} n'existe pas"
            )
        
        if field not in ["nom", "habitant"]:
            raise HTTPException(
                status_code=400,
                detail="Le champ doit être 'nom' ou 'habitant'"
            )
        
        if field == "habitant":
            value = int(value)
        
        update_result = collection.update_one(
            {"_id": ObjectId(city_id)},
            {"$set": {field: value}}
        )
        
        if update_result.modified_count > 0:
            return {
                "message": f"Ville avec l'ID {city_id} mise à jour avec succès"
            }
        else:
            return {
                "message": "Aucune modification n'a été effectuée"
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/mongodb/delete/{city_name}", response_class=JSONResponse)
async def delete_city(city_name: str):
    """
    Supprime une ville de la base de données MongoDB.
    
    Args:
        city_name (str): Nom de la ville à supprimer
        
    Returns:
        dict: Message de confirmation de la suppression
        
    Raises:
        HTTPException: Si la ville n'existe pas ou en cas d'erreur lors de la suppression
    """
    try:
        # Vérifier si la ville existe
        existing_city = collection.find_one({"nom": city_name})
        if not existing_city:
            raise HTTPException(
                status_code=404,
                detail=f"La ville {city_name} n'existe pas"
            )
        
        # Supprimer la ville
        result = collection.delete_one({"nom": city_name})
        
        if result.deleted_count > 0:
            return {
                "message": f"Ville {city_name} supprimée avec succès"
            }
        else:
            return {
                "message": "Aucune ville n'a été supprimée"
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/sql/ingredient/{nom}/{quantite}")
async def insert_ingredient(nom: str, quantite: str):
    """
    Ajoute un nouvel ingrédient dans la base de données SQL.
    
    Args:
        nom (str): Nom de l'ingrédient
        quantite (str): Quantité de l'ingrédient
        
    Returns:
        dict: Message de confirmation de l'ajout
        
    Raises:
        HTTPException: En cas d'erreur lors de l'insertion
    """
    try:
        conn, cursor = get_db()
        
        sql = "INSERT INTO ingredient (nom, quantite) VALUES (%s, %s);"
        cursor.execute(sql, (nom, quantite))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {"message": f"Ingrédient '{nom}' ajouté avec succès avec une quantité de {quantite}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/benford/test", response_class=HTMLResponse)
async def get_benford_test():
    """
    Analyse la loi de Benford sur des images pour détecter les manipulations.
    Compare une image réelle, une image générée et une image photoshoppée.
    
    Returns:
        HTMLResponse: Page HTML contenant l'analyse graphique et tabulaire
        
    Raises:
        HTTPException: En cas d'erreur lors de l'analyse ou si les images ne sont pas trouvées
    """
    try:
        import pandas as pd
        import numpy as np
        import cv2
        from scipy.fftpack import dct
        from collections import Counter
        import os
        
        # Fonction pour calculer la distribution de Benford à partir d'une image
        def dct_and_benford(image_path):
            # Lire l'image
            img = cv2.imread(image_path)
            if img is None:
                raise HTTPException(status_code=404, detail=f"Image non trouvée: {image_path}")
            
            # Convertir en niveaux de gris
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Appliquer la DCT
            dct_coeffs = dct(dct(gray.T, norm='ortho').T, norm='ortho')
            
            # Prendre la valeur absolue des coefficients
            abs_coeffs = np.abs(dct_coeffs)
            
            # Aplatir le tableau
            flat_coeffs = abs_coeffs.flatten()
            
            # Filtrer les valeurs non nulles
            non_zero_coeffs = flat_coeffs[flat_coeffs > 0.1]
            
            # Extraire le premier chiffre de chaque coefficient
            first_digits = []
            for coeff in non_zero_coeffs:
                # Convertir en chaîne et prendre le premier caractère
                digit = int(str(float(coeff)).replace('.', '')[0])
                if 1 <= digit <= 9:  # Ignorer 0
                    first_digits.append(digit)
            
            # Calculer la distribution
            digit_counts = Counter(first_digits)
            total_count = len(first_digits)
            
            # Calculer les pourcentages
            percentages = {}
            for digit in range(1, 10):
                percentages[digit] = (digit_counts.get(digit, 0) / total_count * 100)
            
            return percentages
        
        # Chemins des images
        # Utiliser une image réelle du dataset
        real_image_path = "static/real.jpg"
        # Utiliser une image fake du dataset
        fake_image_path = "static/fake.jpg"
        # Utiliser l'image fournie
        custom_image_path = "static/photoshopfail.jpg"
        
        # Vérifier si les images existent, sinon les copier depuis le dataset
        if not os.path.exists("static"):
            os.makedirs("static")
    
        # # Calculer les distributions de Benford
        real_benford = dct_and_benford(real_image_path)
        fake_benford = dct_and_benford(fake_image_path)
        custom_benford = dct_and_benford(custom_image_path)
        
        # Valeurs attendues selon la loi de Benford
        benford_expected = {
            1: 30.1, 2: 17.6, 3: 12.5, 4: 9.7,
            5: 7.9, 6: 6.7, 7: 5.8, 8: 5.1, 9: 4.6
        }
        
        # Créer les graphiques
        plt.figure(figsize=(15, 5))
        
        # Graphique pour l'image réelle
        plt.subplot(1, 3, 1)
        digits = list(range(1, 10))
        real_values = [real_benford.get(d, 0) for d in digits]
        expected_values = [benford_expected[d] for d in digits]
        
        plt.bar(digits, real_values, alpha=0.5, label='Observé', color='blue')
        plt.plot(digits, expected_values, 'r-', label='Benford', marker='o')
        plt.title('Image Réelle')
        plt.xlabel('Premier chiffre')
        plt.ylabel('Pourcentage (%)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Graphique pour l'image fake
        plt.subplot(1, 3, 2)
        fake_values = [fake_benford.get(d, 0) for d in digits]
        
        plt.bar(digits, fake_values, alpha=0.5, label='Observé', color='green')
        plt.plot(digits, expected_values, 'r-', label='Benford', marker='o')
        plt.title('Image Générée')
        plt.xlabel('Premier chiffre')
        plt.ylabel('Pourcentage (%)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Graphique pour l'image personnalisée
        plt.subplot(1, 3, 3)
        custom_values = [custom_benford.get(d, 0) for d in digits]
        
        plt.bar(digits, custom_values, alpha=0.5, label='Observé', color='purple')
        plt.plot(digits, expected_values, 'r-', label='Benford', marker='o')
        plt.title('Image Photoshoppée')
        plt.xlabel('Premier chiffre')
        plt.ylabel('Pourcentage (%)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Sauvegarder le graphique en base64
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png', bbox_inches='tight')
        plt.close()
        img_buf.seek(0)
        plot_url = base64.b64encode(img_buf.getvalue()).decode()

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Analyse de Benford - Test d'images</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1, h2 {{
                    color: #333;
                    text-align: center;
                }}
                .images {{
                    display: flex;
                    justify-content: space-between;
                    margin: 20px 0;
                }}
                .image-container {{
                    width: 32%;
                    text-align: center;
                }}
                .image-container img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 4px;
                }}
                .graph {{
                    text-align: center;
                    margin: 20px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #f8f9fa;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Analyse de la loi de Benford sur des images</h1>
                <div class="graph">
                    <h2>Comparaison des distributions de Benford sur des images</h2>
                    <img src="data:image/png;base64,{plot_url}" alt="Graphique de la loi de Benford">
                </div>
                
                <h2>Tableau comparatif</h2>
                <table>
                    <tr>
                        <th>Premier chiffre</th>
                        <th>Benford attendu</th>
                        <th>Image Réelle</th>
                        <th>Image Générée</th>
                        <th>Image Photoshoppé</th>
                    </tr>
                    {''.join(f"""
                    <tr>
                        <td>{digit}</td>
                        <td>{benford_expected[digit]:.1f}%</td>
                        <td>{real_benford.get(digit, 0):.2f}%</td>
                        <td>{fake_benford.get(digit, 0):.2f}%</td>
                        <td>{custom_benford.get(digit, 0):.2f}%</td>
                    </tr>
                    """ for digit in range(1, 10))}
                </table>
                
                <h2>Analyse</h2>
                <p>
                    La loi de Benford prédit que dans de nombreux ensembles de données naturelles, 
                    la distribution des premiers chiffres n'est pas uniforme. Le premier chiffre 1 
                    apparaît environ 30% du temps, tandis que 9 apparaît moins de 5% du temps.
                </p>
                <p>
                    Pour les images, les coefficients DCT (Discrete Cosine Transform) peuvent être 
                    analysés pour voir s'ils suivent la loi de Benford. Les images naturelles ont 
                    tendance à suivre cette loi, tandis que les images générées ou manipulées peuvent 
                    montrer des déviations.
                </p>
                <p>
                    <strong>Écart moyen par rapport à Benford:</strong><br>
                    Image Réelle: {sum(abs(real_benford.get(d, 0) - benford_expected[d]) for d in range(1, 10))/9:.2f}%<br>
                    Image Générée: {sum(abs(fake_benford.get(d, 0) - benford_expected[d]) for d in range(1, 10))/9:.2f}%<br>
                    Image Personnalisée: {sum(abs(custom_benford.get(d, 0) - benford_expected[d]) for d in range(1, 10))/9:.2f}%
                </p>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Les routes suivantes sont des routes API JSON que l'on appelle depuis le notebook test.ipynb
#car sinon les données ne sont pas lues correctement et cela me rend du HTML

@app.get("/recipes/")
async def get_recipes_json():
    """
    Récupère toutes les recettes de la base de données SQL au format JSON.
    
    Returns:
        JSONResponse: Liste de toutes les recettes au format JSON
    """
    try:
        conn, cursor = get_db()
        cursor.execute("SELECT * FROM recette;")
        recipes = cursor.fetchall()
        cursor.close()
        conn.close()
        return JSONResponse(content=recipes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


import decimal
import json

def decimal_to_float(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Fonction utilitaire pour créer des réponses JSON avec gestion des Decimal
def create_json_response(content):
    json_content = json.dumps(content, default=decimal_to_float)
    return JSONResponse(content=json.loads(json_content))

# Modifiez les routes pour utiliser cette fonction

@app.get("/recipe/{recipe_id}/steps")
async def get_recipe_steps_json(recipe_id: int):
    """
    Récupère les étapes de préparation d'une recette spécifique au format JSON.
    
    Args:
        recipe_id (int): Identifiant de la recette
        
    Returns:
        JSONResponse: Dictionnaire contenant l'ID de la recette et la liste des étapes
    """
    try:
        conn, cursor = get_db()
        
        # D'abord vérifier si la recette existe
        check_recipe = "SELECT id FROM recette WHERE id = %s"
        cursor.execute(check_recipe, (recipe_id,))
        recipe = cursor.fetchone()
        
        if not recipe:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Recette non trouvée")
        
        # Si la recette existe, récupérer ses étapes
        sql = """
            SELECT 
                e.id,
                e.numero,
                e.etape as description
            FROM etape e
            WHERE e.recette_id = %s
            ORDER BY e.numero ASC
        """
        cursor.execute(sql, (recipe_id,))
        steps = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not steps:
            raise HTTPException(status_code=404, detail="Aucune étape trouvée pour cette recette")
            
        return JSONResponse(content={
            "recipe_id": recipe_id,
            "steps": steps
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recipe/{recipe_id}/ingredients")
async def get_recipe_ingredients_json(recipe_id: int):
    """
    Récupère la liste des ingrédients d'une recette spécifique au format JSON.
    
    Args:
        recipe_id (int): Identifiant de la recette
        
    Returns:
        JSONResponse: Liste des ingrédients de la recette au format JSON
    """
    try:
        conn, cursor = get_db()
        
        # First check if recipe exists
        check_recipe = "SELECT id FROM recette WHERE id = %s"
        cursor.execute(check_recipe, (recipe_id,))
        recipe = cursor.fetchone()
        
        if not recipe:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        # If recipe exists, get ingredients
        sql = """
            SELECT i.id, i.nom, i.quantite
            FROM ingredient i
            JOIN recette_ingredient ri ON i.id = ri.ingredient_id
            WHERE ri.recette_id = %s;
        """
        cursor.execute(sql, (recipe_id,))
        ingredients = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not ingredients:
            raise HTTPException(status_code=404, detail="No ingredients found for this recipe")
            
        return JSONResponse(content=ingredients)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
