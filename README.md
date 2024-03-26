# Project Description

This project is a learning agent that uses various APIs and tools to gather and process information, store it in a shared memory, and use it to answer user queries. The agent is designed to be neutral and objective, providing accurate responses based on reliable information.

## Features

- Uses WikipediaAPIWrapper, ArxivAPIWrapper, and BraveSearch to gather information.
- Stores information in a shared memory using a custom SharedMemory class.
- Uses GraphQAChain and NetworkxEntityGraph to process and analyze the information.
- Uses OpenAI's ChatOpenAI model for natural language processing.
- Implements a Graph Agent and a Cognitive Agent to handle user queries.

## Classes

- `learning_agent`: An empty class for future development.
- `SharedMemory`: A class to handle storing and retrieving information in a shared memory.
- `Graph_Agent`: A class that uses various tools to gather and process information, and answer user queries.
- `CognitiveAgent`: A class that interacts with the Graph Agent to handle user queries.

## Tools

- `write_memory`: A tool to write information into the shared memory.
- `read_memory`: A tool to read information from the shared memory.
- `node_information`: A tool to retrieve metadata related to a node in the graph.
- `Noeuds_Proches`: A tool to search for nodes connected to a specific node.
- `list_of_nodes`: A tool to return all nodes in the graph.

## Requirements

- json
- langchain
- networkx
- pickle
- GrandCypher
- OpenAI API key
- BraveSearch API key

## Usage

Initialize a CognitiveAgent with a data path and an API key, then use the search method to ask questions. The agent will use the tools at its disposal to find the answer and respond with a detailed response, citing its sources.

## Running the Application

The project also includes a Flask application that allows users to interact with the agent through a web interface. To run the application, set the `OPENAI_API_KEY` environment variable to your OpenAI API key, then run `flask run`. The application will be accessible at `http://localhost:5000`.

## File Structure

- `main.py`: The main file containing the classes and tools.
- `app.py`: The Flask application file.
- `templates/interface_user.html`: The HTML template for the Flask application.
- Data directory: Contains the data used by the agent, including the graph data and node information.

## Future Work

- Implement the `learning_agent` class.
- Add more tools for information gathering and processing.
- Improve the agent's ability to understand and respond to complex queries.
- Enhance the shared memory to store and retrieve information more efficiently.
