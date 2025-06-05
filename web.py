from threading import Thread
from flask import Flask, request, redirect, url_for, render_template_string

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
<p>
  {% if paused %}
  <a href="{{ url_for('resume') }}">Resume checking</a>
  {% else %}
  <a href="{{ url_for('pause') }}">Pause checking</a>
  {% endif %}
</p>
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
<h1>Edit {{ original_name }}</h1>
<form method="post" action="{{ url_for('update_shop', original_name=original_name) }}">
  Name: <input name="name" value="{{ original_name }}"><br>
  CSS selector: <input name="selector" value="{{ selector }}"><br>
  <button type="submit">Save</button>
</form>
<form method="post" action="{{ url_for('delete_shop', name=original_name) }}">
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
    return render_template_string(EDIT_SHOP_TEMPLATE, original_name=name, selector=shop.selector)


@app.route('/shops/update/<original_name>', methods=['POST'])
def update_shop(original_name):
    new_name = request.form['name']
    selector = request.form['selector']
    if new_name != original_name:
        tracker.rename_shop(original_name, new_name)
        tracker.update_shop(new_name, selector)
    else:
        tracker.update_shop(original_name, selector)
    return redirect(url_for('list_shops'))


@app.route('/shops/delete/<name>', methods=['POST'])
def delete_shop(name):
    tracker.remove_shop(name)
    return redirect(url_for('list_shops'))

@app.route('/add', methods=['POST'])
def add_product():
    tracker.add_product(request.form['name'], request.form['url'], request.form['shop'])
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

if __name__ == '__main__':
    app.run()
