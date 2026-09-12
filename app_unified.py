from flask import Flask, request, render_template_string
import psycopg2
import os
import time
import requests
from prometheus_client import Counter, generate_latest, REGISTRY

app = Flask(__name__)

# -------------------- БАЗА ДАННЫХ --------------------
def get_db_connection():
    for i in range(10):
        try:
            conn = psycopg2.connect(
                host="db",
                database=os.getenv("POSTGRES_DB", "mydb"),
                user=os.getenv("POSTGRES_USER", "myuser"),
                password=os.getenv("POSTGRES_PASSWORD", "mysecretpassword")
            )
            return conn
        except:
            time.sleep(1)
    return None

def init_db():
    conn = get_db_connection()
    if conn is None:
        print("❌ Не удалось подключиться к базе данных!")
        return
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            description TEXT NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Таблица tasks готова")

# -------------------- МОНИТОРИНГ --------------------
def check_service(url):
    try:
        r = requests.get(url, timeout=2)
        return "✅ Жив" if r.status_code == 200 else "❌ Упал"
    except:
        return "❌ Недоступен"

# -------------------- МЕТРИКИ ДЛЯ PROMETHEUS --------------------
request_count = Counter('http_requests_total', 'Total HTTP requests')

@app.route("/metrics")
def metrics():
    request_count.inc()
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain; charset=utf-8'}

# -------------------- ГЛАВНАЯ СТРАНИЦА --------------------
@app.route("/", methods=["GET", "POST"])
def index():
    status1 = check_service("http://site1:80")
    status2 = check_service("http://site2:80")
    
    conn = get_db_connection()
    if conn is None:
        return "❌ Ошибка подключения к базе данных", 500
    
    cur = conn.cursor()
    
    if request.method == "POST":
        description = request.form.get("description")
        if description:
            cur.execute("INSERT INTO tasks (description) VALUES (%s)", (description,))
            conn.commit()
    
    cur.execute("SELECT id, description FROM tasks")
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><title>Дашборд + Заметки</title></head>
    <body>
        <h1>📊 Мониторинг сервисов</h1>
        <ul>
            <li>Первый сайт (порт 8000): {{ status1 }}</li>
            <li>Второй сайт (порт 8001): {{ status2 }}</li>
        </ul>
        <p><a href="/metrics">Посмотреть метрики для Prometheus</a></p>
        
        <hr>
        
        <h1>📝 Мои заметки</h1>
        <form method="POST">
            <input type="text" name="description" placeholder="Что нужно сделать?" size="40">
            <button type="submit">Добавить</button>
        </form>
        <ul>
            {% for task in tasks %}
                <li>{{ task[1] }}</li>
            {% endfor %}
        </ul>
    </body>
    </html>
    """, status1=status1, status2=status2, tasks=tasks)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
