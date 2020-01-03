# ReMa server site

This is the server site of Android Application ReMa.

## How to use

1. Create virtual environment: `pip install -r requirements.txt`
2. Initialize MySQL and initialize rema database with `mysql -u <user> < schema.sql`
3. Run on the server site. `waitress-serve --call 'rema:create_app'`
