
from app.order_service import OrderService
from app.payment_gateway import PaymentGateway
from tests.support.fake_db import FakeDb


def test_pago_rechazado_conserva_stock_y_no_registra_pedido(mocker, capsys):
    """
    Clasificación: Top-down.
    Justificación: se inicia en OrderService real y se sustituyen
    las dependencias inferiores.
    Componentes reales: OrderService.
    Sustituidos: FakeDb y Mock de PaymentGateway configurado para rechazar.
    Resultado esperado: rechazo informado, stock conservado y sin pedidos.
    """

    db = FakeDb(stock={"TAZA": 9}, prices={"TAZA": 7.5})

    pasarela = mocker.Mock(spec=PaymentGateway)
    pasarela.charge.return_value = {
        "approved": False,
        "reason": "insufficient_funds"
    }

    servicio = OrderService(db, pasarela)

    servicio.place_order("TAZA", 2, "tok_fake")

    pasarela.charge.assert_called_once()

    assert "Pago rechazado" in capsys.readouterr().out

    # Comprobamos ambas condiciones sin detener la prueba en la primera.
    errores = []

    if db.get_stock("TAZA") != 9:
        errores.append(f"Stock incorrecto: {db.get_stock('TAZA')}, esperado: 9")

    if db.orders != {}:
        errores.append(f"Se registraron pedidos: {db.orders}")

    assert not errores, "\n".join(errores)

