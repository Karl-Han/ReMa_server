# ReMa server site

This is the server site of Android Application [ReMa](https://github.com/android-app-development-course/2019-a20-ReMa).

## How to use

1. Create virtual environment and install requirements: `pip install -r requirements.txt`
2. Initialize MySQL and initialize rema database with `mysql -u rema < schema.sql`
3. Run on the server site. `waitress-serve --call 'rema:create_app'`
