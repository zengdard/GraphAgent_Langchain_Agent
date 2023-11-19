import json
from langchain.memory import ConversationBufferWindowMemory
from langchain.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain.tools import BraveSearch, Tool
from langchain.indexes.graph import NetworkxEntityGraph
from grandcypher import GrandCypher
from langchain.chains import GraphQAChain
import pickle
import networkx as nx
import langchain
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType


wikipedia = WikipediaAPIWrapper()
arxiv = ArxivAPIWrapper()
brave = BraveSearch.from_api_key(api_key="BSAzgLCqFawrEF2MvN4tOustnBbkinZ", search_kwargs={"count": 5})

langchain.debug = True  

class learning_agent:
    pass

class SharedMemory:
    def __init__(self):
        """
        Initialise la mémoire partagée avec un dictionnaire vide pour stocker les informations
        et un dictionnaire de liens.
        """
        self.memory = {}
        self.links = {}

    def write_memory(self, data):
        """
        Stocke une information dans cet espace de mémoire.

        Args:
            data (str): Une chaîne de caractères contenant une paire clé-valeur séparée par un tiret '-', de cette manière key - value.

        Returns:
            None

        Examples:
            - Input: "example_key, example_value - another_key, another_value"
              Output: "Memory spaces created with keys 'example_key' and 'another_key' and values 'example_value' and 'another_value'."

            - Input: "key, value"
              Output: "Memory space created with key 'key' and value 'value'."
        """
        try:
            pairs = data.split('-')
            self.memory[pairs[0]] = pairs[1]
            return f"Memory spaces created with keys {pairs[0]}."
        except Exception as a:
            print(str(a))
            return 'Formatte votre demande de cette manière : key - value'


    def read_memory(self, number):
        """
        Récupère une information stockée dans cet espace de mémoire.

        Args:
            number: L'identifiant unique pour cette information.

        Returns:
            information (str): L'information stockée, ou None si elle n'existe pas.

        Examples:
            - Input: "'example_key'"
              Output: "Value associated with 'example_key': 'example_value'."

            - Input: "'another_key'"
              Output: "Value associated with 'another_key': 'another_value'."

        """
        if number not in self.memory:
            return  KeyError(f"La clé '{number}' n'existe pas dans la mémoire.")

        return self.memory.get(number, None)

    def suivre_liens(self, numero):
        return self.liens.get(numero, {})

    def obtenir_empreinte(self):
        """Récupère toutes les informations stockées dans cet espace de mémoire.
        arguments:
            None
        returns:
                empreinte (dict): un dictionnaire contenant toutes les informations stockées dans cet espace de mémoire"""
        empreinte = {}
        empreinte["informations"] = self.memoire
        empreinte["liens"] = self.liens
        return empreinte
    
    def read_memory_par_lien(self, numero_lien):
        informations_liees = []
        for numero, liens in self.liens.items():
            if numero_lien in liens:
                information = self.memoire.get(numero)
                if information:
                    informations_liees.append((numero, information))
        return informations_liees
    
class Graph_Agent:
    def __init__(self, data_path, api_key):
        self.data_path = data_path.replace(' ', '_')
        self.G = nx.read_gml(f"{self.data_path}/{self.data_path}.gml")
        self.Cypher_back_graph = GrandCypher(self.G)
        self.api_key = api_key
        self.memory = ConversationBufferWindowMemory(k=10, memory_key='chat_history')
        self.Memory_Agent = SharedMemory()



        with open(f'{self.data_path}/node_info.json', 'r',  encoding='utf-8') as fichier_json:
                 self.donnees_json = json.load(fichier_json)


        # Create LLM
        self.llm = ChatOpenAI(
            openai_api_key='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',
            model_name='gpt-3.5-turbo-16k',
            temperature=0.1
        )
        
        self.graph_qa = GraphQAChain.from_llm(
            llm=self.llm,
            graph=NetworkxEntityGraph.from_gml(f'{self.data_path}/{self.data_path}.gml'),
            verbose=True
        )

        self.tools = [
             Tool(
               name="write_memory",
                description="Create a memory space, you can write information in this memory. Input should be a like NAME,INFORMATION - NAME-INFORMATION .",

               func=self.Memory_Agent.write_memory),
            Tool(
               name="read_memory",
               description="Recupere les informations stockées dans cet espace de mémoire.",
               func=self.Memory_Agent.read_memory),
            Tool(
                name="node_information",
                func=self.node_information,
                description="Un outil qui te permet de récupérer toutes les metadonnées liées à un noeud dans le graphe",
            ),
           # Tool(
           #     name="liaison",
           #     func=self.liaison,
           #     description="A tool that returns all nodes in the graph",
           # ),
           # Tool(
           #     name='WikipediaQID',
           #     description='Search node with a wikipedia QID',
           #     func=self.WikipediaQID
           # ),
             #Tool(
             #   name='search_url_of_node_with_id',
             #   func=self.search_url_of_node_with_id,
             #   description='Search connected nodes of Question node with Title '),
            Tool(
                name='Noeuds_Proches',
                func=self.Noeuds_Proches,
                description='Search connected nodes of Question node with Title'),
            Tool(name="list_of_nodes",
                func=self.list_of_nodes,
                description='Return all nodes in the graph. The input to this tool should be a comma separated list of nodes.'),

            #Tool(name="find_all_relationships_between_nodes",
            #     func=self.find_all_relationships_between_nodes,
            #     description='Found type Relation between 2 nodes in the Networkx Graph, need the 2 nodes ')
        ]

        with open(f"{self.data_path}/{self.data_path}.gml", 'r') as gml_file:
            # Utilisez la méthode readlines pour lire les premières lignes
            lignes = gml_file.readlines()[:30]

        history = '''Oublie tout ce que tu sais n'invente rien, base toi sur ce que je te donne via les tools que je te donne 
        Tu es l'équivalent de Socrate en terme de réflexion. Tu es totalement neutre, et chaque propositions qu'on te propose est équivalente à toutes autres.
 
        Tu es un agent qui répond uniquement aux demandes d'un autre agent afin de l'aider à raisonner sur l'actualité en fonction d'un graph de connaissances.
        
        Voici un extrait du graph et des nodes qui le composent : {lignes}.
        '''
        history2 = ''' Voici un EXEMPLE de réflexion : 
        DEBUT EXEMPLE
        Demande : Quelles sont les relations entre les 2 corées ?
        Cherche les liaisons du node 'Parle_moi_du_regain_de_tensions_entre_la_Cor&#233;e_du_Nord_et_du_Sud' function Noeuds_Proches(node1)
        Le node 'Quelles sont les derni&#232;res actualit&#233;s sur les relations entre la Cor&#233;e du Nord et la Cor&#233;e du Sud ?' se prête le mieux pour répondre à cette question.
        Récupération des liaisons du noeud. function Noeuds_Proches(node1)
        Ces nodes si semblent intéressant : North Korea&#8211;South Korea relations - BBC News , South Korea - Relations, Divisions, Reunification | Britannica. 
        Récupération des informations liées aux nodes via la recherche URL associée à chaque node. function make_node_search(node)
        Retourne tous ces éléments à l'agent cognitif.
        FIN EXEMPLE
            '''

        self.memory.chat_memory.add_user_message(history)
        self.memory.chat_memory.add_user_message(history2)
        self.agent_executor = initialize_agent(
            self.tools, self.llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True, memory=self.memory)
        


    def find_all_relationships_between_nodes(self, node1, node2):
        '''Return the relation type between Node1 & Node2'''
        return self.Cyhper_back_graph.run(f'''MATCH (A)-[relation]->(B)
            WHERE A.label == "{node1}, B.label == {node2}
            return A, B, type(relation) AS type_de_relation''')

    def liaison(self, node1, node2):
        '''Return the relation type between Node1 & Node2
        
        arguments:
            node1 (str): the first node
            node2 (str): the second node
        returns:
            list of relations (list): a list of all relations between node1 and node2
        '''
        return list(nx.all_simple_paths(self.G, source=node1, target=node2))

    def Noeuds_Proches(self, node):
        try:
            return list(self.G.neighbors(node))
        except:
            return 'Noeud non présent dans le graph, cherche d abord la liste pour bien orthographier le noeud'
        
    def list_of_nodes(self, passs):
        '''Return all nodes in the graph
        arguments:
            passs (str): a passs to use this function
        returns:
            list of nodes (list): a list of all nodes in the graph
                
                '''
        return list(self.G.nodes)

    def node_information(self, noeud):
        if self.G.has_node(noeud):
            try:  
                attributs_du_noeud = self.G.nodes[noeud]
                url_du_noeud = self.donnees_json[noeud.replace('_', ' ')]['url']
                search = brave.run(f'''{url_du_noeud}''')
                return search
            except:
                return 'noeud non présent dans le graph, cherche d abord la liste pour bien orthographier le noeud'
        else:
            return 'noeud non présent dans le graph, cherche d abord la liste pour bien orthographier le noeud'
        
    def make_node_search(self, noeud):
        if self.G.has_node(noeud):
            attributs_du_noeud = self.G.nodes[noeud]
            url_du_noeud = attributs_du_noeud['URL']
            search = brave.run(f'''{noeud}''')
            return search
        else:
            return 'noeud non présent dans le graph, cherche d abord la liste pour bien orthographier le noeud'


    def WikipediaQID(self, QID):
        for key, value in self.responses.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "Q_ID" in item and item["Q_ID"] == QID:
                        return value

        return 'Article Wikipédia non trouvé, essayez une autre méthode'

    def request_from_graph_agent(self, request):
        '''Request from cognitive agent'''

        Prompt_Message_Pre_cognitive_agent = f""" 
        Egalement le Graph au format GML, te permettra de comprendre leurs relations.
        Chaque noeud article répond au noeud question qui lui est connecté, tu peux d'aider en regardant leurs liaisons 
       
        Ton unique but est répondre uniquement aux questions de l'agent congitif en fonction des informations que tu trouves sur ce graph,
        Tu as accés à tous ces tools : {[tool.name for tool in self.tools]}
        Thème du graph : {self.data_path}
        
        Voici la demande de l'user {request}
        Fais ta réponse en citant toujours tes sources précisément par rapport au graph ou à tes recherche brave. De la même manière que Wikipedia fais dans ses articles.
        """
        response = self.agent_executor.run(Prompt_Message_Pre_cognitive_agent)
        return response

class CognitiveAgent:
    def __init__(self, data_path, api_key):
        self.data_path = data_path.replace(' ', '_')
        self.api_key = api_key
        self.memory = ConversationBufferWindowMemory(k=10, memory_key='chat_history')
        self.graph_agent  = Graph_Agent(data_path=self.data_path, api_key=self.api_key)
        self.Memory_Agent = SharedMemory()
        
        with open(f'{self.data_path}/{self.data_path}.pkl', "rb") as file:
             loaded_graph = pickle.load(file)

        # Create LLM
        self.llm = ChatOpenAI(
            openai_api_key='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',
            model_name='gpt-3.5-turbo-16k',
            temperature=0.1
        )

        self.tools = [
            #Tool(
            #    name="brave",
            #    description="Search in google.",
            #    func=brave.run),

            Tool(
                name="request_from_graph_agent",
                description='Request from cognitive agent',
                func=self.graph_agent.request_from_graph_agent),
           Tool(
                name="write_memory",
                description="Create a memory space, you can write information in this memory. Input should be a string séparée par un tiret '-', de cette manière key - value ",
                func=self.Memory_Agent.write_memory
            ),

            Tool(
                name="read_memory",
                description="Read information in this memory.",
                func=self.Memory_Agent.read_memory
            )
        ]


##REFAIRE pour que l'agent comprenne le sujet général de la conversation et qu'il puisse répondre à des questions plus générales en ayant la possibilié de mieux comprendre également les questions de l'user le thème via des requêtes RDFs
        
        triplets = [(subject, predicate, obj) for subject, obj, predicate in loaded_graph.edges(data=True)]
        print(triplets)
        # Ici, nous convertissons chaque triplet en une chaîne formatée pour l'affichage.
        formatted_triplets = [
    ' - '.join([subject, json.dumps(predicate), json.dumps(obj)])
    for subject, predicate, obj in triplets
]

        
        Analysis = f"""
        Use the following knowledge triplets to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

        {formatted_triplets}

        
        How you can read it : The triplets indicate that the relations between North Korea and South Korea have been characterized by 'intermittent periods of sunshine policy and mutual provocation'.
        The subject of the graph is: {self.data_path}

        
        """
        self.memory.chat_memory.add_user_message(Analysis)

        self.agent = initialize_agent(
            self.tools, self.llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True, memory=self.memory)

    def search(self, quest, prompt=None):
        quest_f =f""" You are akin to Socrates in terms of reflection, which means you must examine each proposition with absolute neutrality. Every piece of information you receive must be treated with the same objectivity, without any preference or prejudice.

        Based on the knowledge triplets provided and the tools at your disposal, you must analyze the question posed and provide an enlightened response. It is crucial that you cite your sources precisely, referring to specific triplets or the findings obtained through your tools to substantiate your response.

        Here is the question you need to address:
        {quest}

        Use the triplets in your historic to construct your answer or use your tools. If can't answer this, state this clearly in your response.

        Respond in accordance with the context of the conversation and the details of the topic discussed. Remember to provide as accurate responses as possible, based solely on the reliable information at your disposal.
        Return your respone all times.
        
        """
        response = self.agent.run(quest_f)
        self.memory.chat_memory.add_user_message(response)
        return response

#agent_1 = CognitiveAgent(data_path="Parle moi du regain de tensions entre la Corée du Nord et du Sud", api_key='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')
#agent_1.search('Parle moi globalement du sujet coréen')


#CODER LES ARBRES DE REFLEXION
#CODER TOUTES LES FONCTIONS DE RECHERCHE & REFLEXION + MEMOIRE TAMPONS
#CODER L'AGENT DE REFLEXION AVEC FONCTION DE RECOMPENSE POUR L4AGENT COGNITIF
