import requests

BHASHINI_API_KEY = "459ed6664f-53df-486d-9954-3b28c66e4143"
BHASHINI_USER_ID = "YSycq_NXhc7I-uGwA7O6nl7uknsxNq1_441uMaFyR2gQjw9BtwKZHN6g9w1xqOnt"
url = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
headers = {
    "userID": BHASHINI_USER_ID,
    "ulcaApiKey": BHASHINI_API_KEY,
    "Authorization": BHASHINI_API_KEY,
    "Content-Type": "application/json"
}
payload = {
    "pipelineTasks": [{"taskType": "translation", "config": {"language": {"sourceLanguage": "en", "targetLanguage": "hi"}}}],
    "pipelineRequestConfig": {"pipelineId": "64392f96daac500b55c543cd"}
}
try:
    res = requests.post(url, headers=headers, json=payload, timeout=5)
    print(res.status_code, res.text[:200])
except Exception as e:
    print(e)
