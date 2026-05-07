# import google.generativeai as genai

# genai.configure(api_key="AIzaSyBzIJ6CB5A9WLeEY0VS3ojBlms_9eZtycM")

# for m in genai.list_models():
#     print(m.name, m.supported_generation_methods)


from google import genai
client = genai.Client(api_key="AIzaSyBzIJ6CB5A9WLeEY0VS3ojBlms_9eZtycM")
for m in client.models.list():
    print(m.name)