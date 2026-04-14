from services.llm_summarizer import LLMSummarizer

class AlertManager:
    def __init__(self, gemini_api_key=None):
        self.llm = LLMSummarizer(api_key=gemini_api_key)

    def check_alerts(self, alerts_config, live_data):
        """
        alerts_config = [
            {"id": "1", "symbol": "DOGE", "metric": "price", "condition": "above", "value": 0.15}, ...
        ]
        live_data = {"DOGE": {"price": 0.16, "market_cap": ...}}
        Returns a list of generated alert messages.
        """
        triggered_messages = []
        
        for rule in alerts_config:
            symbol = rule['symbol']
            if symbol not in live_data:
                continue
                
            current_value = live_data[symbol].get(rule['metric'])
            if current_value is None:
                continue
                
            threshold = float(rule['value'])
            is_triggered = False
            
            if rule['condition'] == 'above' and current_value > threshold:
                is_triggered = True
            elif rule['condition'] == 'below' and current_value < threshold:
                is_triggered = True
                
            if is_triggered:
                # Get the AI-summarized vibe message
                msg = self.llm.generate_alert_summary(
                    symbol=symbol,
                    current_price=live_data[symbol].get('price'),
                    metric=rule['metric'],
                    threshold_value=threshold,
                    condition=rule['condition']
                )
                triggered_messages.append(msg)
                
        return triggered_messages
