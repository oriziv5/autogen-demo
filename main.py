import asyncio
import datetime
import requests
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.task import Console, TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models import AzureOpenAIChatCompletionClient
from dotenv import load_dotenv, dotenv_values
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from autogen_agentchat.base import TaskResult

# Load environment variables from .env file
load_dotenv()

# Create the token provider
token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

# Load the configuration
config = dotenv_values(".env")

# Create the model client
model_client=AzureOpenAIChatCompletionClient(
            azure_endpoint=config["AZURE_OPENAI_ENDPOINT"],
            model=config["AZURE_OPENAI_MODEL"],
            api_version=config["AZURE_OPENAI_API_VERSION"],
            azure_ad_token_provider=token_provider,
            # we can set the temperature to 0 to get deterministic results
            temperature=0
)

# Define a tool
async def get_weather(city: str) -> str:
    return f"The weather in {city} is 73 degrees and Sunny."

async def get_time(city: str) -> str:
    # Call a free API to get the time for a given city
    city = city.replace(" ", "_")
    response = requests.get(f"http://worldtimeapi.org/api/timezone/{city}")
    if response.status_code == 200:
        data = response.json()
        datetime_str = data["datetime"]
        human_time = datetime.datetime.fromisoformat(datetime_str).strftime('%Y-%m-%d %H:%M:%S')
        print(f"The time in {city} is {human_time}.")
        return f"The time in {city} is {human_time}."
    else:
        return f"Could not retrieve the time for {city}."

async def get_time_local(city: str) -> str:
    return f"The time in {city} is 12:00 PM."

async def main() -> None:
    # Define a weather agent
    weather_agent = AssistantAgent(
        name="weather_agent",
        model_client=model_client,
        tools=[get_weather],
        description="Agent that provides weather information for a given city.",
        system_message="You are helpful AI assistant, use tools to solve tasks about weather. Respond only with the weather",
    )

    # Define a time agent
    time_agent = AssistantAgent(
        name="time_agent",
        description="Agent that provides time information for a given city.",
        system_message="Use tools to solve tasks about getting the time, respond only with the time. ",
        model_client=model_client,
        tools=[get_time_local],
    )

    # Create the supervisor agent.
    supervisor_agent = AssistantAgent(
        "supervisor_agent",
        model_client=model_client,
        description="agnent that act as supervisor and provide feedback on the other agents' responses.",
        system_message="Provide short feedback. Check that user query was resolved. Respond with 'APPROVE' to when your feedbacks are addressed and conclude the final answer to the user before that.",
    )

    # Create the report agent.
    report_agent = AssistantAgent(
        name="report_agent",
        model_client=model_client,
        description="agent that generate an answer based on the other agents' responses and after APPROVE is received.",
        system_message="You are a helpful assistant that can summearize the conversation and provide the final answer to the user. When you done with generating the answer, reply with TERMINATE.",
    )    

    # Define termination condition
    text_termination = TextMentionTermination("TERMINATE")
    max_message_termination = MaxMessageTermination(10)
    termination = text_termination | max_message_termination

    # Create a team of agents
    agent_team = RoundRobinGroupChat([
        weather_agent, 
        time_agent,
        supervisor_agent,
        report_agent
    ], termination_condition=termination)

    # Run the team with the user's query and stream messages to the console
    user_query = input("Enter your query: ")
    # stream = agent_team.run_stream(task=user_query)
    # await Console(stream)
    await run_team_stream(agent_team=agent_team, task=user_query)


async def run_team_stream(agent_team: RoundRobinGroupChat , task) -> None:
    async for message in agent_team.run_stream(task=task):
        if isinstance(message, TaskResult):
            print(message.messages[-1].content)
        else:
            print(message.content)


asyncio.run(main())