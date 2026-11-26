import pytest

from app.order_service import OrderService, OutOfStockError
from app.payment_gateway import PaymentGateway
from tests.support.fake_db import FakeDb


def test_stock_insuficiente_no_cobra_ni_registra(mocker):
    '''Clasificación: Top-down
        Justificación: se empieza en la capa de lógica de negocio (OrderService), que es el
        componente real más alto incluido, y se sustituyen las capas inferiores
        (persistencia y pasarela de pagos), que aún no están desplegadas.
        Capa de inicio: OrderService
        Componentes reales: OrderService
        Dependencias sustituidas: FakeDb (stock 1, precio 7.5), Mock(spec=PaymentGateway)
         de entrada: TAZA, 5, tok_fake, stock 1, precio 7.5
        Resultado esperado: OutOfStockError, pasarela sin llamadas, stock 1, sin pedidos
        Resultado obtenido: PASSED
        - Confirmó que, con stock insuficiente, OrderService detiene el pedido antes del
            cobro: lanza OutOfStockError con lo solicitado (5) y lo disponible (1), no llama
            a PaymentGateway.charge, no modifica el inventario y no registra ningún pedido.
    '''
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