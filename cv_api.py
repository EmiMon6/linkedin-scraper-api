import io
import os
from fpdf import FPDF

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
FONT_REGULAR = os.path.join(FONT_DIR, 'DejaVuSans.ttf')
FONT_BOLD = os.path.join(FONT_DIR, 'DejaVuSans-Bold.ttf')
FONT_ITALIC = os.path.join(FONT_DIR, 'DejaVuSans-Oblique.ttf')
FONT_BOLD_ITALIC = os.path.join(FONT_DIR, 'DejaVuSans-BoldOblique.ttf')

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
        self.add_font('DejaVu', '', FONT_REGULAR)
        self.add_font('DejaVu', 'B', FONT_BOLD)
        self.add_font('DejaVu', 'I', FONT_ITALIC)
        self.add_font('DejaVu', 'BI', FONT_BOLD_ITALIC)
        self.set_auto_page_break(auto=True, margin=50)
        self.add_page()
        self.set_margins(40, 40, 40)
        self.usable_w = self.w - self.l_margin - self.r_margin

    def _safe(self, val, default=''):
        if val is None:
            return default
        s = str(val).strip()
        return s if s else default

    def _auto_size(self, text, max_w, start_size, min_size=8, style=''):
        size = start_size
        while size > min_size:
            self.set_font('DejaVu', style, size)
            if self.get_string_width(text) <= max_w:
                return size
            size -= 0.5
        return min_size

    def _truncate(self, text, max_w, style='', size=10):
        self.set_font('DejaVu', style, size)
        if self.get_string_width(text) <= max_w:
            return text
        ellipsis = '...'
        while len(text) > 1 and self.get_string_width(text + ellipsis) > max_w:
            text = text[:-1].rstrip()
        return text.rstrip(',;. ') + ellipsis

    def header_section(self, name, contact_info):
        name = self._safe(name, 'Your Name')
        max_w = self.usable_w
        size = self._auto_size(name, max_w, 22, min_size=14, style='B')
        self.set_font('DejaVu', 'B', size)
        self.set_text_color(20, 20, 20)
        self.cell(0, size * 0.55, name, align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(1)

        if contact_info:
            parts = [p.strip() for p in contact_info.split('|') if p.strip()]
            ci_size = self._auto_size(' | '.join(parts), max_w, 10, min_size=8)
            self.set_font('DejaVu', '', ci_size)
            self.set_text_color(90, 90, 90)
            self.cell(0, 5, ' | '.join(parts), align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def section_title(self, title):
        title = self._safe(title, '').upper()
        if not title:
            return
        self.set_font('DejaVu', 'B', 12)
        self.set_text_color(25, 25, 25)
        self.cell(0, 7, title, new_x='LMARGIN', new_y='NEXT')
        y = self.get_y()
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.4)
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(2)

    def subheading(self, left_title, right_text='', left_subtitle='', right_subtitle=''):
        left_title = self._safe(left_title)
        right_text = self._safe(right_text)
        left_subtitle = self._safe(left_subtitle)
        right_subtitle = self._safe(right_subtitle)

        if not left_title and not right_text and not left_subtitle and not right_subtitle:
            return

        w = self.usable_w
        date_w = 30
        col_left = w - date_w - 4
        col_right = date_w

        title_size = 11
        if left_title:
            fits = False
            while title_size > 9:
                self.set_font('DejaVu', 'B', title_size)
                if self.get_string_width(left_title) <= col_left:
                    fits = True
                    break
                title_size -= 0.5
            if not fits:
                left_title = self._truncate(left_title, col_left, 'B', title_size)

        if left_title and right_text:
            self.set_font('DejaVu', '', 9.5)
            rt = right_text
            if self.get_string_width(right_text) > col_right:
                rt = self._truncate(right_text, col_right, '', 9.5)

            self.set_font('DejaVu', 'B', title_size)
            self.set_text_color(25, 25, 25)
            self.cell(col_left, 5.2, left_title)
            self.set_font('DejaVu', '', 9.5)
            self.set_text_color(110, 110, 110)
            self.cell(col_right, 5.2, rt, align='R', new_x='LMARGIN', new_y='NEXT')
        elif left_title:
            self.set_font('DejaVu', 'B', title_size)
            self.set_text_color(25, 25, 25)
            self.cell(self.usable_w, 5.2, left_title, new_x='LMARGIN', new_y='NEXT')
        elif right_text:
            self.set_font('DejaVu', '', 9.5)
            self.set_text_color(110, 110, 110)
            self.cell(self.usable_w, 5.2, right_text, align='R', new_x='LMARGIN', new_y='NEXT')

        if left_subtitle or right_subtitle:
            ls_size = 10
            while ls_size > 8:
                self.set_font('DejaVu', 'I', ls_size)
                if not left_subtitle or self.get_string_width(left_subtitle) <= col_left:
                    break
                ls_size -= 0.5
            if left_subtitle and self.get_string_width(left_subtitle) > col_left:
                left_subtitle = self._truncate(left_subtitle, col_left, 'I', ls_size)

            self.set_font('DejaVu', 'I', ls_size)
            self.set_text_color(70, 70, 70)
            self.cell(col_left, 4.8, left_subtitle)
            if right_subtitle:
                self.set_font('DejaVu', '', 9.5)
                self.set_text_color(110, 110, 110)
                self.cell(col_right, 4.8, right_subtitle, align='R', new_x='LMARGIN', new_y='NEXT')
            else:
                self.ln(4.8)

        self.set_text_color(0, 0, 0)
        self.ln(0.8)

    def bullet_list(self, items):
        items = items or []
        clean_items = [self._safe(it) for it in items if self._safe(it)]
        if not clean_items:
            return
        self.set_font('DejaVu', '', 9.5)
        self.set_text_color(40, 40, 40)
        bullet_w = 5
        text_w = self.usable_w - bullet_w - 2
        for item in clean_items:
            self.set_x(self.l_margin + bullet_w)
            self.cell(bullet_w, 4.2, '-')
            self.set_x(self.l_margin + bullet_w + 2)
            self.multi_cell(text_w, 4.2, item, new_x='LMARGIN', new_y='NEXT')
        self.ln(1.5)

    def skills_line(self, category, skills):
        category = self._safe(category)
        skills = self._safe(skills)
        if not category and not skills:
            return
        prefix = (category + ': ') if category else ''
        self.set_font('DejaVu', 'B', 9.5)
        self.set_text_color(25, 25, 25)
        prefix_w = self.get_string_width(prefix)
        self.cell(prefix_w, 4.5, prefix)
        self.set_font('DejaVu', '', 9.5)
        self.set_text_color(60, 60, 60)
        remaining = self.usable_w - prefix_w
        self.multi_cell(remaining, 4.5, skills, new_x='LMARGIN', new_y='NEXT')
        self.ln(0.8)


def _clean_url(url):
    if not url:
        return ''
    return str(url).replace('https://', '').replace('http://', '').replace('www.', '').strip('/')


def generate_pdf(data):
    if not isinstance(data, dict):
        data = {}

    pdf = ResumePDF()

    name = str(data.get('name') or 'Your Name').strip() or 'Your Name'
    contact = data.get('contact') or {}
    if not isinstance(contact, dict):
        contact = {}

    contact_parts = []
    loc = str(contact.get('location') or '').strip()
    if loc:
        contact_parts.append(loc)
    phone = str(contact.get('phone') or '').strip()
    if phone:
        contact_parts.append(phone)
    email = str(contact.get('email') or '').strip()
    if email:
        contact_parts.append(email)
    linkedin = _clean_url(contact.get('linkedin'))
    youtube = _clean_url(contact.get('youtube'))
    if linkedin:
        contact_parts.append(linkedin)
    elif youtube:
        contact_parts.append(youtube)
    github = _clean_url(contact.get('github'))
    if github:
        contact_parts.append(github)
    contact_info = ' | '.join(contact_parts)

    pdf.header_section(name, contact_info)

    education = data.get('education') or []
    if isinstance(education, list) and education:
        pdf.section_title('EDUCATION')
        for edu in education:
            if not isinstance(edu, dict):
                continue
            pdf.subheading(
                edu.get('school'),
                edu.get('location'),
                edu.get('degree'),
                edu.get('date')
            )
            pdf.bullet_list(edu.get('bullets') or [])

    experience = data.get('experience') or []
    if isinstance(experience, list) and experience:
        pdf.section_title('EXPERIENCE')
        for exp in experience:
            if not isinstance(exp, dict):
                continue
            pdf.subheading(
                exp.get('company'),
                exp.get('date'),
                exp.get('title'),
                exp.get('location')
            )
            pdf.bullet_list(exp.get('bullets') or [])

    projects = data.get('projects') or []
    if isinstance(projects, list) and projects:
        pdf.section_title('PROJECTS')
        for proj in projects:
            if not isinstance(proj, dict):
                continue
            pdf.subheading(
                proj.get('title'),
                proj.get('date'),
                '',
                ''
            )
            pdf.bullet_list(proj.get('bullets') or [])

    skills = data.get('skills') or {}
    if isinstance(skills, dict) and skills:
        pdf.section_title('SKILLS')
        for cat, skills_list in skills.items():
            if isinstance(skills_list, list):
                skills_str = ', '.join(str(s).strip() for s in skills_list if str(s).strip())
            else:
                skills_str = str(skills_list).strip()
            if skills_str:
                pdf.skills_line(cat, skills_str)

    return pdf.output()
