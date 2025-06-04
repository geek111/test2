from threading import Thread
from flask import Flask, request, redirect, url_for, render_template_string

from price_tracker.tracker import PriceTracker
from price_tracker.shops.shop_a import ShopA
from price_tracker.shops.shop_b import ShopB

app = Flask(__name__)
tracker = PriceTracker('products.json', interval=3600)
tracker.register_shop('shopa', ShopA())
tracker.register_shop('shopb', ShopB())

# start background price checking
def start_background_tracker():
    Thread(target=tracker.run, daemon=True).start()

start_background_tracker()

INDEX_TEMPLATE = """
<!doctype html>
<title>Price Tracker</title>
<h1>Tracked Products</h1>
<ul>
  {% for p in products %}
  <li>{{ p.name }} - {{ p.last_price }} ({{ p.shop }})</li>
  {% endfor %}
</ul>
<h2>Add Product</h2>
<form method="post" action="{{ url_for('add_product') }}">
  Name: <input name="name"><br>
  URL: <input name="url"><br>
  Shop:
  <select name="shop">
    {% for s in shops %}
    <option value="{{ s }}">{{ s }}</option>
    {% endfor %}
  </select>
  <button type="submit">Add</button>
</form>
<p><a href="{{ url_for('check_now') }}">Check prices now</a></p>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_TEMPLATE, products=tracker.store.products, shops=tracker.shops.keys())

@app.route('/add', methods=['POST'])
def add_product():
    tracker.add_product(request.form['name'], request.form['url'], request.form['shop'])
    return redirect(url_for('index'))

@app.route('/check')
def check_now():
    tracker.check_prices()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
