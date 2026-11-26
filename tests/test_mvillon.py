import pytest
from app.order_service import OrderService
from app.payment_gateway import PaymentGateway
from tests.support.fake_db import FakeDb


def test_pedido_exitoso_registra_y_descuenta_stock(mocker):
    """
    Clasificación: Top-down
    Justificación: se inicia en OrderService (capa de negocio) y se sustituyen
    las capas inferiores que no están desplegadas.
    Componentes reales: OrderService
    Sustituidos: FakeDb, Mock(spec=PaymentGateway)
    """
    db = FakeDb(stock={"TAZA": 9}, prices={"TAZA": 7.5})
    pasarela = mocker.Mock(spec=PaymentGateway)
    pasarela.charge.return_value = {
        "approved": True,
        "transaction_id": "tx_fake",
    }
    servicio = OrderService(db, pasarela)
    resultado = servicio.place_order("TAZA", 2, "tok_fake")

    pasarela.charge.assert_called_once()
    assert pasarela.charge.call_args.args[1] == pytest.approx(17.4)
    assert db.get_stock("TAZA") == 7
    assert len(db.orders) == 1
    assert next(iter(db.orders.values()))["total"] == pytest.approx(17.4)
    assert resultado["status"] == "CONFIRMED"