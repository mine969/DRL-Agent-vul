# IEEE Conference Format Analysis

Files reviewed:
- `research/conference-template-a4 (4).docx`
- `research/Research_Paper_Draft.docx`

## 1. What the IEEE template is using

Observed from `conference-template-a4 (4).docx`:

- Paper size: A4 (`8.27 x 11.69 in`)
- Margins: top `0.75 in`, bottom `1.00 in`, left `0.62 in`, right `0.62 in`
- Default font family: `Times New Roman`
- Main title style (`paper title`): `24 pt`, centered
- Abstract style: `9 pt`, justified, bold abstract label
- Author style in the template: centered block; sample author lines render around `9-11 pt`
- Body text style: IEEE body layout with built-in spacing and two-column formatting in the main paper area
- Reference entries: `8 pt`
- Figure labels: template guidance explicitly says `8 point Times New Roman`

Important template guidance seen in the file:

- Do not change margins, column widths, line spacing, or text fonts
- Use the A4 template for A4 submission
- Do not use symbols, special characters, footnotes, or math in the paper title or abstract

## 2. What the current draft is using

Observed from `Research_Paper_Draft.docx`:

- Paper size: US Letter (`8.50 x 11.00 in`)
- Margins: `1.00 in` on all sides
- Layout: single column
- Paragraph styles are not aligned to IEEE template usage
- Title is currently styled like a section heading, not the IEEE title block
- Abstract is split into a heading line plus body text, not IEEE `Abstract-...` format
- References are stored in one long paragraph instead of separate IEEE reference entries
- The draft contains:
  - 1 title
  - 1 abstract
  - Sections I-VI
  - 2 figures
  - 2 tables
  - 15 references

Current draft style sizes include:

- Title style: `28 pt`
- Heading 1: `20 pt`
- Heading 2: `16 pt`
- Heading 3: `14 pt`
- Abstract style: `10 pt`

These are much larger than the IEEE conference template body and heading conventions.

## 3. Main compliance gaps

To make the draft match the IEEE conference template, these are the main issues to fix:

1. Change page setup from US Letter to A4.
2. Replace 1-inch margins with IEEE template margins.
3. Convert the manuscript from single-column to IEEE conference two-column layout for the main body.
4. Apply the template title style instead of a normal heading style.
5. Rewrite the abstract into one IEEE paragraph: `Abstract- ...`
6. Add an IEEE keywords line: `Keywords- ...`
7. Use IEEE heading hierarchy consistently:
   - `I. ...`
   - `A. ...`
   - `1) ...`
8. Convert figure captions and table captions to template caption styles.
9. Split the references into separate numbered IEEE reference paragraphs.
10. Keep all body text in Times New Roman with template-controlled spacing and columns.

## 4. Content structure check

The good news is that your research content is already close to IEEE structure.

It already has:

- Abstract
- Introduction
- Related Work
- Methodology
- Evaluation and Results
- Discussion
- Conclusion
- References

So the biggest task is formatting and front-matter cleanup, not rewriting the whole paper.

## 5. Recommended IEEE front matter for your draft

Suggested title:

`Deep Reinforcement Learning Vulnerability Scanner for Modern Web Applications`

Suggested IEEE abstract format:

`Abstract- Traditional vulnerability testing often relies on manual penetration testing or static heuristic scanners. While these methods are effective to a degree, they are hard to scale and can miss complex, multi-step exploit chains. To solve this, we propose a more dynamic, intelligent approach: modeling the web vulnerability discovery process as a Markov Decision Process (MDP) and training an Extended Double Dueling Deep Q-Network (Extended D3QN) to navigate it. Our configured agent combines Double DQN, a Dueling architecture, Prioritized Experience Replay, and Noisy Networks. By building a custom Gymnasium environment, WebSecurityGym, we train our agent against diverse mock applications containing real-world flaws like SQL Injection (SQLi) and Cross-Site Scripting (XSS). Guided by a phase-based learning strategy that progresses from reconnaissance to active exploitation, the agent learns to chain attacks autonomously, though detection coverage remains uneven across vulnerability classes in evaluation.`

(Superseded — see the abstract in `Bachelor_Simplified_Draft.md`, the current canonical draft, for the up-to-date version.)

Suggested keywords line:

`Keywords- deep reinforcement learning, web vulnerability scanning, autonomous penetration testing, D3QN, cybersecurity, web application security`

## 6. Fastest practical way to convert it in Word

The easiest manual workflow is:

1. Open `conference-template-a4 (4).docx`.
2. Replace the sample title and author block.
3. Paste your abstract into the template abstract paragraph.
4. Add the keywords line under the abstract.
5. Copy each section from `Research_Paper_Draft.docx` into the template body.
6. Reapply template styles instead of keeping the old draft styles.
7. Move figures and tables into the nearest top or bottom of columns.
8. Rebuild the references as separate IEEE entries.

## 7. Submission-focused notes

- Your current draft is not yet submission-ready in IEEE conference format.
- The paper content is usable, but the page layout and style system still need conversion.
- The references section especially needs cleanup before submission.
- The title/abstract/keywords block should be rebuilt directly inside the template, not pasted as plain formatted text.
