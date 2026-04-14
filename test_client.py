from services.ave_api_client import AveApiClient

client = AveApiClient()
res = client.get_token_price_and_volume("So11111111111111111111111111111111111111112")
print("RESULT:", res)
