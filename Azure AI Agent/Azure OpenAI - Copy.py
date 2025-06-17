import os
from dotenv import load_dotenv
from pathlib import Path


# Add references
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FilePurpose, CodeInterpreterTool, MessageRole



def main(): 

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    project_endpoint= os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

    # Display the data to be analyzed
    script_dir = Path(__file__).parent  # Get the directory of the script
    file_path = script_dir / 'data.txt'

    with file_path.open('r') as file:
        data = file.read() + "\n"
        print(data)

    #Create project client
    project_client = AIProjectClient(
        credential=DefaultAzureCredential(),
        endpoint=project_endpoint
    )

    with project_client:

        # Upload the data file and create a CodeInterpreterTool
        file = project_client.agents.files.upload_and_poll(
            file_path=file_path, purpose=FilePurpose.AGENTS
        )
        print(f"Uploaded {file.filename}")        

        #Define code interpreter
        code_interpreter = CodeInterpreterTool(file_ids=[file.id])

        #Create an agent
        agent =project_client.agents.create_agent(
            model=model_deployment,
            name='data-agent',
            instructions="You are an AI agent that analyzes the data in the file that has been uploaded. If the user requests a chart, create it and save it as a .png file.",
            tools= code_interpreter.definitions,
            tool_resources= code_interpreter.resources,
        )

        #Create thread.
        thread = project_client.agents.threads.create()

        while True:
            user_input = input("Please write your input (or 'quit' to exit): ")
            if user_input.lower() == 'quit':
                break
            if len(user_input) == 0:
                print("Please enter a prompt.")
                continue


            #Create Message
            message = project_client.agents.messages.create(
                thread_id=thread.id,
                role='user',
                content= user_input
                )
            
            # Start the run
            run = project_client.agents.runs.create_and_process(
                thread_id=thread.id,
                agent_id=agent.id
            )

            # Get latest agent message
            agent_response = project_client.agents.messages.get_last_message_by_role(
                thread_id=thread.id,
                role=MessageRole.AGENT
            )
            if agent_response:
                content = agent_response.get('content', [])
                if content and content[0].get('text', {}).get('value'):
                    print(f"Agent Response: {content[0]['text']['value']}")

                attachments = agent_response.get('attachments', [])
                if attachments and attachments[0].get('file_id'):
                    file_id = attachments[0]['file_id']

                    # Placeholder for dynamic file name generation
                    ## Might want to change file_name to something more good looking.
                    project_client.agents.files.save(file_id=file_id, file_name=f'{file_id}.png')




        #Delete agent after use.
        project_client.agents.delete_agent(agent_id=agent.id)


if __name__ == '__main__': 
    main()

