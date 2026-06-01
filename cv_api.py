import io
from fpdf import FPDF

def generate_html(data):
    name = data.get('name', 'Name')
    contact = data.get('contact', {})
    phone = contact.get('phone', '')
    email = contact.get('email', '')
    youtube = contact.get('youtube', '')
    linkedin = contact.get('linkedin', '')
    github = contact.get('github', '')
    location = contact.get('location', '')

    contact_parts = []
    if location:
        contact_parts.append(f'<span>{location}</span>')
    if phone:
        contact_parts.append(f'<span>{phone}</span>')
    if email:
        contact_parts.append(f'<span>{email}</span>')
    if linkedin:
        clean_li = linkedin.replace('https://', '').replace('http://', '').replace('www.', '')
        contact_parts.append(f'<span>{clean_li}</span>')
    elif youtube:
        contact_parts.append(f'<span>{youtube}</span>')
    if github:
        clean_gh = github.replace('https://', '').replace('http://', '').replace('www.', '')
        contact_parts.append(f'<span>{clean_gh}</span>')

    contact_info_str = '\n<span class="separator">|</span>\n'.join(contact_parts)

    exp_html = []
    for exp in data.get('experience', []):
        bullets = "".join([f"<li>{b}</li>" for b in exp.get('bullets', [])])
        exp_html.append(f"""
        <div class="subheading-container">
            <div class="subheading-row">
                <span class="subheading-title">{exp.get('company', '')}</span>
                <span class="subheading-right">{exp.get('date', '')}</span>
            </div>
            <div class="subheading-row">
                <span class="subheading-subtitle">{exp.get('title', '')}</span>
                <span class="subheading-right">{exp.get('location', '')}</span>
            </div>
            <ul>{bullets}</ul>
        </div>
        """)
    experience_section = "".join(exp_html)

    proj_html = []
    for proj in data.get('projects', []):
        bullets = "".join([f"<li>{b}</li>" for b in proj.get('bullets', [])])
        proj_html.append(f"""
        <div class="subheading-container">
            <div class="subheading-row">
                <span class="subheading-title">{proj.get('title', '')}</span>
                <span class="subheading-right">{proj.get('date', '')}</span>
            </div>
            <ul>{bullets}</ul>
        </div>
        """)
    projects_section = "".join(proj_html)

    edu_html = []
    for edu in data.get('education', []):
        bullets = "".join([f"<li>{b}</li>" for b in edu.get('bullets', [])])
        edu_html.append(f"""
        <div class="subheading-container">
            <div class="subheading-row">
                <span class="subheading-title">{edu.get('school', '')}</span>
                <span class="subheading-right">{edu.get('location', '')}</span>
            </div>
            <div class="subheading-row">
                <span class="subheading-subtitle">{edu.get('degree', '')}</span>
                <span class="subheading-right">{edu.get('date', '')}</span>
            </div>
            <ul>{bullets}</ul>
        </div>
        """)
    education_section = "".join(edu_html)

    skills_html = []
    for skill_cat, skills_list in data.get('skills', {}).items():
        if isinstance(skills_list, list):
            skills_str = ", ".join(skills_list)
        else:
            skills_str = str(skills_list)
        skills_html.append(f"""
        <div class="skills-line">
            <strong>{skill_cat}:</strong> {skills_str}
        </div>
        """)
    skills_section = "".join(skills_html)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - CV</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <style>
        :root {{
            --bg-color: #f3f4f6;
            --paper-bg: #ffffff;
            --text-main: #141414;
            --text-muted: #4d4d4d;
            --border-color: #d3d3d3;
            --font-family: 'Crimson Pro', Georgia, 'Times New Roman', serif;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: var(--font-family);
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.35;
            padding: 2rem 1rem;
            font-size: 11.5pt;
        }}

        .page-wrapper {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
        }}

        .letter-page {{
            width: 8.5in;
            min-height: 11in;
            background-color: var(--paper-bg);
            padding: 0.5in 0.5in 0.75in 0.5in;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
            position: relative;
        }}

        .controls {{
            text-align: center;
            margin-bottom: 10px;
        }}

        .btn-download {{
            background-color: #1e293b;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 0.9rem;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-weight: 600;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .btn-download:hover {{
            background-color: #0f172a;
        }}

        header {{
            text-align: center;
            margin-bottom: 18px;
        }}

        header h1 {{
            font-size: 24pt;
            font-weight: 700;
            margin-bottom: 6px;
            letter-spacing: -0.01em;
        }}

        .contact-info {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 8px;
            color: var(--text-main);
            font-size: 10.5pt;
        }}

        .contact-info span {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .separator {{
            color: var(--border-color);
            margin: 0 4px;
        }}

        section {{
            margin-bottom: 14px;
        }}

        section h2.section-title {{
            font-size: 13pt;
            font-weight: 700;
            text-transform: uppercase;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 2px;
            margin-top: 10px;
            margin-bottom: 6px;
            letter-spacing: 0.02em;
        }}

        .subheading-container {{
            margin-bottom: 8px;
        }}

        .subheading-row {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
        }}

        .subheading-title {{
            font-weight: 700;
            font-size: 11.5pt;
        }}

        .subheading-subtitle {{
            font-style: italic;
            font-size: 11pt;
        }}

        .subheading-right {{
            font-size: 10.5pt;
            color: var(--text-muted);
            text-align: right;
        }}

        ul {{
            list-style-type: none;
            padding-left: 0;
            margin-top: 2px;
        }}

        li {{
            font-size: 10.5pt;
            margin-bottom: 2px;
            position: relative;
            padding-left: 14px;
            text-align: justify;
        }}

        li::before {{
            content: "\\2022";
            position: absolute;
            left: 2px;
            color: var(--text-main);
            font-size: 9pt;
            top: -1px;
        }}

        .skills-list {{
            margin-top: 4px;
        }}

        .skills-line {{
            font-size: 10.5pt;
            margin-bottom: 4px;
            line-height: 1.3;
        }}

        .skills-line strong {{
            font-weight: 700;
        }}

        @media print {{
            body {{
                background: white;
                margin: 0;
                padding: 0;
            }}
            .page-wrapper {{
                display: block;
            }}
            .letter-page {{
                width: 100%;
                min-height: auto;
                box-shadow: none;
                margin: 0;
                padding: 0;
            }}
            .controls {{
                display: none;
            }}
            .subheading-container {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="controls">
        <button class="btn-download" onclick="downloadPDF()">
            Descargar CV en PDF
        </button>
    </div>

    <div class="page-wrapper" id="resume-content">
        <div class="letter-page">
            <header>
                <h1>{name}</h1>
                <div class="contact-info">
                    {contact_info_str}
                </div>
            </header>

            <section>
                <h2 class="section-title">EDUCATION</h2>
                {education_section}
            </section>

            <section>
                <h2 class="section-title">EXPERIENCE</h2>
                {experience_section}
            </section>

            <section>
                <h2 class="section-title">PROJECTS</h2>
                {projects_section}
            </section>

            <section>
                <h2 class="section-title">SKILLS</h2>
                <div class="skills-list">
                    {skills_section}
                </div>
            </section>
        </div>
    </div>

    <script>
        function downloadPDF() {{
            const element = document.getElementById('resume-content');
            const opt = {{
                margin:       0,
                filename:     '{name.replace(' ', '_')}_CV.pdf',
                image:        {{ type: 'jpeg', quality: 0.98 }},
                html2canvas:  {{ scale: 2.2, useCORS: true }},
                jsPDF:        {{ unit: 'in', format: 'letter', orientation: 'portrait' }}
            }};
            html2pdf().set(opt).from(element).save();
        }}
    </script>
</body>
</html>"""
    return html


class ResumePDF(FPDF):
    def __init__(self):
        super().__init__(format='letter')
        self.set_auto_page_break(auto=True, margin=54)
        self.add_page()
        self.set_margins(36, 36, 36)

    def header_section(self, name, contact_info):
        self.set_font('Helvetica', 'B', 24)
        self.cell(0, 12, name, align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(2)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 5, contact_info, align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(20, 20, 20)
        self.cell(0, 8, title.upper(), new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def subheading(self, left_title, right_text, left_subtitle='', right_subtitle=''):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(20, 20, 20)
        w = self.w - self.l_margin - self.r_margin
        self.cell(w * 0.7, 5, left_title)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(w * 0.3, 5, right_text, align='R', new_x='LMARGIN', new_y='NEXT')

        if left_subtitle or right_subtitle:
            self.set_font('Helvetica', 'I', 10)
            self.set_text_color(60, 60, 60)
            self.cell(w * 0.7, 5, left_subtitle)
            self.set_font('Helvetica', '', 10)
            self.set_text_color(100, 100, 100)
            self.cell(w * 0.3, 5, right_subtitle, align='R', new_x='LMARGIN', new_y='NEXT')

        self.set_text_color(0, 0, 0)
        self.ln(1)

    def bullet_list(self, items):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(30, 30, 30)
        for item in items:
            self.set_x(self.l_margin + 4)
            self.cell(4, 4, '-')
            w = self.w - self.l_margin - self.r_margin - 8
            self.multi_cell(w, 4, item, new_x='LMARGIN', new_y='NEXT')
            self.ln(1)
        self.ln(2)

    def skills_line(self, category, skills):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(20, 20, 20)
        self.cell(self.get_string_width(f'{category}: ') + 2, 5, f'{category}: ')
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50, 50, 50)
        w = self.w - self.l_margin - self.r_margin - self.get_x() + self.l_margin
        self.multi_cell(w, 5, skills, new_x='LMARGIN', new_y='NEXT')
        self.ln(1)


def generate_pdf(data):
    pdf = ResumePDF()

    name = data.get('name', 'Name')
    contact = data.get('contact', {})
    contact_parts = []
    if contact.get('location'):
        contact_parts.append(contact['location'])
    if contact.get('phone'):
        contact_parts.append(contact['phone'])
    if contact.get('email'):
        contact_parts.append(contact['email'])
    if contact.get('linkedin'):
        clean_li = contact['linkedin'].replace('https://', '').replace('http://', '').replace('www.', '')
        contact_parts.append(clean_li)
    elif contact.get('youtube'):
        contact_parts.append(contact['youtube'])
    if contact.get('github'):
        clean_gh = contact['github'].replace('https://', '').replace('http://', '').replace('www.', '')
        contact_parts.append(clean_gh)
    contact_info = ' | '.join(contact_parts)

    pdf.header_section(name, contact_info)

    pdf.section_title('EDUCATION')
    for edu in data.get('education', []):
        pdf.subheading(
            edu.get('school', ''),
            edu.get('location', ''),
            edu.get('degree', ''),
            edu.get('date', '')
        )
        pdf.bullet_list(edu.get('bullets', []))

    pdf.section_title('EXPERIENCE')
    for exp in data.get('experience', []):
        pdf.subheading(
            exp.get('company', ''),
            exp.get('date', ''),
            exp.get('title', ''),
            exp.get('location', '')
        )
        pdf.bullet_list(exp.get('bullets', []))

    pdf.section_title('PROJECTS')
    for proj in data.get('projects', []):
        pdf.subheading(
            proj.get('title', ''),
            proj.get('date', '')
        )
        pdf.bullet_list(proj.get('bullets', []))

    pdf.section_title('SKILLS')
    for cat, skills_list in data.get('skills', {}).items():
        if isinstance(skills_list, list):
            skills_str = ', '.join(skills_list)
        else:
            skills_str = str(skills_list)
        pdf.skills_line(cat, skills_str)

    return pdf.output()
