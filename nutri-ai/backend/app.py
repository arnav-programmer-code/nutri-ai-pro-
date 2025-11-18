from flask import Flask, render_template, request, redirect, jsonify
from pymongo import MongoClient
import google.generativeai as genai
import json

app = Flask(
    __name__,
    template_folder="../",
    static_folder="../",
    static_url_path=""
)

# --------------------------------------------
# MONGO DB
# --------------------------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["nutri_ai"]
users = db["users"]

# --------------------------------------------
# GEMINI SETUP (ALL IN THIS FILE)
# --------------------------------------------
genai.configure(api_key="AIzaSyC0WoWaK25l9U2YzuEheuY4GGWolcxjvLs")
model = genai.GenerativeModel("gemini-2.5-flash")

def clean(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()
    text = text.replace(",}", "}").replace(",]", "]")
    return text

def analyze_food_text(food):
    prompt = (
        f"Analyze the food: {food}. "
        "Return ONLY valid JSON with keys: "
        "{\"calories\":\"\",\"protein\":\"\",\"carbs\":\"\",\"fat\":\"\",\"note\":\"\"}"
    )

    res = model.generate_content(prompt)
    return clean(res.text)

def analyze_food_image(image_bytes):
    prompt = (
        "Analyze this food image and return ONLY valid JSON with keys: "
        "{\"calories\":\"\",\"protein\":\"\",\"carbs\":\"\",\"fat\":\"\",\"note\":\"\"}"
    )

    res = model.generate_content([
        prompt,
        {"mime_type": "image/jpeg", "data": image_bytes}
    ])

    return clean(res.text)

# --------------------------------------------
# AUTH ROUTES
# --------------------------------------------


@app.route("/")
def home():
    return render_template("login.html")

@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_user():
    email = request.form.get("email")
    password = request.form.get("password")
    name = request.form.get("name")

    if users.find_one({"email": email}):
        return "Email already exists"

    users.insert_one({
        "email": email,
        "password": password,
        "name": name
    })

    return redirect("/")

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_user():
    email = request.form.get("email")
    password = request.form.get("password")

    user = users.find_one({"email": email})

    if not user or user["password"] != password:
        return "Invalid email or password"

    return redirect(f"/dashboard?user={user['name']}")

@app.route("/dashboard")
def dashboard():
    username = request.args.get("user")
    return render_template("dashboard.html", user=username)

# --------------------------------------------
# GEMINI API ROUTES (FRONTEND CALLS THESE)
# --------------------------------------------
@app.route("/analyze_food", methods=["POST"])
def analyze_food_route():
    food = request.form.get("food")
    data = analyze_food_text(food)
    return data   # raw JSON string

@app.route("/analyze_image", methods=["POST"])
def analyze_image_route():
    img = request.files["image"]
    data = analyze_food_image(img.read())
    return data   # raw JSON string

@app.route("/ai_chat", methods=["POST"])
def ai_chat():
    try:
        prompt = request.form.get("prompt")
        if not prompt:
            return "No prompt received"

        result = model.generate_content(prompt)

        if hasattr(result, "text"):
            return result.text
        else:
            return "AI returned empty response."

    except Exception as e:
        return f"Error: {str(e)}"




# --------------------------------------------
# RUN APP
# --------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
