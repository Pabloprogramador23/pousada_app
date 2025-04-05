from django.test import TestCase
from rest_framework.test import APIClient
from datetime import date
from hospedes.models import Hospede
from quartos.models import Quarto
from reservas.models import Reserva

class ReservaTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.hospede = Hospede.objects.create(
            nome="Maria Souza",
            telefone="(87) 99999-1234",
            data_nascimento=date(1990, 5, 1),  # ➕ adicionado
        )

        self.quarto = Quarto.objects.create(
            numero="101",
            tem_ventilador=False
        )
    def test_criar_reserva_basica(self):
        data = {
            "cliente": self.hospede.id,
            "quarto": self.quarto.id,
            "data_checkin": "2025-04-10",
            "data_checkout": "2025-04-13",
            "numero_pessoas": 2,
            "pago_50": True,
            "confirmado": True
        }

        response = self.client.post("/api/reservas/", data, format="json")
        self.assertEqual(response.status_code, 201)
        reserva = Reserva.objects.get(id=response.data["id"])
        self.assertEqual(reserva.valor_total, 80 * 3)

    def test_reserva_conflitante_nao_permitida(self):
        # Reserva inicial
        Reserva.objects.create(
            cliente=self.hospede,
            quarto=self.quarto,
            data_checkin=date(2025, 4, 10),
            data_checkout=date(2025, 4, 13),
            numero_pessoas=2,
            confirmado=True
        )

        # Nova reserva conflitante
        data = {
            "cliente": self.hospede.id,
            "quarto": self.quarto.id,
            "data_checkin": "2025-04-12",  # conflito com a anterior
            "data_checkout": "2025-04-15",
            "numero_pessoas": 2,
            "pago_50": True,
            "confirmado": True
        }

        response = self.client.post("/api/reservas/", data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("O quarto já está reservado", str(response.data))
