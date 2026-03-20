import logging
try:
    from transformers import pipeline
except ImportError:
    print("Transformers library not found. Please install it via pip install transformers torch")
    pipeline = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SentimentAnalyzer:
    def __init__(self, model_name="ProsusAI/finbert"):
        self.model_name = model_name
        self.classifier = None
        self._initialize_model()

    def _initialize_model(self):
        """Initializes the Hugging Face pipeline."""
        if pipeline is None:
            logging.error("Transformers library not available.")
            return

        try:
            logging.info(f"Loading model {self.model_name}... This may take a while first time.")
            self.classifier = pipeline("sentiment-analysis", model=self.model_name)
            logging.info("Model loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load model {self.model_name}: {e}")
            self.classifier = None

    def analyze_headline(self, headline):
        """
        Analyzes the sentiment of a news headline.

        Args:
            headline (str): The news headline text.

        Returns:
            float: Sentiment score between -1 and 1.
                   Positive > 0, Negative < 0, Neutral ~= 0.
        """
        if not self.classifier:
            logging.warning("Model not initialized. Returning 0.")
            return 0.0

        try:
            result = self.classifier(headline)[0]
            label = result['label']
            score = result['score']

            if label == 'positive':
                return score
            elif label == 'negative':
                return -score
            else: # neutral
                return 0.0
        except Exception as e:
            logging.error(f"Error analyzing headline: {e}")
            return 0.0

if __name__ == "__main__":
    # Test block
    analyzer = SentimentAnalyzer()
    
    test_headlines = [
        "Reliance Industries reports 20% jump in quarterly profits",
        "TCS shares fall as margins shrink due to wage hikes",
        "Markets open flat ahead of RBI policy announcement"
    ]
    
    print("\n--- Sentiment Analysis Test ---")
    for hl in test_headlines:
        sentiment = analyzer.analyze_headline(hl)
        print(f"Headline: {hl}\nScore: {sentiment:.4f}\n")
