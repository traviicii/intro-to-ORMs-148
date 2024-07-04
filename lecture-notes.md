
# Lecture: Introduction to Object-Relational Mappers (ORMs) with Flask and SQLAlchemy

## Useful Links:

[SQLAlchemy Quickstart Guide](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)

[SQLAlchemy Mapped Class Configuration](https://docs.sqlalchemy.org/en/20/orm/mapper_config.html)

[SQLAlchemy Relationship Configuration](https://docs.sqlalchemy.org/en/20/orm/relationships.html)

[SQLAlchemy Querying Guide](https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html)

[Understanding Connection Strings](https://www.prisma.io/dataguide/postgresql/short-guides/connection-uris)

## Object Relational Mappers (ORM)
**Definition**: ORMs serve as a link between our application/API and its database, managing the interactions between the two.

### Benefits of ORMs
- **Ease of Use**: No longer needing to write complex SQL queries.
- **Efficiency**: ORMs optimize database interactions.
- **Maintainability**: Working in tandem with database schemas, an ORM can seamlessly handle changes to fields of the database tables.

## Flask-SQLAlchemy
**Definition**: Flask-SQLAlchemy is an extension of Flask that serves as an ORM, allowing us to connect from our Flask app to our database, streamlining these interactions.

### Integrating Flask-SQLAlchemy
1. **Create a virtual environment in your project folder, and activate the venv**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
2. **Install all necessary packages**
    ```sh
    pip install flask flask-sqlalchemy flask-marshmallow marshmallow-sqlalchemy mysql-connector-python
    ```
