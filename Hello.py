__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
from embedchain import App
from embedchain.config import LlmConfig
from string import Template
import streamlit as st
from streamlit.logger import get_logger
from stqdm import stqdm
st.set_page_config(layout="wide") 

MODEL = "gpt-4"
LANGUAGE = "English"

#MODEL = "gpt-4-32k"
#MODEL = "gpt-3.5-turbo"
#MODEL = "gpt-3.5-turbo-16k"
queries_product_ideation = [
    "Product ideation. Aiding product ideation: Suggest 3 tech product ideas I could pursue that could turn a profit in less than 2 years. Describe the idea and also share how it will make money.",
    "Product business models. Generate an Alexander Osterwalder business model canvas.",
    "Product validation. Market Sizing: Assume TAM is Total Addressable Market, SAM is Serviceable Available Market and SOM is Serviceable Obtainable Market. How should I go about estimating the TAM, SAM and SOM for my product/Service ? Please give examples of research sources I should check out.",
    "Product ideation. Expanding product lines: I'm already monetizing this product/service well and now want to branch off to other areas. What adjacent product or services can I offer that leverages my strengths & can quickly turn a profit?"
]

queries_product_vision = [
    "Product vision. Aligning teams with a 1-pager memo: Write a 1-pager that I can share with my engineering & design team to explain the product vision & the product components that will most likely be involved.",
    "Product vision. Work Backwards from a Press Release (Amazon): Using Amazon’s “Working Backwards” model,write a press release for this product feature. Include some impressive metrics. Give it a catchy title."
]

queries_product_strategy = [
    """
    Product strategy. Drafting a Product Strategy based on a framework: Gibson Biddle has a product strategy framework called the DHM Model. 
    D stands for delight (how does the product delight customers and add real value), 
    H stands for hard-to-copy (what is an advantage that your product has that is hard to copy and compete with) and 
    M stands for margin-enhancing (how will the product generate a profit and sustain the business). 
    In short, the DHM model aims to answer: 'How will your product delight customers, in hard-to-copy, margin-enhancing ways?'.
    Now, give me a product strategy for my product using Biddle's DHM model.
    """
]

queries_product_roadmap = [
    "Product roadmap. Generating Roadmap Ideas: Give me list of roadmap ideas aligned with this strategy.",
    "Product roadmap. Generating Roadmap Ideas: Can you draft a sample roadmap for this product? Limit the roadmap items to 10. Categorize them under the 'Now', 'Next', 'Later' labels.",
]


queries_product_metrics = [
    "Product metrics. Generating 3 Objectives with each 3 key Results for the product/Service in 3 temporal perspetive 'now', 'next' and 'later' ",
    "Product metrics. Setting up a MixPanel Dashboard: I've been asked to setup a dashboard for measuring performance of product/service on MixPanel. Can you first nominate the metrics I should be tracking and then give me a step by step guide on how to set these up on MixPanel?",
    "Product metrics. Metrics to track: Using the North Star framework (a north star metric which is composed of four metrics which are multipled (north star metric = breadth x depth x frequency x efficiency ). In detail, Breadth is measuring how many active/returning users are taking actions, depth is measuring what's the depth of engagement, frequency is measuring how often does each user engage and efficiency is measuring how fast do they succeed. One example for a food delivery application: total monthly orders delivered is a north star metric, breadth = number of user placing order, depth = number of items within order, frequency = number of orders completed per user, efficiency = pourcentage of orders delivered within time. A second exemple for music application: time spent by subscribers listening to music is a north star metric, breadth = number of trial users + number of premium users, depth = number of hours per session, frequency = number of session per week, efficiency is not evaluated). Can you suggest Northstar metric I should be tracking to measure how well my product / service is doing?",
    "Product metrics. Electing metrics based on a HEART framework: Using the HEART framework, give me the key AAARRR (Awareness, Activation, Acquisition, Revenue, Retention, Referral) metrics I should be tracking & optimizing for.",
    "Product metrics. Business, Product and Delivery metrics: Propose Business metrics that make sense for top level business, Product metrics that make sense for Product managers (can be AAARRR metrics, Awareness, Activation, Acquisition, Revenue, Retention, Referral), Delivery metrics that make sense for Developers. ", 
]

queries_product_positioning = [
    "Product positioning. Competitive intelligence report: write a competitive intelligence report comparing us to other players that I can share in an investor brief?",
]

queries_product_discovery = [
    "Product discovery. personas: Generate 3 fleshed out persona profiles that primarily serves my product/service market?",
    """Product discovery. uncover jobs-to-be done:  
    I want to conduct some consumer research to figure out my consumer's jobs-to-be-done.
    What personas should I target and then what questions should I be asking them to elicit their job-to-be-done. 
    Take inspiration from the book 'Mom Test'""",
    "PRoduct discovery. Opportunity Trees: Assume that the desired outcome are the one uncovered with jobs-to-be-done, Craft an opportunity tree based on Teresa Torres' book, Continuous Discovery Habits, against this desired outcome.",
    "Product discovery. Survey Questions: Using guidelines mentioned in Teresa Torres book 'Continuous Discovery Habits', formulate a survey to capture feedback for my product/service",
    "Product discovery. Outreach emails for Customer Interviews: Write an email that I can send to users inviting them to a short 20-minute feedback call on ways we can improve my product/service. Incentivize them with the proper mean.",

]

queries_product_designthinking = [
    "Product Design Thinking. Customer Journey Maps: Create a sample customer journey map",
    "Product Design Thinking. Design Sprint Brief: Write a memo explaining to my team what we'll be doing on each day of the design sprint. Give a few examples of what the solutions can look like",
]

queries_product_solutionizing = [
    "Product solutionizing. Getting advice on Buy vs Build decisions: give me a framework to decide if i need to build a feature or buy a solution to do this feature.",
    "Product solutionizing. Learning prioritization schemes: how to priorize features using Kano? Can you give me features that would qualify as 'basic','excitement and 'performance' according to Kano?",
]

queries_product_documentation = [
    "Product documentation. PRD Outlines: Write a brief PRD for the product/solution.",
    "Product documentation. Explaining Themes, Epics, Users Stories: write main theme, epics and their associated user stories using in Gherkin syntax",
]

queries_product_copy = [
    "Product copy. Write a boilerplate welcome email for when someone signs up for the first time for my product/service linking out to tutorials, videos & customer testimonials that would encourage them to keep using the product/Service ?.",
]

queries_product_monetization = [
    "Product monetization. Brainstorming revenue streams: Suggest 3 more viable ways for us monetize the product/service and why ?",
]

queries_product_launch = [
    "Product launch. Seeding Pre-mortems: Create a pre-mortem analysis based on Shreyas Doshi's content on this subject on what could potentially go wrong ?",
    "Product launch. Release notes: Write the release notes for that build. ?",
    "Product launch. Writing feature announcements: Generate text for the product/service announcement notification. Use some light humor in the post.",
    "Product launch. Generating a go-to-market plan: I need a 10-point tactical go-to-market plan to grow this product/service in the next 12 months. For each point, mention what needs to be done, who typically does it & how it will be measured.",
]

queries_product_experimentation = [
    "Product experimentation. Suggestions for an A/B test: Recommend 3 A/B tests I could run on this product/Service to improve conversions",
]

queries_product_team = [
    "Product team. Ideas for Organizing Product Teams: Can you recommend what kind of organizational chart I should aim for? Mention who should report to who",
    "Product team. Crediting the team: Write a creative & fun company-wide email publicly thanking the efforts of each team individually with @ mentions",
]

queries_product_growth = [
    "Product growth. Recommending Growth Loops: What kind of growth loops can I add to my product/service based on what Nir Eyal describes in his book called 'Hooked' ?",
    "Product growth. Telling a story about our product / service: You want to excite our sales, marketing and customer success teams about this product/service. You have to prepare a 10-slide presentation to announce this at the next townhall. Include a story using each persona. Use motivating, uplifting language?",
    "Product growth. Making Excuses: Give me a bundle of 10hilarious excuses that I could rotate in my emails to stakeholders explaining why a certain committed feature was delayed.",
]

bot = App()
bot.online = True # enable internet access for the bot


def get_prompt(company, market, product_idea, language = "English"):
  # Use config params from https://docs.embedchain.ai/advanced/query_configuration
  string_full = """
            Act as Product Manager of an """ + company + """
            Here is the product/service: "

            """ + product_idea  + """


            Target market for the product is : """ + market + """

            Use the following information to respond to the human's query.
            Context: $context

            If you don't know the answer, just say that you don't know, don't try to make up an answer.

            Answer the question in """ + language  + """ language.
            You must format answer in markdown without mentioning the format.
            Start the answer with a title rephrasing the question.
            In the end of each answer, introduce by 'Our tips' in bold, provide guidances to take opportunity of that.

            Let's think step by step.

            Human: $query
            Product Manager:
    """
  expert_chat_template = Template(string_full)
  # Example: Use the template, also add a system prompt.
  llm_config = LlmConfig(model=MODEL, temperature=0, template=expert_chat_template, system_prompt="You are a Product Manager.")
  return llm_config


def build_valueproposal_prompt(language = "English"):
  string_full = """
            Act as an expert in creating bootstrapped new venture, in the quest of finding as quickly as possible product market fit, and using as much as possible Product Led Growth strategies.

            Use the following information to respond to the human's query.
            Context: $context

            If you don't know the answer, just say that you don't know, don't try to make up an answer.

            Answer the question in """ + language  + """ language.
            You must format answer in markdown without mentioning the format.
            Start the answer with a title rephrasing the question.

            Let's think step by step.

            Human: $query
            expert:
    """
  expert_chat_template = Template(string_full)
  return expert_chat_template


def get_biz_valueproposal(number_of_ideas, keywords, language = "English"):
    llm_config = LlmConfig(model=MODEL, temperature=0, template=build_valueproposal_prompt(), system_prompt="You are expert.")
    query = """Given a set of keywords,
    propose """ + str(number_of_ideas) + """ differents unique value proposals, with each value proposal is one simple product name in 3 syllabs , up to 4 sentences.
    Questions to validate the strenght of the value proposal: What is the pain, Who has the pain, How painful is it, How is it being solved now, How much in euros will people pay per month to avoid it?
    Here is a formula that will assist you in crafting a value proposition: End Result Customer Wants + Specific Period of Time + Addresses the Objections
    Example, Domino’s Pizza
    (End Result) Customers want hot fresh pizza to be delivered to their doorstep.
    (Specific Period of Time) Domino’s Pizza aims to deliver hot fresh pizzas in 30 mins.
    (Address the Objections) If Domino’s Pizza fails to do so, customers do not have to pay for the pizza

    Answer the question in """ + language  + """ language.
    
    Here are the keywords:
    """
    query += keywords
    response = bot.query(query, config=llm_config)
    return response


def display_biz_result(company:str,market:str, business_idea:str, rubrique:str, query_list, language:str):
    for query in query_list:
        st.markdown(" - " + query)
    st.markdown("")
    if st.button('Generate ' + rubrique, type="primary"):
        with st.container():
            st.markdown("# " + rubrique)
            with st.spinner('Wait for it ...'):
                for query in stqdm(query_list):
                    llm_config = get_prompt(company, market, business_idea, language = language)
                    response = bot.query(query, config=llm_config)
                    st.markdown(response)
                st.markdown("")


LOGGER = get_logger(__name__)


def run():
    st.title('🦜 Product maker App')
    
    company = st.text_input("Company","ed tech platform")
    business_idea = st.text_area("Product/Service unique value proposition","EddyTechy helps students of any age learn how to code & start taking up freelance projects")
    market = st.text_input("Market","French students in Univerity or Grande Ecole")
    with st.expander("Settings"):
        os.environ["OPENAI_API_KEY"] = st.text_input("OpenAI API Key","")
        language_selected = st.radio(
            "Language",
            options=["English", "French"],
        )
    with st.expander("Unique Value Propositions generator"):
        with st.container():
            keywords = st.text_input("Enter your keywords to generate Unique Value Propositions", "non linear editor, web, mobile tv, streaming, live, broadcaster, newsroom, motion graphic, ai")
            nb_ideas = st.text_input("Enter number of Unique Value Propositions to generate", "3")
            if st.button('Generate Unique Value Propositions'):
                    with st.spinner('Wait for it...'):
                        result = get_biz_valueproposal(int(nb_ideas), keywords, language = language_selected)
                        st.markdown(result)

    with st.expander("Product ideation"):
        display_biz_result(company, market, business_idea, 'Product ideation', queries_product_ideation, language = language_selected)
    with st.expander("Product vision"):
        display_biz_result(company, market, business_idea, 'Product vision', queries_product_vision, language = language_selected)
    with st.expander("Product strategy"):
        display_biz_result(company, market, business_idea, 'Product strategy', queries_product_strategy, language = language_selected)
    with st.expander("Product roadmap"):
        display_biz_result(company, market, business_idea, 'Product roadmap', queries_product_roadmap, language = language_selected)
    with st.expander("Product metrics"):
        display_biz_result(company, market, business_idea, 'Product Metrics', queries_product_metrics, language = language_selected)
    with st.expander("Product positioning"):
        display_biz_result(company, market, business_idea, 'Product positioning', queries_product_positioning, language = language_selected)
    with st.expander("Product discovery"):
        display_biz_result(company, market, business_idea, 'Product discovery', queries_product_discovery, language = language_selected)
    with st.expander("Product design thinking"):
        display_biz_result(company, market, business_idea, 'Product design thinking', queries_product_designthinking, language = language_selected)    
    with st.expander("Product solutionizing"):
        display_biz_result(company, market, business_idea, 'Product solutionizing', queries_product_solutionizing, language = language_selected)
    with st.expander("Product documentation"):
        display_biz_result(company, market, business_idea, 'Product documentation', queries_product_documentation, language = language_selected)
    with st.expander("Product monetization"):
        display_biz_result(company, market, business_idea, 'Product monetization', queries_product_monetization, language = language_selected)
    with st.expander("Product launch"):
        display_biz_result(company, market, business_idea, 'Product launch', queries_product_launch, language = language_selected)
    with st.expander("Product experimentation"):
        display_biz_result(company, market, business_idea, 'Product experimentation', queries_product_experimentation, language = language_selected)
    with st.expander("Product team"):
        display_biz_result(company, market, business_idea, 'Product team', queries_product_team, language = language_selected)
    with st.expander("Product growth"):
        display_biz_result(company, market, business_idea, 'Product growth', queries_product_growth, language = language_selected)
    with st.expander("Product copy"):
        display_biz_result(company, market, business_idea, 'Product copy', queries_product_copy, language = language_selected)


if __name__ == "__main__":
    run()
