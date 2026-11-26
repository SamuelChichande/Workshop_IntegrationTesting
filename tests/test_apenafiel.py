import pytest

from app.order_service import OrderService, OutOfStockError
from app.payment_gateway import PaymentGateway
from tests.support.fake_db import FakeDb


def test_stock_insuficiente_no_cobra_ni_registra(mocker):
    
    db = FakeDb(stock={"TAZA": 1}, prices={"TAZA": 7.5})
    pasarela = mocker.Mock(spec=PaymentGateway)
    servicio = OrderService(db, pasarela)

    with pytest.raises(OutOfStockError) as excinfo:
        servicio.place_order("TAZA", 5, "tok_fake")

    # El mensaje del error informa lo solicitado y lo disponible.
    assert "solicitado=5" in str(excinfo.value)
    assert "disponible=1" in str(excinfo.value)

    # Aserción clave: el pedido se detuvo antes de cobrar.
    pasarela.charge.assert_not_called()

    # El inventario no cambió y no se registró ningún pedido.
    assert db.get_stock("TAZA") == 1
    assert db.orders == {}