from setuptools import setup, find_packages

setup(
    name="city_tagger",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'requests',
        'sqlalchemy',
        'flask',
        'python-dotenv',
        'stripe',
        'bcrypt',
        'PyJWT',
        'Flask-Mail',
        'alembic',
        'psycopg2-binary',
        'Flask-Login',
        'supabase',
        'gunicorn',
        'flask-cors'
    ],
) 