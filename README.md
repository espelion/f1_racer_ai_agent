<!-- For template See:https://github.com/othneildrew/Best-README-Template/blob/master/README.md  -->

<br />
<div align="center">
  <a href="https://github.com/praekelt/eskom-bot">
    <img src="AIRacer.png" alt="Logo" width="80" height="80">
  </a>
    <h3 align="center">F1 Racer AI Agent</h3>
  <p align="center">
    A basic AI agent that can mimic the persona and behavior of a Formula One racer, suitable for social media interactions.
    <br />
    <a href="https://github.com/espelion/f1_racer_ai_agent/issues">Report Bug</a>
    ·
    <a href="https://github.com/espelion/f1_racer_ai_agent/issues/new?labels=enhancement&template=feature-request">Request Feature</a>
  </p>
</div>


<details id="top">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#docker">Docker</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#examples">Example Scenarios</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>


## About The Project <a id="about-the-project"></a>

This project introduces the F1 Racer AI Agent, a Python-based application designed to simulate the persona and social media interactions of a Formula One racer. The agent is capable of generating text, such as posts and comments, that reflect the typical vocabulary, sentiments (like determination, excitement, or disappointment), and style of an F1 driver. It can also simulate actions like "replying" to comments, "posting" status updates, "liking" posts, and "mentioning" others. A key feature is its basic contextual awareness, allowing it to tailor responses based on a simulated race weekend context, including the current race stage (e.g., practice, qualifying, race) and recent results. This project aims to explore natural language processing and agent design principles to create an engaging and believable AI persona.

<p align="right">(<a href="#top">back to top</a>)</p>


### Built With <a id="built-with"></a>
This F1 Racer AI Agent is built with `Python 3.11` and is designed for containerization using `Docker`. The agent's text generation can be extended with NLP libraries such as NLTK or Transformers (e.g., from Hugging Face), and potentially leverage Large Language Models like Gemini, though the current primary implementation uses a template-based approach.
* [![Python][Python]][Python-url]
* [![Docker][Docker]][Docker-url]
* [![NLTK][NLTK]][NLTK-url]
* [![Gemini][Gemini]][Gemini-url]
* [![Hugging-face][Hugging-face]][Hugging-face-url]

<p align="right">(<a href="#top">back to top</a>)</p>


## Getting Started  <a id="getting-started"></a>

```
f1_agent_project/
├── agent/
│   ├── __init__.py
│   ├── state.py
│   ├── text_generator.py
│   ├── actions.py
│   ├── racer.py
│   └── utils.py
├── agent/
│   ├── __init__.py
│   ├── consts.py
│   └── logger.py
├── f1_agent.py
├── Dockerfile
├── requirements.txt
├── logger.json
└── README.md
```

This F1 Racer AI Agent runs on `Python 3.11`. It utilizes either a basic logging setup or a more nuanced logging set up using a dict config located at `logger.json` as seen above, `logger.py` loads the config or defaults to a basic logger. For local development and running, no specific complex environment variable configurations are required beyond standard `Python` and `NLTK` for for sentiment analysis.

### Prerequisites <a id="prerequisites"></a>

Ensure you have Python 3.11 installed. It's recommended to use a virtual environment for managing dependencies.
*   Python 3.11
*   pip

### Installation <a id="installation"></a>

_Follow these steps to get your development environment running._

1.  Clone the repo
    ```sh
    git clone https://github.com/espelion/f1_racer_ai_agent.git
    cd f1_racer_ai_agent
    ```
2.  Create and activate a Python 3.11 virtual environment:
    ```sh
    python3.11 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  Install dependencies from `requirements.txt`:
    ```sh
    pip install -r requirements.txt
    ```
4.  Run the application:
    ```sh
    python f1_agent.py
    ```
    You can also specify the text generator (though "basic" is the default and currently the only option implemented):
    ```sh
    python f1_agent.py --text-generator basic
    ```

<p align="right">(<a href="#top">back to top</a>)</p>

### Docker <a id="docker"></a>

_The application includes a `Dockerfile` for easy containerization and execution._

1.  Build the Docker image. Navigate to the project's root directory (where the `Dockerfile` is) and run:
    ```sh
    docker build -t f1-racer-agent .
    ```
2.  Run the Docker container interactively:
    ```sh
    docker run -it --rm f1-racer-agent
    ```
    To run with specific arguments (e.g., explicitly setting the text generator):
    ```sh
    docker run -it --rm f1-racer-agent --text-generator basic
    ```

<p align="right">(<a href="#top">back to top</a>)</p>


## Usage <a id="usage"></a>

The F1 Racer AI Agent is run as an interactive command-line application. After starting the agent (either directly via Python or using Docker as described in the <a href="#getting-started">Getting Started</a> section), you can interact with it by typing commands into the terminal.

Type `help` in the agent's command prompt to see the list of available commands for simulating racer actions and updating context. These are the available options at the moment:

```
  help                            - Show this help message.
  quit / q                        - Exit the interactive mode.
  state                           - Show current agent state and race name.
  stage <new_stage>               - Update agent's current race stage (Example: FP1, Q2, Race).
  result <new_result>             - Record agent's last race result (Example: P1, P5, DNF).
  racename <new_race_name>        - Set the current race name (Example MonzaGP).
  post                            - Agent generates and 'posts' a status update based on current context.
  reply <fan_comment_text>        - Agent generates a 'reply' to the given fan comment.
  mention <entity> [message]      - Agent 'posts' mentioning an entity. Message is optional (defaults to 'Great job by {mention}!').
                                    Example: mention MyMechanic
                                    Example: mention Sponsor Great race thanks!
  like "<post_content>" [author]  - Agent 'likes' a post. Author is optional (defaults to 'Trixie').
                                    Example: like "Well done team" - Note the ""
                                    Example: like "Good fight" Max - Note the ""
```

### Example Scenarios <a id="examples"></a>

Your agent should be able to generate outputs similar to the following (depending on its internal "thinking" state):

```
(FP1, Res: N/A, Race: SilverstoneGP) > stage q3
(Q3, Res: N/A, Race: SilverstoneGP) >
(Q3, Res: N/A, Race: SilverstoneGP) > result p2
(Q3, Res: P2, Race: SilverstoneGP) >
(Q3, Res: P2, Race: SilverstoneGP) > post
Agent posted: Fantastic result! P2 on the grid for #SilverstoneGP GP! The Mach 5 was flying in Q3. #TeamMach 5 did an amazing job. Great spot to attack from tomorrow! #F1 #Qualifying #FrontRowsCalling 💨
(Q3, Res: P2, Race: SilverstoneGP) > mention max What a great race dude!
Agent posted with mention: What a great race dude!, Big shoutout to @max!
(Q3, Res: P2, Race: SilverstoneGP) > like "Max is the one" trixie
2025-05-18T14:22:56 INFO agent.actions:28 Action: Liking post from trixie: "Max is the one"
(Q3, Res: P2, Race: SilverstoneGP) > reply I love you Go!
Agent replied: Go Mifune replies: Love the energy! 🚀 Your cheers make a massive difference out on track. So glad you enjoyed it! #Mach5Speed #BestFans
(Q3, Res: P2, Race: SilverstoneGP) > q
2025-05-18T14:23:33 INFO __main__:50 Exiting interactive mode.
```

It is important the set an initial state via `stage` and `result` before the agent can engage.

<p align="right">(<a href="#top">back to top</a>)</p>


## Contact

Project Link: https://github.com/espelion/f1_racer_ai_agent
Email: mfundo@espelion.com

For issues or feature requests, please use the GitHub Issues page.

<p align="right">(<a href="#top">back to top</a>)</p>


[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://python.org/
[Docker]: https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff&style=for-the-badge
[Docker-url]: https://docs.docker.com/
[NLTK]: https://img.shields.io/badge/NLTK-0C9A9A?style=for-the-badge&logo=nltk&logoColor=white
[NLTK-url]: https://www.nltk.org/
[Gemini]: https://img.shields.io/badge/Google%20Gemini-886FBF?logo=googlegemini&logoColor=fff&style=for-the-badge
[Gemini-url]: https://ai.google.dev/gemini-api/docs
[Hugging-face]: https://img.shields.io/badge/Hugging%20Face-FFD21E?logo=huggingface&logoColor=000&style=for-the-badge
[Hugging-face-url]: https://huggingface.co/docs
