import json
import os
import uuid
import datetime

BASE = os.path.join(os.path.dirname(__file__), '..')
CATALOG_PATH = os.path.join(BASE, 'shared-data', 'catalog.json')
RECIPES_PATH = os.path.join(BASE, 'shared-data', 'recipes.json')
ORDERS_PATH = os.path.join(BASE, 'orders', 'orders.json')
LOG_DIR = os.path.join(BASE, 'logs')

STATUS_SEQUENCE = ['received','confirmed','being_prepared','out_for_delivery','delivered']

def load_json(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def save_json(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2)

def simulate_voice(agent, text):
    # Placeholder for Murf Falcon TTS + LiveKit handoff
    print(f'[{agent} VOICE] {text}')

class Catalog:
    def __init__(self):
        self.items = {i['id']: i for i in load_json(CATALOG_PATH)}

    def find(self, item_id):
        return self.items.get(item_id)

    def search_by_name(self, query):
        q = query.lower()
        return [v for v in self.items.values() if q in v['name'].lower()]

    def list_all(self):
        return list(self.items.values())

class Cart:
    def __init__(self):
        self.items = {}  # id -> qty

    def add(self, item_id, qty=1):
        self.items[item_id] = self.items.get(item_id, 0) + int(qty)

    def remove(self, item_id):
        if item_id in self.items:
            del self.items[item_id]

    def update(self, item_id, qty):
        if int(qty) <= 0:
            self.remove(item_id)
        else:
            self.items[item_id] = int(qty)

    def clear(self):
        self.items = {}

    def summary(self, catalog):
        out = []
        total = 0
        for iid, qty in self.items.items():
            item = catalog.find(iid)
            if not item:
                continue
            price = item.get('price',0)
            out.append({'id': iid, 'name': item['name'], 'qty': qty, 'unit_price': price, 'subtotal': price*qty})
            total += price*qty
        return out, total

class OrderManager:
    def __init__(self):
        self.orders = load_json(ORDERS_PATH)

    def new_order(self, customer_name, address, cart_summary, total):
        order_id = str(uuid.uuid4())[:8]
        order = {
            'orderId': order_id,
            'customerName': customer_name,
            'address': address,
            'items': cart_summary,
            'total': total,
            'status': 'received',
            'createdAt': datetime.datetime.now().isoformat(),
            'lastUpdated': datetime.datetime.now().isoformat()
        }
        self.orders.append(order)
        save_json(ORDERS_PATH, self.orders)
        self._log(f'Order {order_id} created (received)')
        return order

    def list_orders(self):
        return list(self.orders)

    def find_order(self, order_id):
        for o in self.orders:
            if o['orderId'] == order_id:
                return o
        return None

    def advance_status(self, order_id):
        o = self.find_order(order_id)
        if not o:
            return None
        cur = o.get('status','received')
        try:
            i = STATUS_SEQUENCE.index(cur)
            if i < len(STATUS_SEQUENCE)-1:
                o['status'] = STATUS_SEQUENCE[i+1]
                o['lastUpdated'] = datetime.datetime.now().isoformat()
                save_json(ORDERS_PATH, self.orders)
                self._log(f'Order {order_id} status advanced to {o[\"status\"]}')
                return o['status']
        except ValueError:
            pass
        return o.get('status')

    def _log(self, text):
        os.makedirs(LOG_DIR, exist_ok=True)
        f = os.path.join(LOG_DIR, f'orders_{datetime.date.today().isoformat()}.log')
        with open(f, 'a', encoding='utf-8') as lf:
            lf.write(f'[{datetime.datetime.now().isoformat()}] {text}\\n')

class OrderingAgent:
    def __init__(self):
        self.catalog = Catalog()
        self.recipes = load_json(RECIPES_PATH)
        self.cart = Cart()
        self.orders = OrderManager()

    def greet(self):
        simulate_voice('Alicia', 'Hi! I am QuickShop Assistant. I can help you browse, add items, and place orders.')

    def show_catalog(self):
        items = self.catalog.list_all()
        for it in items:
            print(f\"{it['id']} — {it['name']} ({it['category']}) — ₹{it['price']}/{it['unit']}\")

    def add_item(self, id_or_name, qty=1):
        # If exact id given
        item = self.catalog.find(id_or_name)
        if not item:
            # try search by name
            results = self.catalog.search_by_name(id_or_name)
            if len(results) == 1:
                item = results[0]
            elif len(results) > 1:
                simulate_voice('Alicia', f'I found multiple items for \\\"{id_or_name}\\\". Please be more specific.')
                for r in results:
                    print(r['id'], r['name'])
                return
            else:
                simulate_voice('Alicia', f'No item found for \\\"{id_or_name}\\\".')
                return
        self.cart.add(item['id'], qty)
        simulate_voice('Alicia', f'Added {qty} x {item[\"name\"]} to your cart.')

    def add_recipe(self, recipe_key, servings=1):
        r = self.recipes.get(recipe_key)
        if not r:
            simulate_voice('Alicia', f'I don\\'t know the recipe \\\"{recipe_key}\\\".')
            return
        for entry in r:
            self.cart.add(entry['id'], int(entry.get('qty',1))*int(servings))
        simulate_voice('Alicia', f'Added ingredients for {recipe_key} (servings: {servings}).')

    def show_cart(self):
        summary, total = self.cart.summary(self.catalog)
        if not summary:
            simulate_voice('Alicia', 'Your cart is empty.')
            return
        print('Cart:')
        for it in summary:
            print(f\"{it['qty']} x {it['name']} — ₹{it['unit_price']} each — subtotal ₹{it['subtotal']}\")
        print(f'Total: ₹{total}')

    def remove_item(self, item_id):
        self.cart.remove(item_id)
        simulate_voice('Alicia', f'Removed {item_id} from cart (if present).')

    def update_qty(self, item_id, qty):
        self.cart.update(item_id, qty)
        simulate_voice('Alicia', f'Quantity updated for {item_id} to {qty}.')

    def place_order(self):
        summary, total = self.cart.summary(self.catalog)
        if not summary:
            simulate_voice('Alicia', 'Your cart is empty. Nothing to order.')
            return
        print('Final summary:')
        for it in summary:
            print(f\"{it['qty']} x {it['name']} — ₹{it['subtotal']}\")
        print(f'Total: ₹{total}')
        name = input('Your name> ').strip()
        address = input('Delivery address> ').strip()
        order = self.orders.new_order(name, address, summary, total)
        simulate_voice('Alicia', f'Order placed. Your order id is {order[\"orderId\"]}.')
        self.cart.clear()

    def show_orders(self):
        all_orders = self.orders.list_orders()
        if not all_orders:
            simulate_voice('Alicia', 'No orders found.')
            return
        for o in all_orders:
            print(f\"{o['orderId']} — {o['customerName']} — ₹{o['total']} — {o['status']} — {o['createdAt']}\")
    
    def track_order(self, order_id):
        o = self.orders.find_order(order_id)
        if not o:
            simulate_voice('Alicia', 'Order not found.')
            return
        simulate_voice('Alicia', f\"Order {order_id} is currently: {o['status']}. Last update: {o.get('lastUpdated')}\")
        print(json.dumps(o, indent=2))

    def reorder(self, order_id):
        o = self.orders.find_order(order_id)
        if not o:
            simulate_voice('Alicia', 'Order not found.')
            return
        # rebuild cart from order items
        for it in o['items']:
            self.cart.add(it['id'], it['qty'])
        simulate_voice('Alicia', f'Rebuilt cart from order {order_id}. Check cart and place order when ready.')

    def advance_status(self, order_id):
        status = self.orders.advance_status(order_id)
        if status:
            simulate_voice('Alicia', f'Order {order_id} advanced to {status}.')
        else:
            simulate_voice('Alicia', f'Could not advance order {order_id}.')

def repl():
    agent = OrderingAgent()
    agent.greet()
    print('Commands: catalog | add <id_or_name> [qty] | recipe <key> [servings] | cart | remove <id> | update <id> <qty> | place | orders | track <orderId> | reorder <orderId> | advance <orderId> | quit')
    while True:
        cmd = input('\\n> ').strip()
        if not cmd:
            continue
        parts = cmd.split()
        cmd0 = parts[0].lower()
        try:
            if cmd0 == 'catalog':
                agent.show_catalog()
            elif cmd0 == 'add':
                if len(parts) >= 2:
                    qty = int(parts[2]) if len(parts) >=3 else 1
                    agent.add_item(parts[1], qty)
                else:
                    print('Usage: add <id_or_name> [qty]')
            elif cmd0 == 'recipe':
                key = parts[1] if len(parts)>=2 else ''
                servings = int(parts[2]) if len(parts)>=3 else 1
                agent.add_recipe(key, servings)
            elif cmd0 == 'cart':
                agent.show_cart()
            elif cmd0 == 'remove':
                agent.remove_item(parts[1])
            elif cmd0 == 'update':
                agent.update_qty(parts[1], int(parts[2]))
            elif cmd0 == 'place':
                agent.place_order()
            elif cmd0 == 'orders':
                agent.show_orders()
            elif cmd0 == 'track':
                agent.track_order(parts[1])
            elif cmd0 == 'reorder':
                agent.reorder(parts[1])
            elif cmd0 == 'advance':
                agent.advance_status(parts[1])
            elif cmd0 in ('quit','exit'):
                simulate_voice('Alicia', 'Goodbye!')
                break
            else:
                print('Unknown command.')
        except Exception as e:
            print('Error:', e)

if __name__ == '__main__':
    repl()
