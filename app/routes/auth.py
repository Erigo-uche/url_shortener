from flask import Blueprint, request, redirect, url_for, session, flash, current_app
from app import db, utils

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET","POST"])
def register():
    try:
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]

            if not all([username, email, password]):
                return "All fields required"
      
            password_hash = utils.hashp(password)

           
            db.store_info(username, email, password_hash)
            flash("Account created successfully")
    
            return redirect(url_for("auth.login"))
        
        return "register page"
    
    except Exception as e:
        current_app.logger.exception("Error loading register page: %s", e)
        raise
  

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]

            if not all([email, password]):
                return "Incomplete field"
            
            user = db.valid_p(email)
            if not user:
                flash("Invalid credentials")
                return redirect(url_for("auth.login"))
            
            user_id = user[0]
            p_hash = user[1]

            p_validation = utils.valp(password, p_hash)
            if not p_validation:
                flash("Invalid password")
                return redirect(url_for("auth.login"))
            
            session["user_id"] = user_id

            flash("Login successful")

            return redirect("/dashboard")
        
        return "login page" 
    
    except Exception as e:
        current_app.logger.exception("Error loading login page: %s", e)
        raise
    

@auth_bp.route("/logout")
def logout():
    session.clear()

    flash("Logged out")

    return redirect(url_for("auth.login"))
        
            






