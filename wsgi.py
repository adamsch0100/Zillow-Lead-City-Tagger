from src.app import app
from src.services.city_tagger_service import city_tagger_service

if __name__ == "__main__":
    # Start the city tagger service
    city_tagger_service.start()
    
    # Run the Flask application
    app.run() 