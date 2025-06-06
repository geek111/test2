from threading import Thread
import re
import json
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, redirect, url_for, render_template_string, jsonify

from price_tracker.shops.generic import parse_price, _find_price_in_json

from price_tracker.tracker import PriceTracker

app = Flask(__name__)
tracker = PriceTracker('products.json', interval=3600, shops_path='shops.json')

# start background price checking
def start_background_tracker():
    Thread(target=tracker.run, daemon=True).start()

start_background_tracker()

INDEX_TEMPLATE = """
<!doctype html>
<title>Price Tracker</title>
<h1>Tracked Products</h1>
<p><a href="{{ url_for('list_shops') }}">Manage shops</a></p>
<ul>
  {% for p in products %}
  <li>
    {{ p.name }} - {{ p.last_price }} ({{ p.shop }})
    <form method="post" action="{{ url_for('delete_product') }}" style="display:inline">
      <input type="hidden" name="url" value="{{ p.url }}">
      <button type="submit">Delete</button>
    </form>
  </li>
  {% endfor %}
</ul>
<h2>Add Product</h2>
<form method="post" action="{{ url_for('add_product') }}">
  Name: <input name="name"><br>
  URL: <input name="url" id="url"><br>
  CSS selector: <input name="selector" id="selector">
  <button type="button" onclick="detectSelector()">Pobierz selector</button><br>
  Price: <input name="price" id="price" readonly><br>
  Shop:
  <select name="shop">
    {% for s in shops %}
    <option value="{{ s }}">{{ s }}</option>
    {% endfor %}
  </select>
  <button type="submit">Add</button>
</form>
<p><a href="{{ url_for('check_now') }}">Check prices now</a></p>
<p>
  {% if paused %}
  <a href="{{ url_for('resume') }}">Resume checking</a>
  {% else %}
  <a href="{{ url_for('pause') }}">Pause checking</a>
  {% endif %}
</p>
<script>
function detectSelector() {
  const url = document.getElementById('url').value;
  fetch('/detect_selector?url=' + encodeURIComponent(url))
    .then(r => r.json())
    .then(data => {
      document.getElementById('selector').value = data.selector;
      if (data.price !== undefined) {
        document.getElementById('price').value = data.price;
      }
    })
    .catch(() => alert('Failed to detect selector'));
}
</script>
"""

SHOPS_TEMPLATE = """
<!doctype html>
<title>Shops</title>
<h1>Registered Shops</h1>
<ul>
  {% for name, selector in shops.items() %}
  <li>{{ name }} - {{ selector }}
      <a href="{{ url_for('edit_shop_form', name=name) }}">Edit</a>
      <form method="post" action="{{ url_for('delete_shop', name=name) }}" style="display:inline">
        <button type="submit">Delete</button>
      </form>
  </li>
  {% endfor %}
</ul>
<h2>Add Shop</h2>
<form method="post" action="{{ url_for('add_shop') }}">
  Name: <input name="name"><br>
  Selector: <input name="selector"><br>
  <button type="submit">Add</button>
</form>
<p><a href="{{ url_for('index') }}">Back</a></p>
"""

EDIT_SHOP_TEMPLATE = """
<!doctype html>
<title>Edit Shop</title>
<h1>Edit {{ name }}</h1>
<form method="post" action="{{ url_for('update_shop', name=name) }}">
  Name: <input name="new_name" value="{{ name }}"><br>
  CSS selector: <input name="selector" value="{{ selector }}"><br>
  <button type="submit">Save</button>
</form>
<form method="post" action="{{ url_for('delete_shop', name=name) }}">
  <button type="submit">Delete shop</button>
</form>
<p><a href="{{ url_for('list_shops') }}">Back to shops</a></p>
"""

@app.route('/')
def index():
    paused = getattr(tracker, 'paused', False)
    if not hasattr(tracker, 'paused'):
        app.logger.warning("PriceTracker instance missing 'paused' attribute")
    return render_template_string(
        INDEX_TEMPLATE,
        products=tracker.store.products,
        shops=tracker.shops.keys(),
        paused=paused,
    )


@app.route('/shops')
def list_shops():
    shops = {name: s.selector for name, s in tracker.shop_store.shops.items()}
    return render_template_string(SHOPS_TEMPLATE, shops=shops)


@app.route('/shops/add', methods=['POST'])
def add_shop():
    tracker.add_shop(request.form['name'], request.form['selector'])
    return redirect(url_for('list_shops'))


@app.route('/shops/edit/<name>')
def edit_shop_form(name):
    shop = tracker.shop_store.shops.get(name)
    if not shop:
        return redirect(url_for('list_shops'))
    return render_template_string(EDIT_SHOP_TEMPLATE, name=name, selector=shop.selector)


@app.route('/shops/update/<name>', methods=['POST'])
def update_shop(name):
    new_name = request.form.get('new_name', name)
    selector = request.form['selector']
    tracker.rename_shop(name, new_name, selector)
    return redirect(url_for('list_shops'))


@app.route('/shops/delete/<name>', methods=['POST'])
def delete_shop(name):
    tracker.remove_shop(name)
    return redirect(url_for('list_shops'))

@app.route('/add', methods=['POST'])
def add_product():
    price_str = request.form.get('price', '')
    try:
        price_val = parse_price(price_str) if price_str else 0.0
    except Exception:
        price_val = 0.0

    tracker.add_product(
        request.form['name'],
        request.form['url'],
        request.form['shop'],
        request.form.get('selector', ''),
        price_val
    )
    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
def delete_product():
    tracker.remove_product(request.form['url'])
    return redirect(url_for('index'))

@app.route('/check')
def check_now():
    tracker.check_prices()
    return redirect(url_for('index'))


@app.route('/pause')
def pause():
    tracker.pause()
    return redirect(url_for('index'))


@app.route('/resume')
def resume():
    tracker.resume()
    return redirect(url_for('index'))


@app.route('/detect_selector')
def detect_selector():
    url = request.args.get('url')
    if not url:
        return 'URL required', 400
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except Exception as exc:
        return str(exc), 400

    soup = BeautifulSoup(resp.text, 'html.parser')

    # First try JSON-LD scripts which often contain the exact price
    for script in soup.find_all('script', type='application/ld+json'):
        if not script.string:
            continue
        try:
            data = json.loads(script.string)
        except Exception:
            continue
        val = _find_price_in_json(data)
        if val is not None:
            return jsonify({
                'selector': "script[type='application/ld+json']",
                'price': parse_price(str(val))
            })

    pattern = re.compile(r'\d+[\.,]\d+\s*(?:zł|pln|eur|€|usd|\$)?', re.I)

    # Ignore matches located inside <script> or <style> tags
    element = None
    price_value = None
    for el in soup.find_all(string=pattern):
        if el.parent.name not in ('script', 'style'):
            try:
                price_value = parse_price(str(el))
            except Exception:
                continue
            element = el
            break

    if element is not None:
        elem = element.parent
        selector = elem.name
        if elem.get('id'):
            selector += f"#{elem.get('id')}"
        elif elem.get('class'):
            selector += '.' + '.'.join(elem.get('class'))
        return jsonify({'selector': selector, 'price': price_value})

    # Fallback to JSON-LD scripts
    for script in soup.find_all('script', type='application/ld+json'):
        if not script.string:
            continue
        try:
            data = json.loads(script.string)
        except Exception:
            continue
        val = _find_price_in_json(data)
        if val is not None:
            return jsonify({
                'selector': "script[type='application/ld+json']",
                'price': parse_price(str(val))
            })

    return '', 404

if __name__ == '__main__':
    app.run()
