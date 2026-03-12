from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__)

cart = []

CSV_PATH = os.path.join("data", "products.csv")

def load_products():
    products = []
    with open(CSV_PATH, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            products.append({
                "item_code": row["item_code"],
                "style": row["style"],
                "sizes": row["sizes"],
                "colour": row["colour"],
                "pairs_per_bag": row["pairs_per_bag"],
                "bag_price": float(row["bag_price"]),
                "bg_color": row["bg_color"]
            })
    return products

@app.route("/", methods=["GET", "POST"])
def index():
    global cart
    products = load_products()

    if request.method == "POST":
        code = request.form.get("item_code")
        qty = int(request.form.get("qty"))

        product = next((p for p in products if p["item_code"] == code), None)
        if product:
            amount = qty * product["bag_price"]

            # Fill first empty slot if available
            for i in range(len(cart)):
                if cart[i] is None:
                    cart[i] = {
                        "description": f'{product["style"]} {product["sizes"]} {product["colour"]}',
                        "qty": qty,
                        "amount": amount,
                        "bg_color": product["bg_color"]
                    }
                    break
            else:
                cart.append({
                    "description": f'{product["style"]} {product["sizes"]} {product["colour"]}',
                    "qty": qty,
                    "amount": amount,
                    "bg_color": product["bg_color"]
                })

        return redirect(url_for("index"))

    total_qty = sum(i["qty"] for i in cart if i)
    total_amount = sum(i["amount"] for i in cart if i)
    subsidy_rate = 1700
    subsidy_total = subsidy_rate * total_qty
    final_total = total_amount - subsidy_total

    return render_template(
        "index.html",
        products=products,
        cart=cart,
        total_qty=total_qty,
        total_amount=total_amount,
        subsidy=subsidy_total,
        final_total=final_total
    )

@app.route("/delete/<int:index>")
def delete_item(index):
    global cart
    if 0 <= index < len(cart):
        cart[index] = None
    return redirect(url_for("index"))

@app.route("/clear")
def clear():
    global cart
    cart = []
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)