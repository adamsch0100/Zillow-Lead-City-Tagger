import os
import stripe
from dotenv import load_dotenv

load_dotenv()

def list_stripe_products():
    # First try test mode
    print("\nChecking TEST mode products:")
    print("=" * 50)
    stripe.api_key = os.getenv('STRIPE_TEST_SECRET_KEY')
    
    products = stripe.Product.list()
    for product in products:
        print(f"\nProduct: {product.name} (ID: {product.id})")
        print(f"Active: {product.active}")
        print(f"Description: {product.description}")
        
        # Get prices for this product
        prices = stripe.Price.list(product=product.id)
        print("\nPrices:")
        for price in prices:
            amount = price.unit_amount / 100  # Convert from cents to dollars
            print(f"- ${amount}/{'month' if price.recurring else 'one-time'} (ID: {price.id})")
            print(f"  Active: {price.active}")
            if hasattr(price, 'nickname') and price.nickname:
                print(f"  Nickname: {price.nickname}")
    
    # Then check live mode
    print("\n\nChecking LIVE mode products:")
    print("=" * 50)
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    products = stripe.Product.list()
    for product in products:
        print(f"\nProduct: {product.name} (ID: {product.id})")
        print(f"Active: {product.active}")
        print(f"Description: {product.description}")
        
        # Get prices for this product
        prices = stripe.Price.list(product=product.id)
        print("\nPrices:")
        for price in prices:
            amount = price.unit_amount / 100  # Convert from cents to dollars
            print(f"- ${amount}/{'month' if price.recurring else 'one-time'} (ID: {price.id})")
            print(f"  Active: {price.active}")
            if hasattr(price, 'nickname') and price.nickname:
                print(f"  Nickname: {price.nickname}")

if __name__ == '__main__':
    list_stripe_products() 