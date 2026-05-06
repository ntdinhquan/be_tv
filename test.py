import google.generativeai as genai

genai.configure(api_key="AIzaSyCezOXTZSv1R2AyQ7J2HKHRS3rnS49jwbc")

for m in genai.list_models():
    print(m.name, m.supported_generation_methods)