from nik.server.response import Response
from nik.views.elements import Div


def action():
    return Response("Action performed")


def view(patient_id, appointment_id):
    return Div(
        f"Patient ID={patient_id}, Appointment ID={appointment_id}",
    )
