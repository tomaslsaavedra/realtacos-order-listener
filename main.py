import os, csv, datetime, requests
from flask import Flask, request, Response

app = Flask(__name__)

CLICKUP_TOKEN = os.getenv("CLICKUP_TOKEN")
CLICKUP_LIST  = os.getenv("CLICKUP_LIST")

# Pegar los IDs que copiaste del Playground
CF_IDPEDIDO = os.getenv("CF_IDPEDIDO")
CF_SUCURSAL = os.getenv("CF_SUCURSAL")
CF_HORA     = os.getenv("CF_HORA")
CF_ITEMS    = os.getenv("CF_ITEMS")
CF_NOTAS    = os.getenv("CF_NOTAS")
CF_CLIENTE  = os.getenv("CF_CLIENTE")

@app.route("/ue_webhook", methods=["POST"])
def ue_webhook():
    order = request.json["event_body"]

    cliente = f"{order['eater']['first_name']} {order['eater']['last_name']}".strip()

    body = {
      "name": f"Pedido {order['id']} – {order['store']['name']}",
      "status": "Pendiente",
      "custom_fields":[
        {"id": CF_IDPEDIDO, "value": order["id"]},
        {"id": CF_SUCURSAL, "value": order["store"]["name"]},
        {"id": CF_HORA, "value": order["accepted_at"]},
        {"id": CF_ITEMS, "value": ", ".join([f"{x['quantity']} {x['title']}" for x in order['items']])},
        {"id": CF_NOTAS, "value": order.get("delivery_notes","")},
        {"id": CF_CLIENTE,"value": cliente}
      ]
    }
    requests.post(
        f"https://api.clickup.com/api/v2/list/{CLICKUP_LIST}/task",
        headers={"Authorization": CLICKUP_TOKEN},
        json=body, timeout=10
    )

    with open("clientes_pedidos.csv", "a", newline="") as f:
        csv.DictWriter(f, fieldnames=["fecha","order_id","cliente"]).writerow({
            "fecha": datetime.datetime.utcnow().isoformat(),
            "order_id": order["id"],
            "cliente": cliente
        })
    return Response(status=200)

# Render usará gunicorn, pero si lo corrés local:
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
