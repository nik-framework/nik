from nik.views.elements import Div


def view(patient_id: str):
    return Div(
        f"Patient ID={patient_id}",
    )
