import os
import sqlite3
import pandas as pd
import base64
import matplotlib.pyplot as plt
from semantic_kernel import Kernel
from semantic_kernel.utils.logging import setup_logging
from semantic_kernel.functions import kernel_function, KernelFunctionFromPrompt
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.planners.function_calling_stepwise_planner import FunctionCallingStepwisePlanner
from azure.communication.email import EmailClient
import asyncio
from keys import *

setup_logging()

def csv_to_sqlite(csv_path):
    df = pd.read_csv(csv_path)
    os.makedirs("workspace", exist_ok=True)
    df.to_pickle("workspace/data.pkl")
    conn = sqlite3.connect("workspace/data.db")
    df.to_sql("data", conn, index=False, if_exists="replace")
    conn.close()

def run_pipeline(csv_path, user_goal):
    csv_to_sqlite(csv_path)

    kernel = Kernel()
    azure_service = AzureChatCompletion(
        service_id= keys["service_id"],
        deployment_name=keys["deployment_name"],
        endpoint=keys["endpoint"],
        api_key=keys["api_key"],
    )
    kernel.add_service(azure_service)

    @kernel_function(name="execute_sql", description="Execute a SQL query on the data and return the result.")
    def execute_sql(query: str) -> str:
        try:
            conn = sqlite3.connect("workspace/data.db")
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(results, columns=columns)
            df.to_pickle("workspace/sql_result.pkl")
            conn.close()
            return df.to_string(index=False)
        except Exception as e:
            return f"SQL Execution Error: {str(e)}"

    @kernel_function(name="run_plot", description="Execute matplotlib Python code to generate a plot.")
    def run_plot(code: str) -> str:
        local_vars = {}
        try:
            df = pd.read_pickle("workspace/sql_result.pkl")
            exec(code, {"df": df, "plt": plt}, local_vars)
            print(local_vars.keys())
            plot_path = "workspace/plot.png"
            plt.savefig(plot_path)
            plt.close()
            return f"Plot saved at {plot_path}"
        except Exception as e:
            return f"Plot Execution Error: {str(e)}"
    email_text_result =""
    @kernel_function(name="send_email", description="Send email with analysis result and optional plot image.")
    def send_email(body: str) -> str:
        #add your email connection string here
        connection_string = ""
        email_client = EmailClient.from_connection_string(connection_string)
        nonlocal email_text_result  
        email_text_result = body
        with open("workspace/plot.png", "rb") as file:
            image_contents = file.read()
        image_bytes_b64 = base64.b64encode(image_contents).decode()

        message = {
            "content": {
                "subject": "Analysis Report",
                "plainText": body,
                "html": f"<html><body><pre>{body}</pre></body></html>",
            },
            "recipients": {
                "to": [{"address": "v-kvinayak@microsoft.com", "displayName": "Kumar Vinayak"}],
            },
            "senderAddress": "DoNotReply@eb2f5da7-613b-4bbe-88d9-e50944365cbc.azurecomm.net",
            "attachments": [
                {
                    "name": "plot.png",
                    "contentType": "image/png",
                    "contentInBase64": image_bytes_b64,
                }
            ],
        }

        poller = email_client.begin_send(message)
        result = poller.result()
        return "Email sent."

    kernel.add_function("exec", execute_sql)
    kernel.add_function("exec", run_plot)
    kernel.add_function("exec", send_email)

    df = pd.read_pickle("workspace/data.pkl")
    schema_description = "".join([f"- {col} ({dtype})" for col, dtype in zip(df.columns, df.dtypes.astype(str))])
    print("Schema description:\n", schema_description)
    kernel.add_function(
            plugin_name="sql_writer",
            function=KernelFunctionFromPrompt(
                function_name="write_sql",
                prompt=f"""You are an SQL expert. The user asked: {user_goal}. Write a single SQL query using the table 'data'.

    The table 'data' has the following columns:
    {schema_description}""",
                description="Generate SQL query from user question, please check the schema and decide on your own what all columns to use."
            )
        )
    kernel.add_function(
        plugin_name="plot_generator",
        function=KernelFunctionFromPrompt(
            function_name="write_plot_code",
            prompt=f"""You are a Python data scientist. Write matplotlib code that uses the DataFrame `df` to create a bar chart from the query result. Always end your code with `plt.savefig('workspace/plot.png')`. The user asked: {user_goal}.

The DataFrame 'df' contains columns:
{schema_description}""",
            description="Generate matplotlib code from query"
        )
    )
    kernel.add_function(
        plugin_name="email_writer",
        function=KernelFunctionFromPrompt(
            function_name="write_email",
            prompt=f"""Write a professional summary email body explaining the result of the analysis. The user asked: {user_goal}.

The analysis is based on a table with these columns:
{schema_description}""",
            description="Write email summary for user"
        )
    )


    execution_settings = AzureChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    planner = FunctionCallingStepwisePlanner("gpt-4-32k")
    result = asyncio.run(planner.invoke(kernel=kernel, question=user_goal))
    print("Plan result:\n", result)
    return email_text_result

# if __name__ == "__main__":
#     run_pipeline("faker.csv", "SHow me all the cars and colors in the data and send via email.")
