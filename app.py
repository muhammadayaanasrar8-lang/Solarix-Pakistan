from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
# Secure secret key for Flask session state
app.secret_key = 'solarix_session_secret_key_987654321_pk'

# Central catalog of solar products and advisor packages
PRODUCTS = {
    'p1': {
        'name': 'Solar Panel 590W',
        'price': 23500,
        'image': '/static/images/solar panel.png',
        'specs': ['N-Type Mono-Facial', 'HOT 2.0 TOPCon Technology', '5-Year Performance Warranty']
    },
    'p2': {
        'name': 'Inverter 3KW',
        'price': 80000,
        'image': '/static/images/Inverter1.png',
        'specs': ['Pure Sine Wave Hybrid', 'Dual MPPT Tracker Channels', '3-Year Warranty']
    },
    'p3': {
        'name': 'Lithium Battery 3.5kWh',
        'price': 150000,
        'image': '/static/images/Battery1.png',
        'specs': ['Compact Wall-Mount Cabinet', 'Fast Charge & High Discharge', '10-Year Manufacturer Warranty']
    },
    'p4': {
        'name': 'Solar Panel 640W',
        'price': 28500,
        'image': '/static/images/solar panel.png',
        'specs': ['N Type Bifacial Panel', 'Advanced 20-busbar (20BB) Technology', '5-Year Performance Warranty']
    },
    'p5': {
        'name': 'Solar Panel 705W',
        'price': 33000,
        'image': '/static/images/solar panel.png',
        'specs': ['N Type Bifacial Panel', 'Advanced 20-busbar (20BB) Technology', '5-Year Performance Warranty']
    },
    'p6': {
        'name': 'Solar Panel 770W',
        'price': 37000,
        'image': '/static/images/solar panel.png',
        'specs': ['N Type Bifacial Panel', 'Advanced 20-busbar (20BB) Technology', '5-Year Performance Warranty']
    },
    'p7': {
        'name': 'Inverter 4KW',
        'price': 115000,
        'image': '/static/images/Inverter1.png',
        'specs': ['Pure Sine Wave Hybrid', 'Dual MPPT Tracker Channels', '3-Year Warranty']
    },
    'p8': {
        'name': 'Inverter 8KW',
        'price': 210000,
        'image': '/static/images/Inverter1.png',
        'specs': ['Pure Sine Wave Hybrid', 'Dual MPPT Tracker Channels', '3-Year Warranty']
    },
    'p9': {
        'name': 'Inverter 12KW',
        'price': 275000,
        'image': '/static/images/Inverter1.png',
        'specs': ['12kW IP54 Hybrid Inverter', 'Dual MPPT Tracker Channels', '5-Year Warranty']
    },
    'p10': {
        'name': 'Lithium Battery 4.8kWh',
        'price': 180000,
        'image': '/static/images/Battery1.png',
        'specs': ['Premium LiFePO4 cells', '6,000+ Charge-Discharge Cycles', 'Safe Built-in Smart BMS']
    },
    'p11': {
        'name': 'Lithium Battery 5.2kWh',
        'price': 220000,
        'image': '/static/images/Battery1.png',
        'specs': ['100Ah Capacity', '52V Nominal Voltage', 'Advanced LiFePO₄ chemistry']
    },
    'p12': {
        'name': 'Lithium Battery 10.3kWh',
        'price': 540000,
        'image': '/static/images/Battery1.png',
        'specs': ['10.36kwh EP11 Battery Bank', 'IP-rated Protection', 'Advanced LiFePO₄ chemistry']
    }
}

PACKAGES = {
    'pkg-3kw': {
        'name': 'Solarix 3KW Starter Package',
        'price': 180000,
        'image': '/static/images/package.png',
        'desc': 'Ideal for small homes. Power 1 A/C, 4 fans, and LED lights.',
        'specs': '4x 640W Tier-1 Panels, 3KW Smart Inverter, Structure & Setup.'
    },
    'pkg-4kw': {
        'name': 'Solarix 4KW Eco-Smart Package',
        'price': 460000,
        'image': '/static/images/package.png',
        'desc': 'Ideal for medium homes. Power 2 A/Cs, fridge, water pump, and lights.',
        'specs': '8x 590W Tier-1 Panels, 4KW Hybrid Inverter, 4.8kWh Lithium Battery, Cabling & Setup.'
    },
    'pkg-8kw': {
        'name': 'Solarix 8KW Premium Powerhouse',
        'price': 1100000,
        'image': '/static/images/package.png',
        'desc': 'Ideal for larger homes. Full energy independence with net-metering support.',
        'specs': '15x 770W Panels, 8KW 3-Phase Inverter, 10.3kWh Lithium Storage, Net-Metering Registration.'
    }
}

# Unified items lookup for cart resolves
ITEMS = {**PRODUCTS, **PACKAGES}

# Jinja filter to format currency cleanly
@app.template_filter('currency')
def currency_filter(value):
    try:
        return f"Rs. {int(value):,}"
    except (ValueError, TypeError):
        return f"Rs. {value}"

# Context processor to globally supply cart item quantities
@app.context_processor
def utility_processor():
    def get_cart_count():
        cart = session.get('cart', {})
        return sum(cart.values())
    return dict(cart_count=get_cart_count())

# Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/products")
def products():
    # Pass BOTH products and packages to the template
    return render_template("products.html", products=PRODUCTS, packages=PACKAGES)
@app.route("/cart")
def cart():
    cart_dict = session.get('cart', {})
    cart_items = []
    subtotal = 0
    
    for item_id, qty in cart_dict.items():
        if item_id in ITEMS:
            details = ITEMS[item_id]
            total_price = details['price'] * qty
            subtotal += total_price
            cart_items.append({
                'id': item_id,
                'name': details['name'],
                'price': details['price'],
                'image': details['image'],
                'quantity': qty,
                'total': total_price
            })
            
    shipping = 0 if subtotal > 100000 or subtotal == 0 else 5000
    tax = int(subtotal * 0.18)
    grand_total = subtotal + shipping + tax
    
    return render_template(
        "cart.html", 
        cart_items=cart_items, 
        subtotal=subtotal, 
        shipping=shipping, 
        tax=tax, 
        grand_total=grand_total
    )

@app.route("/add-to-cart/<item_id>", methods=["GET", "POST"])
def add_to_cart(item_id):
    if 'cart' not in session:
        session['cart'] = {}
        
    cart_dict = session['cart']
    if item_id in ITEMS:
        cart_dict[item_id] = cart_dict.get(item_id, 0) + 1
        session['cart'] = cart_dict
        session.modified = True
        
    # Redirect back to the page where action occurred, or fall back to products
    return redirect(request.referrer or url_for('products'))

@app.route("/update-qty/<item_id>", methods=["POST"])
def update_qty(item_id):
    cart_dict = session.get('cart', {})
    change = int(request.form.get('change', 0))
    
    if item_id in cart_dict:
        cart_dict[item_id] += change
        if cart_dict[item_id] <= 0:
            cart_dict.pop(item_id)
        session['cart'] = cart_dict
        session.modified = True
        
    return redirect(url_for('cart'))

@app.route("/remove-from-cart/<item_id>", methods=["POST"])
def remove_from_cart(item_id):
    cart_dict = session.get('cart', {})
    if item_id in cart_dict:
        cart_dict.pop(item_id)
        session['cart'] = cart_dict
        session.modified = True
        
    return redirect(url_for('cart'))

@app.route("/clear-cart", methods=["POST"])
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('products'))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        payment = request.form.get('payment')
        
        cart_dict = session.get('cart', {})
        if not cart_dict:
            return redirect(url_for('products'))
            
        subtotal = sum(ITEMS[item_id]['price'] * qty for item_id, qty in cart_dict.items() if item_id in ITEMS)
        shipping = 0 if subtotal > 100000 else 5000
        tax = int(subtotal * 0.18)
        grand_total = subtotal + shipping + tax
        
        order_id = f"SLX-{random.randint(100000, 999999)}"
        
        # Save order receipt details in the session for display on redirect
        session['last_order'] = {
            'order_id': order_id,
            'name': name,
            'phone': phone,
            'address': address,
            'total': grand_total
        }
        # Clear cart upon order completion
        session.pop('cart', None)
        session.modified = True
        return redirect(url_for('checkout'))
        
    # GET logic
    # Check if we should render the success state
    last_order = session.pop('last_order', None)
    if last_order:
        return render_template("checkout.html", order_success=True, order=last_order)
        
    # Otherwise render the standard checkout form (if cart is not empty)
    cart_dict = session.get('cart', {})
    if not cart_dict:
        return redirect(url_for('products'))
        
    cart_items = []
    subtotal = 0
    for item_id, qty in cart_dict.items():
        if item_id in ITEMS:
            details = ITEMS[item_id]
            total_price = details['price'] * qty
            subtotal += total_price
            cart_items.append({
                'name': details['name'],
                'quantity': qty,
                'total': total_price
            })
            
    shipping = 0 if subtotal > 100000 else 5000
    tax = int(subtotal * 0.18)
    grand_total = subtotal + shipping + tax
    
    return render_template(
        "checkout.html", 
        order_success=False, 
        cart_items=cart_items, 
        subtotal=subtotal, 
        shipping=shipping, 
        tax=tax, 
        grand_total=grand_total
    )

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    # Setup initial welcome message if chatbot session is fresh
    if 'chat_messages' not in session:
        session['chat_messages'] = [{
            'text': "Hello! I'm your Solarix Solar Advisor. ☀️ Please enter your average monthly electricity bill in Rupees (Rs.) below, and I will recommend the optimal solar capacity and component package for your household!",
            'is_user': False,
            'package': None
        }]
        
    if request.method == "POST":
        bill_val = request.form.get('bill', '').strip()
        if bill_val and bill_val.isdigit():
            bill = int(bill_val)
            
            # User bubble
            session['chat_messages'].append({
                'text': f"Monthly bill: Rs. {bill:,}",
                'is_user': True,
                'package': None
            })
            
            # AI recommendation assessment
            if bill < 20000:
                rec_key = 'pkg-3kw'
                package = PACKAGES[rec_key]
                bot_text = f"Based on your monthly electricity bill of Rs. {bill:,}, your average consumption is relatively moderate. I recommend a *3KW Solar System*. It easily offsets smaller loads and fits typical residential connections."
            elif bill < 50000:
                rec_key = 'pkg-4kw'
                package = PACKAGES[rec_key]
                bot_text = f"Based on your bill of Rs. {bill:,}, you run high-demand loads like air conditioners. I recommend a *5KW Hybrid Solar System* equipped with lithium battery storage to buffer power cuts and run heavy appliances during peak solar hours."
            else:
                rec_key = 'pkg-8kw'
                package = PACKAGES[rec_key]
                bot_text = f"Your electricity usage of Rs. {bill:,} is substantial. I recommend a full *10KW Premium Solar Powerhouse*. This configuration supports whole-house backing, battery backup, and grid-tied net-metering so you can sell surplus power back to the grid."
            
            # Package card data passed directly to message
            widget_data = {
                'key': rec_key,
                'name': package['name'],
                'price': package['price'],
                'image': package['image'],
                'desc': package['desc'],
                'specs': package['specs']
            }
            
            # Bot bubble
            session['chat_messages'].append({
                'text': bot_text,
                'is_user': False,
                'package': widget_data
            })
            session.modified = True
            
        return redirect(url_for('chatbot'))
        
    return render_template("chatbot.html", chat_messages=session['chat_messages'])

@app.route("/clear-chat", methods=["POST"])
def clear_chat():
    session.pop('chat_messages', None)
    return redirect(url_for('chatbot'))

if __name__ == "__main__":
    app.run(debug=True)