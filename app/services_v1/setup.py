from azure.identity import DefaultAzureCredential
from langchain_openai.chat_models import AzureChatOpenAI  
import os

def setup_azure_openai_local():  
    """Setup Azure OpenAI client for local deployment."""  
    try:  
        
        credential = DefaultAzureCredential()  
        token = credential.get_token("https://cognitiveservices.azure.com/.default")  
        openai_endpoint = 'https://dmrid-ai-services-dev-openai-04.openai.azure.com/' 
        azure_deployment = 'gpt-5-chat'
  
        os.environ["OPENAI_API_KEY"] = token.token  
        azure_openai_client = AzureChatOpenAI(  
            azure_deployment=azure_deployment,  
            openai_api_type='azure_ad',  
            api_version="2024-12-01-preview",  
            azure_endpoint=openai_endpoint,  
            temperature=0  
        )  
  
        
        return azure_openai_client  
    except Exception as e:  
        raise  