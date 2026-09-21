from flask import Flask, render_template, request
import boto3
import pymysql
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

bucket_name = os.environ["S3_BUCKET_NAME"]
db_host = os.environ["DB_HOST"]
db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_name = os.environ["DB_NAME"]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/places")
def places():
    db = pymysql.connect(
        host=db_host,
        port=3306,
        user=db_user,
        password=db_password,
        database=db_name
    )

    cursor = db.cursor()

    cursor.execute("""
        SELECT place_name, location, category, description, photo_url
        FROM places
        ORDER BY id DESC
    """)

    places = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("places.html", places=places)


@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    email = request.form["email"]
    place_name = request.form["place_name"]
    location = request.form["location"]
    category = request.form["category"]
    description = request.form["description"]

    photo = request.files["photo"]
    filename = secure_filename(photo.filename)

    s3 = boto3.client("s3")

    s3.upload_fileobj(
        photo,
        bucket_name,
        filename,
        ExtraArgs={"ContentType": photo.content_type}
    )

    photo_url = (
        f"https://{bucket_name}.s3.eu-north-1.amazonaws.com/{filename}"
    )

    db = pymysql.connect(
        host=db_host,
        port=3306,
        user=db_user,
        password=db_password,
        database=db_name
    )

    cursor = db.cursor()

    sql = """
    INSERT INTO places
    (name, email, place_name, location, category, description, photo_url)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(
        sql,
        (
            name,
            email,
            place_name,
            location,
            category,
            description,
            photo_url
        )
    )

    db.commit()
    cursor.close()
    db.close()

    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>Submission Successful</title>

        <style>
            * {
                box-sizing: border-box;
            }

            body {
                font-family: Arial, sans-serif;
                background: #f4f7fb;
                margin: 0;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }

            .success-card {
                background: white;
                width: 100%;
                max-width: 520px;
                padding: 45px 35px;
                border-radius: 16px;
                text-align: center;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
            }

            .icon {
                font-size: 60px;
                margin-bottom: 15px;
            }

            h1 {
                color: #166534;
                margin-bottom: 12px;
            }

            p {
                color: #6b7280;
                line-height: 1.6;
                margin-bottom: 28px;
            }

            .buttons {
                display: flex;
                justify-content: center;
                gap: 12px;
                flex-wrap: wrap;
            }

            a {
                display: inline-block;
                padding: 13px 25px;
                background: #2563eb;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
            }

            a:hover {
                background: #1d4ed8;
            }

            .places-link {
                background: #0f766e;
            }

            .places-link:hover {
                background: #0d5f59;
            }
        </style>
    </head>

    <body>

        <div class="success-card">

            <div class="icon">✅</div>

            <h1>Place Submitted Successfully!</h1>

            <p>
                Thank you for sharing a hidden place with
                the Hidden Places Explorer community.
            </p>

            <div class="buttons">
                <a href="/">Submit Another Place</a>
                <a href="/places" class="places-link">View Hidden Places</a>
            </div>

        </div>

    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )