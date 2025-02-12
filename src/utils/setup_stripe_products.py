import os
import stripe
from dotenv import load_dotenv

load_dotenv()

def setup_stripe_products(is_test=False):
    """Set up Stripe products and prices"""
    # Set the appropriate API key
    stripe.api_key = os.getenv('STRIPE_TEST_SECRET_KEY') if is_test else os.getenv('STRIPE_SECRET_KEY')
    mode = "TEST" if is_test else "LIVE"
    price_amount = 1000 if is_test else 4900  # $10 for test, $49 for live
    
    print(f"\nSetting up {mode} mode products:")
    print("=" * 50)
    
    # Create or get the product
    product_name = "City Tagger Service"
    products = stripe.Product.list(active=True)
    product = next((p for p in products if p.name == product_name), None)
    
    if not product:
        print(f"Creating new product: {product_name}")
        product = stripe.Product.create(
            name=product_name,
            description="Automatically tag Zillow showing requests with city information in Follow Up Boss",
        )
    else:
        print(f"Using existing product: {product.name} (ID: {product.id})")
    
    # Create or get the price
    prices = stripe.Price.list(product=product.id, active=True)
    price = next((p for p in prices if p.unit_amount == price_amount and p.recurring), None)
    
    if not price:
        print(f"Creating new price: ${price_amount/100}/month")
        price = stripe.Price.create(
            product=product.id,
            unit_amount=price_amount,
            currency="usd",
            recurring={"interval": "month"},
            nickname=f"Monthly subscription ({mode} mode)"
        )
    else:
        print(f"Using existing price: ${price.unit_amount/100}/month (ID: {price.id})")
    
    return {
        'product_id': product.id,
        'price_id': price.id
    }

if __name__ == '__main__':
    # Set up test mode products
    test_ids = setup_stripe_products(is_test=True)
    print(f"\nTest mode IDs:")
    print(f"Product ID: {test_ids['product_id']}")
    print(f"Price ID: {test_ids['price_id']}")
    
    # Set up live mode products
    live_ids = setup_stripe_products(is_test=False)
    print(f"\nLive mode IDs:")
    print(f"Product ID: {live_ids['product_id']}")
    print(f"Price ID: {live_ids['price_id']}")
    
    print("\nAdd these IDs to your .env file:") 