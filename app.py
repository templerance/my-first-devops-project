from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def hello():
    name = os.getenv("MY_NAME", "Гость")
    age = os.getenv("MY_AGE", "неизвестен")
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><title>Flask + Docker</title></head>
    <body>
        <h1 style="color:purple;">Привет, {name}!</h1>
        <p>Тебе {age} лет, и ты только что запустил Python в контейнере!</p>
        <p>Это работает через переменные окружения</p>
    </body>
    </html>
    """
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

