# Gradient Geek

Pour installer le projet en local il fait :

- Créer son environnement virtuel

- Installer les librairies nécessaires

```
pip install -r requirements.txt
```

- Installer la BDD et les migrations

```
python manage.py makemigrations
python manage.py migrate
```

- Charger la BDD avec le fichier CSV

```
python manage.py runscript load_data
```

- Lancer le serveur en local

```
python manage.py runserver
```

Aller sur l'adresse => http://127.0.0.1:8000/
