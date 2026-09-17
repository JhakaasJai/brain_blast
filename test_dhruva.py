import requests

url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
# Let's try to just test if auth works
headers = {
    "Authorization": "YSycq_NXhc7I-uGwA7O6nl7uknsxNq1_441uMaFyR2gQjw9BtwKZHN6g9w1xqOnt",
    "Content-Type": "application/json"
}
payload = {
    "pipelineTasks": [{"taskType": "translation", "config": {"language": {"sourceLanguage": "en", "targetLanguage": "hi"}}}],
    "inputData": {"input": [{"source": "hello"}]}
}
try:
    res = requests.post(url, headers=headers, json=payload, timeout=5)
    print(res.status_code, res.text[:200])
except Exception as e:
    print(e)
