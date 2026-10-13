import os
import pickle
import pandas as pd

from flask import Flask, request, render_template

app = Flask(__name__)

# Load the trained model from the project folder
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "advisor_model.pkl"
)

with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)


def get_advice(cgpa, attendance, study_hours, carryovers, standing):
    tips = []

    if cgpa < 2.0:
        tips.append(
            "Consider meeting your level adviser to discuss "
            "ways to improve your CGPA."
        )

    if attendance < 75:
        tips.append(
            "Your attendance is below 75%. Check your school's "
            "attendance requirements."
        )

    if study_hours < 10:
        tips.append(
            "Consider setting aside more time each week for studying."
        )

    if carryovers > 0:
        tips.append(
            f"Make a study plan to clear your {int(carryovers)} "
            "carryover course(s)."
        )

    if standing == "Good standing" and not tips:
        tips.append(
            "Keep up your study habits and monitor your academic progress."
        )

    if not tips:
        tips.append(
            "Maintain your study routine and review your academic goals."
        )

    return tips


@app.route("/", methods=["GET", "POST"])
def home():
    standing = None
    tips = []
    error = None
    values = {}

    if request.method == "POST":
        try:
            cgpa = float(request.form["cgpa"])
            attendance = float(request.form["attendance"])
            study_hours = float(request.form["study_hours"])
            carryovers = int(request.form["carryovers"])

            values = {
                "cgpa": cgpa,
                "attendance": attendance,
                "study_hours": study_hours,
                "carryovers": carryovers,
            }

            if not 0 <= cgpa <= 5:
                raise ValueError("CGPA must be between 0 and 5.")

            if not 0 <= attendance <= 100:
                raise ValueError("Attendance must be between 0 and 100.")

            if not 0 <= study_hours <= 80:
                raise ValueError("Study hours must be between 0 and 80.")

            if carryovers < 0:
                raise ValueError("Carryovers cannot be negative.")

            student_data = pd.DataFrame(
                [[cgpa, attendance, study_hours, carryovers]],
                columns=[
                    "cgpa",
                    "attendance",
                    "study_hours",
                    "carryovers",
                ],
            )

            standing = str(model.predict(student_data)[0])

            tips = get_advice(
                cgpa,
                attendance,
                study_hours,
                carryovers,
                standing,
            )

        except (ValueError, TypeError):
            error = (
                "Please enter valid numbers within the allowed ranges."
            )

    return render_template(
        "index.html",
        standing=standing,
        tips=tips,
        error=error,
        values=values,
    )


if __name__ == "__main__":
    app.run(debug=True)