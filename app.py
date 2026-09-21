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

    photo_url = f"https://{bucket_name}.s3.eu-north-1.amazonaws.com/{filename}"

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
        (name, email, place_name, location, category, description, photo_url)
    )

    db.commit()
    cursor.close()
    db.close()

    return "Place submitted successfully!"


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )