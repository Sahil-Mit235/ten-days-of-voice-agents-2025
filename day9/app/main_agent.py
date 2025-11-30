import re
from example_catalog import list_products, create_order, last_order

def parse_filters(text):
    text = text.lower()
    filters = {"category": None, "max_price": None, "color": None, "size": None}

    categories = ["mug", "tshirt", "hoodie", "cap"]
    for c in categories:
        if c in text:
            filters["category"] = c

    if "under" in text or "below" in text:
        m = re.search(r"(under|below)\s+(\d+)", text)
        if m:
            filters["max_price"] = int(m.group(2))

    colors = ["white","blue","black","grey"]
    for col in colors:
        if col in text:
            filters["color"] = col

    sizes = ["S","M","L","XL"]
    for sz in sizes:
        if sz.lower() in text:
            filters["size"] = sz

    return filters

def summarize_products(products):
    if not products:
        return "No products found."
    out = []
    for i, p in enumerate(products, start=1):
        out.append(f"{i}. {p['name']} ({p['price']} INR)")
    return "\n".join(out)

def main():
    print("🛒 Voice E-commerce Agent (Day 9)")
    last_shown = []

    while True:
        text = input("\nYou: ").lower().strip()

        if text in ["quit","exit","bye"]:
            print("Goodbye!")
            break

        if "what did i just buy" in text:
            lo = last_order()
            if lo:
                print(f"Last order: {lo['id']} — Total {lo['total']} INR")
            else:
                print("You have no previous orders.")
            continue

        if any(k in text for k in ["show me", "do you have", "list"]):
            filters = parse_filters(text)
            prods = list_products(filters)
            last_shown = prods
            print("Here are the results:")
            print(summarize_products(prods))
            continue

        if "buy" in text or "purchase" in text:
            if not last_shown:
                print("Please show products first.")
                continue

            m = re.search(r"(first|second|third|fourth|\d+)", text)
            if not m:
                print("Please specify which product number to buy.")
                continue

            word = m.group(1)
            mapping = {"first":1,"second":2,"third":3,"fourth":4}
            idx = mapping.get(word, int(word))

            if idx > len(last_shown) or idx < 1:
                print("Invalid item number.")
                continue

            product = last_shown[idx-1]
            order = create_order([{"product_id": product["id"], "quantity": 1}])

            print(f"Order created! ID: {order['id']}, Total: {order['total']} INR")
            continue

        print("I didn't understand. Try: 'show me hoodies', 'do you have mugs under 900', 'buy the first one'.")

if __name__ == "__main__":
    main()
