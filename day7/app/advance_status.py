import json
import os
import datetime

ORDERS_PATH = os.path.join(os.path.dirname(__file__), '..', 'orders', 'orders.json')
STATUS_SEQUENCE = ['received','confirmed','being_prepared','out_for_delivery','delivered']

def load_orders():
    with open(ORDERS_PATH, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def save_orders(o):
    with open(ORDERS_PATH, 'w', encoding='utf-8') as f:
        json.dump(o, f, indent=2)

def advance_all():
    orders = load_orders()
    changed = 0
    for o in orders:
        cur = o.get('status','received')
        try:
            idx = STATUS_SEQUENCE.index(cur)
            if idx < len(STATUS_SEQUENCE)-1:
                o['status'] = STATUS_SEQUENCE[idx+1]
                o['lastUpdated'] = datetime.datetime.now().isoformat()
                changed += 1
        except ValueError:
            continue
    if changed:
        save_orders(orders)
    print(f'Advanced {changed} orders.')

if __name__ == '__main__':
    advance_all()
