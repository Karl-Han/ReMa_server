# ReMa server site

This is the server site of Android Application ReMa.

## How to use

1. Create virtual environment: `pip install < requirements.txt`
2. Initialize MySQL with `mysql -u <user> < schema.sql`
3. Run on the server site. `waitress-serve --call 'rema:create_app'`

