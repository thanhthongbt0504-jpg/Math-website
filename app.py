from flask import Flask, render_template, request, session, redirect, url_for
import random
import sympy as sp

app = Flask(__name__)
app.secret_key = "toan8-luyen-tap-secret-key"
x, y = sp.symbols("x y")

TOPICS = {
    "rut_gon": "Thu gọn biểu thức",
    "nhan_don_thuc": "Nhân đơn thức với đa thức",
    "nhan_hai_da_thuc": "Nhân hai đa thức",
    "cong_tru": "Cộng, trừ đa thức",
    "tim_xy": "Tìm x, y",
}

def poly_text(expr):
    return str(sp.expand(expr)).replace("**", "^").replace("*", "")

def make_question(topic, level):
    a = random.randint(2, 6) if level == "easy" else random.randint(3, 9)
    b = random.randint(1, 5)
    c = random.randint(1, 6)
    d = random.randint(1, 5)
    p = random.choice([-1, 1])
    if topic == "rut_gon":
        expr = x*(x+a) + b*x*(x-c) - x*((b+1)*x+d)
        return f"Thu gọn: {poly_text(expr)}", poly_text(sp.expand(expr)), "Khai triển từng tích, rồi gộp các hạng tử đồng dạng."
    if topic == "nhan_don_thuc":
        expr = (a*x*y) * (b*x - c*y + d)
        return f"Thực hiện phép nhân: {poly_text(expr)}", poly_text(sp.expand(expr)), "Nhân đơn thức với từng hạng tử trong ngoặc."
    if topic == "nhan_hai_da_thuc":
        expr = (x + p*a*y) * (b*x - c*y)
        return f"Khai triển và thu gọn: ({poly_text(x + p*a*y)})({poly_text(b*x-c*y)})", poly_text(sp.expand(expr)), "Nhân mỗi hạng tử của đa thức thứ nhất với từng hạng tử của đa thức thứ hai."
    if topic == "cong_tru":
        e1 = a*x**2 + b*x*y - c*y**2
        e2 = d*x**2 - b*x*y + a*y**2
        sign = random.choice([1, -1])
        expr = e1 + sign*e2
        op = "+" if sign == 1 else "-"
        return f"Tính: ({poly_text(e1)}) {op} ({poly_text(e2)})", poly_text(sp.expand(expr)), "Bỏ ngoặc đúng quy tắc dấu, sau đó gộp các hạng tử đồng dạng."
    # Simple system with integer solution
    sx, sy = random.randint(-4, 5), random.randint(-4, 5)
    m, n = random.randint(1, 4), random.randint(1, 4)
    r1, r2 = m*sx + n*sy, n*sx - m*sy
    return f"Tìm x, y biết: {m}x + {n}y = {r1};  {n}x - {m}y = {r2}.", f"x = {sx}; y = {sy}", "Có thể dùng phương pháp cộng đại số hoặc thế để giải hệ."

@app.route("/", methods=["GET", "POST"])
def index():
    topic = request.values.get("topic", "rut_gon")
    level = request.values.get("level", "easy")
    if topic not in TOPICS:
        topic = "rut_gon"
    if level not in ("easy", "medium", "hard"):
        level = "easy"
    if request.method == "POST":
        action = request.form.get("action")
        if action == "new":
            return redirect(url_for("index", topic=topic, level=level))
        if action == "check":
            session["show_answer"] = True
            session["last_topic"] = topic
            session["last_level"] = level
    # Generate stable question until user asks for another one
    key = f"question_{topic}_{level}"
    if request.args.get("fresh") == "1" or key not in session:
        question, answer, explanation = make_question(topic, level)
        session[key] = {"question": question, "answer": answer, "explanation": explanation}
        session["show_answer"] = False
    q = session[key]
    if request.method == "POST" and request.form.get("action") == "new":
        pass
    return render_template("index.html", topics=TOPICS, topic=topic, level=level, q=q,
                           show_answer=session.get("show_answer", False))

@app.route("/new")
def new_question():
    topic = request.args.get("topic", "rut_gon")
    level = request.args.get("level", "easy")
    session.pop(f"question_{topic}_{level}", None)
    session["show_answer"] = False
    return redirect(url_for("index", topic=topic, level=level, fresh=1))

if __name__ == "__main__":
    app.run(debug=True)
