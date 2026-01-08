from flask import Flask, render_template, request, redirect, url_for, session
import numpy as np

from markowitz import markowitz_optimize
from realtime_market import get_market_data

app = Flask(__name__)
app.secret_key = "sicuan"


# ======================
# FINANCIAL FUNCTION
# ======================

def future_value(pv, r, n):
    return pv * ((1 + r) ** n)


# ======================
# HOME
# ======================

@app.route("/")
def home():
    return render_template("home.html")


# ======================
# START FORM
# ======================

@app.route("/start", methods=["GET", "POST"])
def start():
    if request.method == "POST":
        session["user"] = {
            "nama": request.form.get("nama"),
            "email": request.form.get("email")
        }
        return redirect(url_for("profil_form"))

    return render_template("form.html")


# ======================
# PROFIL RISIKO (8 SOAL)
# ======================

@app.route("/profil", methods=["GET", "POST"])
def profil_form():
    if request.method == "POST":
        try:
            total = sum(int(request.form.get(f"q{i}", 0)) for i in range(1, 9))

            if total <= 14:
                profil = "konservatif"
            elif total <= 21:
                profil = "moderat"
            else:
                profil = "agresif"

            session["profil"] = profil
            return redirect(url_for("advisor"))

        except:
            return redirect(url_for("profil_form"))

    return render_template("profil_form.html")


# ======================
# ADVISOR (MAIN ENGINE)
# ======================

@app.route("/advisor", methods=["GET", "POST"])
def advisor():
    if request.method == "POST":

        # === AMBIL DATA FORM ===
        tujuan = request.form.get("tujuan")

        dana = int(request.form.get("dana_awal"))
        target = int(request.form.get("harga"))

        waktu_angka = int(request.form.get("waktu_angka"))
        waktu_satuan = request.form.get("waktu_satuan")

        if waktu_satuan == "tahun":
            bulan = waktu_angka * 12
        else:
            bulan = waktu_angka

        profil = session.get("profil", "moderat")

        # =====================
        # RETURN + INFLASI
        # =====================

        inflasi_bulanan = 0.003  # 0.3% / bulan

        if profil == "konservatif":
            r = 0.008     # ~1% per bulan
        elif profil == "moderat":
            r = 0.015
        else:
            r = 0.03

        # return sudah dianggap NET inflasi
        fv = future_value(dana, r, bulan)

        realistis = fv >= target

        kebutuhan_per_bulan = max(0, (target - dana) // max(1, bulan))

        # =====================
        # MARKOWITZ PORTFOLIO
        # =====================

        returns = np.array([0.15, 0.10, 0.05])
        cov = np.array([
            [0.10, 0.02, 0.01],
            [0.02, 0.08, 0.01],
            [0.01, 0.01, 0.03]
        ])

        weights = markowitz_optimize(returns, cov)

        alokasi = [
            ("Saham Growth", round(weights[0]*100, 1), int(dana * weights[0])),
            ("Bluechip", round(weights[1]*100, 1), int(dana * weights[1])),
            ("Obligasi", round(weights[2]*100, 1), int(dana * weights[2]))
        ]

        # =====================
        # MARKET CONDITION
        # =====================

        market = get_market_data()

        # =====================
        # RESULT OBJECT
        # =====================

        result = {
            "tujuan": tujuan,
            "dana": dana,
            "target": target,
            "bulan": bulan,
            "profil": profil.capitalize(),

            "fv": int(fv),
            "return_bulanan": round(r * 100, 2),
            "inflasi": round(inflasi_bulanan * 100, 2),

            "kebutuhan_per_bulan": kebutuhan_per_bulan,
            "realistis": realistis,

            "alokasi": alokasi,
            "market": market
        }

        session["result"] = result
        return render_template("result.html", r=result)

    return render_template("advisor.html")


# ======================
# RUN APP
# ======================

if __name__ == "__main__":
    app.run(debug=True, port=10000)
