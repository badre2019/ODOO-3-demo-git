# Utiliser PostgreSQL avec Python — psycopg

`psycopg` est une bibliothèque Python qui permet de communiquer directement avec une base de données PostgreSQL.

On va l'utiliser pour exécuter des requêtes SQL depuis Python, sans ORM ni SQLAlchemy.

## 1. Installation

```bash
pip install "psycopg[binary]"
```

Il faut également avoir PostgreSQL installé et une base de données créée.

## 2. Se connecter à PostgreSQL

On commence par créer une fonction qui retourne une connexion à notre base de données.

```python
import psycopg

def get_connection():
    return psycopg.connect(
        dbname="odoo_training",
        user="postgres",
        password="postgres",
        host="localhost",
        port=5432
    )
```

Cette fonction ouvre une connexion et la retourne. Elle ne la ferme pas.

On pourra ensuite l'utiliser dans notre programme :

```python
with get_connection() as conn:
    # Nos opérations SQL ici
    pass
```

Le `with` permet de gérer automatiquement la connexion et la transaction :

- Si tout se passe bien, les modifications sont validées (`commit`).
- Si une exception survient, les modifications sont annulées (`rollback`).
- À la sortie du bloc, la connexion est fermée.

On va donc ouvrir **une seule connexion** et la passer à nos différentes fonctions.

## 3. Créer un curseur

Pour exécuter une requête SQL, on utilise un `cursor`.

```python
with get_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM developers")
        developers = cursor.fetchall()

    print(developers)
```

Le curseur permet d'envoyer des requêtes SQL à PostgreSQL et de récupérer leurs résultats.

`execute()` exécute la requête, `fetchall()` récupère toutes les lignes et `fetchone()` récupère une seule ligne.

Le `with conn.cursor()` ferme automatiquement le curseur à la fin du bloc, mais ne ferme pas la connexion.

## 4. Les opérations CRUD

Pour les exemples, on considère qu'on possède cette table :

```sql
CREATE TABLE developers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);
```

### SELECT — Récupérer tous les développeurs

```python
def get_all(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM developers")
        return cursor.fetchall()
```

### SELECT — Récupérer un développeur par ID

```python
def get_by_id(conn, developer_id):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM developers WHERE id = %s",
            (developer_id,)
        )
        return cursor.fetchone()
```

On utilise `%s` pour passer des paramètres à une requête SQL.

Les valeurs sont transmises séparément de la requête, ce qui permet notamment d'éviter les injections SQL.

Attention : `(developer_id,)` est un tuple contenant un seul élément. La virgule est nécessaire.

### INSERT — Ajouter un développeur

```python
def create_developer(conn, name):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO developers (name)
            VALUES (%s)
            RETURNING id
            """,
            (name,)
        )
        return cursor.fetchone()[0]
```

`RETURNING id` permet de récupérer l'identifiant généré par PostgreSQL.

### UPDATE — Modifier un développeur

```python
def update_developer(conn, developer_id, name):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE developers
            SET name = %s
            WHERE id = %s
            """,
            (name, developer_id)
        )
        return cursor.rowcount
```

`rowcount` indique le nombre de lignes affectées par la requête.

### DELETE — Supprimer un développeur

```python
def delete_developer(conn, developer_id):
    with conn.cursor() as cursor:
        cursor.execute(
            "DELETE FROM developers WHERE id = %s",
            (developer_id,)
        )
        return cursor.rowcount
```

## 5. Les jointures

Imaginons une deuxième table `projects`, liée à `developers`.

```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    developer_id INTEGER REFERENCES developers(id)
);
```

On peut récupérer les projets avec le nom de leur développeur grâce à une jointure :

```python
def get_projects(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                projects.title,
                developers.name
            FROM projects
            JOIN developers
                ON projects.developer_id = developers.id
        """)
        return cursor.fetchall()
```

Il n'y a rien de particulier à faire côté Python : on écrit simplement notre requête SQL comme d'habitude.

## 6. Utiliser nos fonctions

Maintenant qu'on a nos fonctions, on peut les appeler depuis notre programme principal.

```python
def main():
    with get_connection() as conn:
        # Ajouter un développeur
        new_id = create_developer(conn, "Alice")

        # Récupérer tous les développeurs
        print(get_all(conn))

        # Récupérer Alice
        print(get_by_id(conn, new_id))

        # Modifier Alice
        update_developer(conn, new_id, "Alice Dupont")

        # Supprimer Alice
        delete_developer(conn, new_id)


if __name__ == "__main__":
    main()
```

On ouvre une connexion au début du `main()` et on la réutilise pour toutes nos opérations.

## 7. Les transactions

Une transaction regroupe plusieurs opérations SQL.

Dans notre exemple, toutes les requêtes exécutées dans le bloc `with get_connection() as conn:` font partie de la même transaction, tant qu'on ne valide ou n'annule pas celle-ci manuellement.

Si une requête échoue et provoque une exception qui sort du bloc, PostgreSQL annule les modifications non validées.

```python
with get_connection() as conn:
    create_developer(conn, "Alice")
    create_developer(conn, "Bob")
```

Si les deux insertions réussissent, elles sont validées ensemble à la sortie du `with`.

Si la deuxième échoue, la première est également annulée.

C'est ce qu'on appelle l'**atomicité** d'une transaction : soit toutes les opérations sont validées, soit aucune ne l'est.

Attention : si on intercepte une exception à l'intérieur du bloc, il faut gérer correctement la transaction, notamment avec `rollback()` si nécessaire.

## À retenir

- `psycopg.connect()` ouvre une connexion PostgreSQL.
- `conn.cursor()` crée un curseur pour exécuter du SQL.
- `cursor.execute()` exécute une requête.
- `fetchone()` récupère une ligne, `fetchall()` récupère toutes les lignes.
- `%s` permet de passer des paramètres de manière sécurisée.
- `with conn` gère la transaction et ferme la connexion à la sortie du bloc.
- `with conn.cursor()` ferme le curseur, pas la connexion.
- On peut passer la même connexion à plusieurs fonctions pour effectuer plusieurs opérations dans une seule transaction.

Pour ce mini-projet, on garde volontairement une seule connexion et une structure simple. C'est suffisant pour une application console qui exécute ses opérations les unes après les autres.