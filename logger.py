import csv
import os


def save_result(password, attempts, time_taken):

    file_exists = os.path.isfile("results.csv")

    with open("results.csv", "a", newline="") as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Password",
                "Attempts",
                "Time"
            ])

        writer.writerow([
            password,
            attempts,
            time_taken
        ])