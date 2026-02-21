import win32com.client
import os

docx_path = os.path.abspath('IEEE onference-template-a4.docx')
out_path = os.path.abspath('IEEE_Paper_Draft.docx')

word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = False

try:
    doc = word.Documents.Open(docx_path)
    
    # 1. Replace Abstract
    abstract_text = "This paper presents the development and evaluation of a novel autonomous web vulnerability scanner powered by a Reinforcement Learning (RL) agent. Traditional vulnerability testing relies heavily on either static heuristics or manual penetration testing, which are often time-consuming, unscalable, and prone to missing complex exploit chains. To address these limitations, we formulate the vulnerability discovery process as a Markov Decision Process (MDP) and implement a Double Dueling Deep Q-Network (D3QN) architecture with Experience Replay. The agent is trained within a specifically engineered Gymnasium environment, WebSecurityGym, interacting with dynamic mock applications reflecting real-world vulnerabilities such as SQL Injection (SQLi) and Cross-Site Scripting (XSS). Through a Phase-Based Learning strategy prioritizing reconnaissance before exploitation, the agent demonstrates a high capability of autonomously chaining attacks to uncover severe vulnerabilities while mitigating false positives and evading simulated Web Application Firewalls (WAFs)."
    
    # In IEEE templates, Abstract starts with "Abstract—" or "Abstract —" or "Abstract-"
    # The exact placeholder text in the document starts with "This electronic document is a"
    for p in doc.Paragraphs:
        if "This electronic document is a" in p.Range.Text:
            # Replaces the text but tries to preserve style
            p.Range.Text = abstract_text + "\n"
            break
            
    # 2. Replace Introduction
    intro_text = (
        "The proliferation of web-based applications has exponentially expanded the attack surface available to malicious actors. Despite the prevalence of automated security analysis tools, such as Dynamic Application Security Testing (DAST) scanners, human penetration testers remain essential for identifying complex logical flaws and multi-step attack chains. While human expertise is difficult to replicate, manual security auditing suffers from scalability issues, high costs, and varying levels of consistency. Consequently, there is an urgent need for intelligent, automated systems capable of mimicking the adaptive strategies employed by human hackers.\n\n"
        "In recent years, Artificial Intelligence, particularly Reinforcement Learning (RL), has emerged as a state-of-the-art methodology for solving complex, dynamic decision-making problems. RL provides an optimal paradigm for cybersecurity applications where an agent learns to interact with an environment to maximize a defined reward signal. In the context of web application security, an RL agent can continuously probe an application, interpret HTTP responses, and dynamically adjust its exploit payloads until a vulnerability is successfully triggered.\n\n"
        "This research proposes an autonomous web vulnerability scanner governed by a Deep Q-Network (DQN) agent. The primary contributions of this work are threefold: First, the design of WebSecurityGym, a custom reinforcement learning environment bridging HTTP interactions into numerically represented states and distinct exploit actions. Second, the implementation of a Double Dueling Deep Q-Network (D3QN) tailored for high-dimensional action spaces representing various payloads. Third, the introduction of a Phase-Based Learning strategy that successfully guides the agent from basic reconnaissance to advanced exploitation, accelerating convergence and improving stability. We evaluate our RL-based orchestrator against heavily customized, deliberately vulnerable mock targets, demonstrating significant potential for scalable and intelligent automated security auditing."
    )
    for p in doc.Paragraphs:
        if "This template, modified in MS" in p.Range.Text:
            p.Range.Text = intro_text + "\n"
            break

    # 3. Adding Methodology section at the end of the document
    rng = doc.Content
    rng.Collapse(0) # Collapse to the end
    
    rng.InsertParagraphAfter()
    rng = doc.Content
    rng.Collapse(0)
    rng.Text = "III. METHODOLOGY"
    rng.Style = "Heading 1"
    
    rng.InsertParagraphAfter()
    rng = doc.Content
    rng.Collapse(0)
    rng.Text = "This section details the design, architecture, and implementation of the proposed Reinforcement Learning (RL) based autonomous vulnerability scanner. The methodology is structured around the core components of the system: the system architecture, the formulation of vulnerability scanning as a Markov Decision Process (MDP), the design of the Deep Q-Network (DQN) agent, and the implementation of the simulation environment."
    rng.Style = "Normal"
    
    # Heading 2
    rng.InsertParagraphAfter()
    rng = doc.Content
    rng.Collapse(0)
    rng.Text = "A. System Architecture"
    rng.Style = "Heading 2"
    
    # Body
    rng.InsertParagraphAfter()
    rng = doc.Content
    rng.Collapse(0)
    rng.Text = "The autonomous vulnerability scanner is built upon a modular architecture designed to decouple the AI decision-making process from the underlying HTTP execution engine. The system comprises three primary modules:\n1) The Target Environment (WebSecurityGym): A custom-built OpenAI Gymnasium-compatible environment that simulates realistic web applications. It translates HTTP responses into numerical state vectors and processes the agent's actions into actual security payloads.\n2) The RL Agent (DQNAgent): A Deep Q-Network implementation utilizing a Dueling network architecture with experience replay. This module acts as the 'brain', learning to sequence attacks to maximize the discovery of vulnerabilities.\n3) The Orchestrator (SecurityAuditor & WebsiteExplorer): A functional wrapper that acts as the 'body'. It handles initial reconnaissance (crawling the target URL, extracting forms, and finding endpoints) and executes the actions selected by the agent against the target infrastructure."
    rng.Style = "Normal"

    # Heading 2 Let's just do B, C, D to keep it simple and clean
    rng.InsertParagraphAfter()
    rng = doc.Content
    rng.Collapse(0)
    rng.Text = "B. Formulation of the RL Environment (MDP)"
    rng.Style = "Heading 2"
    
    rng.InsertParagraphAfter()
    rng = doc.Content
    rng.Collapse(0)
    rng.Text = "To apply reinforcement learning to security testing, the interaction between the scanner and the web application is modeled as a Markov Decision Process (MDP). A 15-dimensional state representation is utilized, including HTTP Response Metrics, Structural Indicators, and Security Context. The system utilizes a discrete action space comprising up to 150 distinct operations aligned with the Cyber Kill Chain: Reconnaissance, Vulnerability Assessment, and Exploitation Actions."
    rng.Style = "Normal"

    rng.InsertParagraphAfter()
    rng = doc.Content
    rng.Collapse(0)
    rng.Text = "C. Agent Design and Training Strategy"
    rng.Style = "Heading 2"
    
    rng.InsertParagraphAfter()
    rng = doc.Content
    rng.Collapse(0)
    rng.Text = "The intelligence of the scanner is powered by a Double Dueling Deep Q-Network (D3QN). This architecture addresses overestimation bias inherent in standard DQN while efficiently learning the value of states independent of the actions taken. The reward function is meticulously shaped to encourage vulnerability discovery while penalizing noisy or repetitive behavior. Severe penalties are applied for triggering WAF rules or rate limits (-0.1), directly discouraging brute-force behavior. To optimize training instability, a Phase-Based Learning algorithm is introduced, dynamically unlocking assessment and exploitation actions."
    rng.Style = "Normal"

    doc.SaveAs(out_path)
    print("Modifications saved to " + out_path)

except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    try:
        doc.Close(SaveChanges=False)
    except:
        pass
    word.Quit()
