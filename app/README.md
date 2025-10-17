# Site personnel Streamlit — Jean Direl

## Prérequis

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

## Administration

1. Copiez `.streamlit/secrets.toml.example` vers `.streamlit/secrets.toml`.
2. Générer un mot de passe haché :

```bash
python -m utils.auth
```

3. Collez le hash dans `admin_password_hash`, ajustez l'email.
4. Lancez l'application et ouvrez l’onglet **Admin**.

## Contenu & médias

- Les données sont stockées dans `data/content.json`.
- Les messages du formulaire de contact sont dans `data/messages.json`.
- Remplacez `assets/profile.jpg` et `assets/cv_jean_direl.pdf` par vos fichiers (l’admin permet de les mettre à jour).
- Les fichiers uploadés sont enregistrés dans `assets/uploads/`.

## SMTP optionnel

Renseignez la section `[smtp]` du fichier `secrets.toml` pour activer l’envoi de notifications email à la réception d’un message de contact. Sans configuration SMTP, le formulaire stocke les messages et propose un lien mailto.
