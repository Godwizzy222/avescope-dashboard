import os
import google.generativeai as genai

class LLMSummarizer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def generate_alert_summary(self, symbol, current_price, metric, threshold_value, condition):
        """
        Generates a degen-friendly vibe check alert.
        """
        prompt =f"""
        You are a crypto degen trader bot.
        We just triggered an alert for {symbol} token!
        Current Price: ${current_price}
        Trigger Condition: {metric} went {condition} the target of {threshold_value}.
        
        Write a short (2-3 sentences max) hype/alert message. 
        Use words like 'pump', 'dump', 'smart money', 'breakout', or 'accumulation' if it went up. 
        If it went down, use terms like 'rekt', 'capitulation', 'buying opportunity'.
        Keep it highly engaging and styled for a telegram channel.
        """
        
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                return f"🤖 [AI Offline]: {symbol} hit {metric} {condition} {threshold_value} at ${current_price}. (Error: {str(e)})"
        else:
            # Fallback if no Gemini key
            direction = "rocketing 🚀" if "above" in condition else "dumping 🩸"
            return f"🚨 ALERT: {symbol} is {direction}! It just crossed the {metric} threshold of {threshold_value} and is currently trading at ${current_price}."
