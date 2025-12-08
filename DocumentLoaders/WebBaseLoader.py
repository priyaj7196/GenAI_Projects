from langchain_community.document_loaders import WebBaseLoader
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

url1="https://www.anker.com/products/a1665-5k-ultra-slim-qi2-power-bank?variant=45217864089750&utm_source=google&utm_medium=pmax&utm_campaign=us_anker_charger_conversion_pmax_charger_purchase_ost&utm_content=charger&utm_term=%7B16031486107%7D_%7B%7D_%7B%7D&gad_source=1&gad_campaignid=16037164256&gbraid=0AAAAADbnO27SR82JN-ZK7txXlyQtXU9H3&gclid=CjwKCAiA3L_JBhAlEiwAlcWO5wecHfqrabgfLjroIzUjO2xhlXe0UFv0M2qmLeyKF0sVCh1EiOGn2RoCSDgQAvD_BwE"
url2="https://www.anker.com/products/a1695-anker-power-bank-25000mah-165w?variant=44320657997974&utm_source=google&utm_medium=pmax&utm_content=alwayson&utm_campaign=us_security_DIFMSecurity_m1-2_google-pmax_E9000122_purchase_buycode_audience_external&utm_term=20274825774___Topcvr-travel-0618-travel&NewAudience&gad_source=1&gad_campaignid=20284126303&gbraid=0AAAAADbnO25egHbUp9cSLgbTTQSoeG1Fi&gclid=CjwKCAiA3L_JBhAlEiwAlcWO5xosJLtNQjPThd-tUCxUkAmyX0JNUiGDYmitUQT7aG2rTFXw3dg_YhoCnncQAvD_BwE"

loader=WebBaseLoader([url1,url2])
docs=loader.load()

print(len(docs))
print(docs[0].page_content[:100])
print(docs[1].page_content[:100])

model=ChatOpenAI(model="gpt-4o-mini",temperature=0.0)

prompt=PromptTemplate(
    template="Summarize the following product description: {page_content}",
    input_variables=["page_content"]
)

chain=prompt | model | StrOutputParser()

# Process each document
for doc in docs:
    result = chain.invoke({"page_content": doc.page_content[:500]})  # Limit content length
    print(f"\nSummary:\n{result}\n")