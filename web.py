from threading import Thread
import re
import json
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, redirect, url_for, render_template, jsonify

from price_tracker.shops.generic import parse_price, _find_price_in_json

from price_tracker.tracker import PriceTracker

app = Flask(__name__)
tracker = PriceTracker('products.json', interval=3600, shops_path='shops.json')

# start background price checking
def start_background_tracker():
    Thread(target=tracker.run, daemon=True).start()

start_background_tracker()


@app.route('/')
def index():
    paused = getattr(tracker, 'paused', False)
    if not hasattr(tracker, 'paused'):
        app.logger.warning("PriceTracker instance missing 'paused' attribute")
    return render_template(
        'index.html',
        products=tracker.store.products,
        shops=tracker.shops.keys(),
        paused=paused,
    )


@app.route('/shops')
def list_shops():
    shops = {name: s.selector for name, s in tracker.shop_store.shops.items()}
    return render_template('shops.html', shops=shops)


@app.route('/shops/add', methods=['POST'])
def add_shop():
    tracker.add_shop(request.form['name'], request.form['selector'])
    return redirect(url_for('list_shops'))


@app.route('/shops/edit/<name>')
def edit_shop_form(name):
    shop = tracker.shop_store.shops.get(name)
    if not shop:
        return redirect(url_for('list_shops'))
    return render_template('edit_shop.html', name=name, selector=shop.selector)


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
