from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph

from generate_ieee_formatted_docx import generate


BASE_DIR = Path(__file__).resolve().parent
SOURCE_PATH = BASE_DIR / "Research_Paper_Draft.docx"
INTERMEDIATE_PATH = BASE_DIR / "Research_Paper_Draft_submit_ready.docx"
OUTPUT_PATH = BASE_DIR / "Research_Paper_IEEE_Formatted_submit_ready.docx"
FALLBACK_OUTPUT_PATH = BASE_DIR / "Research_Paper_IEEE_Formatted_submit_ready_full.docx"
AUTHOR_DETAILS_PATH = BASE_DIR / "paper_author_details.json"


REFERENCE_ENTRIES = [
    "[1] R. Singh, M. K. Gupta, D. R. Patil, and S. M. Patil, \"Analysis of Web Application Vulnerabilities using Dynamic Application Security Testing,\" in Proc. IEEE 9th Int. Conf. Convergence in Technology (I2CT), 2024, pp. 1-6, doi: 10.1109/I2CT61223.2024.10543484.",
    "[2] R. Sri Devi and M. Mohan Kumar, \"Testing for Security Weakness of Web Applications using Ethical Hacking,\" in Proc. 4th Int. Conf. Trends in Electronics and Informatics (ICOEI), 2020, pp. 354-361, doi: 10.1109/ICOEI48184.2020.9143018.",
    "[3] C. Mainka, J. Somorovsky, and J. Schwenk, \"Penetration Testing Tool for Web Services Security,\" in 2012 IEEE Eighth World Congress on Services, 2012, pp. 163-170, doi: 10.1109/SERVICES.2012.7.",
    "[4] V. Sujatha, K. Lakshmi Prasanna, K. Niharika, V. Charishma, and K. Bhavya Sai, \"Network Intrusion Detection using Deep Reinforcement Learning,\" in Proc. 7th Int. Conf. Computing Methodologies and Communication (ICCMC), 2023, pp. 1146-1150, doi: 10.1109/ICCMC56507.2023.10083673.",
    "[5] V. Mnih et al., \"Human-level control through deep reinforcement learning,\" Nature, vol. 518, no. 7540, pp. 529-533, 2015, doi: 10.1038/nature14236.",
    "[6] T. Schaul, J. Quan, I. Antonoglou, and D. Silver, \"Prioritized Experience Replay,\" arXiv:1511.05952, 2015. [Online]. Available: https://arxiv.org/abs/1511.05952.",
    "[7] M. C. Ghanem and T. M. Chen, \"Reinforcement learning for efficient network penetration testing,\" Information, vol. 11, no. 1, Art. no. 6, 2020, doi: 10.3390/info11010006.",
    "[8] M. C. Ghanem, T. M. Chen, and E. G. Nepomuceno, \"Hierarchical reinforcement learning for efficient and effective automated penetration testing of large networks,\" J. Intell. Inf. Syst., vol. 60, no. 2, pp. 281-303, 2023, doi: 10.1007/s10844-022-00738-0.",
    "[9] H. Al Shaikh, S. Saha, K. Zamiri Azar, F. Farahmandi, M. Tehranipoor, and F. Rahman, \"Re-Pen: Reinforcement Learning-Enforced Penetration Testing for SoC Security Verification,\" IEEE Trans. Very Large Scale Integr. (VLSI) Syst., vol. 33, no. 3, pp. 853-866, 2025, doi: 10.1109/TVLSI.2024.3510682.",
    "[10] S. Zhou, J. Liu, Y. Lu, J. Yang, Y. Zhang, B. Lin, X. Zhong, and S. Hu, \"SCRIPT: A Scalable Continual Reinforcement Learning Framework for Autonomous Penetration Testing,\" Expert Syst. Appl., vol. 285, Art. no. 127827, 2025, doi: 10.1016/j.eswa.2025.127827.",
    "[11] J. Liu, Y. Zhang, S. Zhou, J. Yang, Y. Lu, and X. Zhong, \"Autonomous penetration testing using reinforcement learning: A review and perspectives,\" Expert Syst. Appl., vol. 300, Art. no. 130219, 2026, doi: 10.1016/j.eswa.2025.130219.",
    "[12] N. Singh, V. Meherhomji, and B. R. Chandavarkar, \"Automated versus Manual Approach of Web Application Penetration Testing,\" in Proc. 11th Int. Conf. Computing, Communication and Networking Technologies (ICCCNT), 2020, pp. 1-6, doi: 10.1109/ICCCNT49239.2020.9225385.",
    "[13] D.-Y. Kao, Y.-Y. Chen, and F.-C. Tsai, \"Hacking Tool Identification in Penetration Testing,\" in Proc. 22nd Int. Conf. Advanced Communication Technology (ICACT), 2020, pp. 256-261, doi: 10.23919/ICACT48636.2020.9061401.",
    "[14] A. Chowdhary, D. Huang, J. S. Mahendran, D. Romo, Y. Deng, and A. Sabur, \"Autonomous Security Analysis and Penetration Testing,\" in Proc. 16th Int. Conf. Mobility, Sensing and Networking (MSN), 2020, pp. 508-515, doi: 10.1109/MSN50589.2020.00086.",
    "[15] S. Jaganathan, M. K. Latha, and K. Dharanikota, \"Design and analysis of reinforcement learning models for automated penetration testing,\" IAES Int. J. Artif. Intell., vol. 14, no. 5, pp. 4061-4073, 2025, doi: 10.11591/ijai.v14.i5.pp4061-4073.",
]


def insert_paragraph_before(reference_paragraph, text, style_name):
    new_p = OxmlElement("w:p")
    reference_paragraph._p.addprevious(new_p)
    paragraph = Paragraph(new_p, reference_paragraph._parent)
    paragraph.style = style_name
    paragraph.text = text
    return paragraph


def add_ai_disclosure(doc):
    if any(paragraph.text.strip().upper() == "ACKNOWLEDGMENT" for paragraph in doc.paragraphs):
        return

    references_heading = None
    for paragraph in doc.paragraphs:
        if paragraph.text.strip().upper() == "REFERENCES":
            references_heading = paragraph
            break
    if references_heading is None:
        raise ValueError("References heading not found")

    insert_paragraph_before(references_heading, "ACKNOWLEDGMENT", "Heading 1")
    insert_paragraph_before(
        references_heading,
        "The authors used AI-assisted language editing during manuscript revision. All technical claims, citations, results, and final wording were reviewed and verified by the authors.",
        "First Paragraph",
    )


def update_reference_block(doc):
    references_heading_index = None
    for index, paragraph in enumerate(doc.paragraphs):
        if paragraph.text.strip().upper() == "REFERENCES":
            references_heading_index = index
            break
    if references_heading_index is None or references_heading_index + 1 >= len(doc.paragraphs):
        raise ValueError("Reference paragraph not found")
    doc.paragraphs[references_heading_index + 1].text = " ".join(REFERENCE_ENTRIES)


def prepare_source_docx():
    doc = Document(str(SOURCE_PATH))
    add_ai_disclosure(doc)
    update_reference_block(doc)
    doc.save(str(INTERMEDIATE_PATH))


def main():
    prepare_source_docx()
    try:
        output = generate(
            source_path=str(INTERMEDIATE_PATH),
            output_path=str(OUTPUT_PATH),
            author_details_path=str(AUTHOR_DETAILS_PATH),
        )
    except PermissionError:
        output = generate(
            source_path=str(INTERMEDIATE_PATH),
            output_path=str(FALLBACK_OUTPUT_PATH),
            author_details_path=str(AUTHOR_DETAILS_PATH),
        )
    print(output)


if __name__ == "__main__":
    main()
