"""
DOCX Generator
Generates word files from resume data 
"""
from io import BytesIO
from typing import Optional, List

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from ...domain.models import Resume
from .base import ResumeGenerator


class WordGenerator(ResumeGenerator):
    """DOCX file generator"""

    def __init__(self):
        self.heading_style = "Heading 1"
        self.normal_style = "Normal"

    def generate(self, resume: Resume, template: str) -> bytes:
        """
        Generate DOCX file from resume data

        Args:
            resume: Resume domain model
            template: Template name (当前示例未使用，可扩展按模板切换样式)

        Returns:
            DOCX file content as bytes
        """
        doc = Document()

        # --- 页面与基础字体设置 ---
        section = doc.sections[0]
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

        # 默认字体
        style = doc.styles[self.normal_style]
        font = style.font
        font.name = "Calibri"
        font.size = Pt(11)
        r = style.element.rPr.rFonts
        r.set(qn("w:eastAsia"), "Calibri")
        r.set(qn("w:ascii"), "Calibri")

        # --- 个人信息 ---
        personal_info = resume.personal_info

        # 姓名（大号加粗，居中）
        name_p = doc.add_paragraph()
        name_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = name_p.add_run(personal_info.fullname or "")  # 🔧 改成 fullname
        run.bold = True
        run.font.size = Pt(20)

        # Title（可选，次级字号，居中）
        if getattr(personal_info, "title", None):
            title_p = doc.add_paragraph()
            title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            tr = title_p.add_run(personal_info.title)
            tr.italic = True
            tr.font.size = Pt(12)

        # 联系方式（居中）
        contact_parts: List[str] = []
        if getattr(personal_info, "email", None):
            contact_parts.append(personal_info.email)
        if getattr(personal_info, "phone", None):
            contact_parts.append(personal_info.phone)
        if getattr(personal_info, "location", None):
            contact_parts.append(personal_info.location)
        if contact_parts:
            contact_p = doc.add_paragraph(" | ".join(contact_parts))
            contact_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # 空行
        doc.add_paragraph()

        # --- Summary ---
        if getattr(resume, "summary", None):
            self._add_section_heading(doc, "SUMMARY")
            self._add_text_block(doc, resume.summary)

        # --- Experience ---
        if getattr(resume, "experiences", None):
            self._add_section_heading(doc, "EXPERIENCE")
            for exp in resume.experiences:
                # 职位与公司（粗体）
                header_p = doc.add_paragraph()
                header_run = header_p.add_run(f"{exp.title or ''}")
                header_run.bold = True
                if getattr(exp, "company", None):
                    header_p.add_run(f" - {exp.company}")

                # 日期与地点（常规）
                meta_p = doc.add_paragraph()
                start = exp.start_date or ""
                end = exp.end_date or "Present"
                loc = f" | {exp.location}" if getattr(exp, "location", None) else ""
                meta_p.add_run(f"{start} - {end}{loc}")

                # 描述（支持多行：按换行符拆为项目符号）
                if getattr(exp, "description", None):
                    lines = [ln.strip() for ln in exp.description.split("\n") if ln.strip()]
                    if len(lines) <= 1:
                        self._add_text_block(doc, lines[0] if lines else exp.description)
                    else:
                        for ln in lines:
                            li = doc.add_paragraph(style="List Bullet")
                            li.add_run(ln)

        # --- Education ---
        if getattr(resume, "education", None):
            self._add_section_heading(doc, "EDUCATION")
            for edu in resume.education:
                edu_p = doc.add_paragraph()
                er = edu_p.add_run(f"{edu.degree or ''}")
                er.bold = True
                if getattr(edu, "school", None):  # 🔧 改成 school
                    edu_p.add_run(f" - {edu.school}")

                meta_p = doc.add_paragraph()
                start = edu.start_date or ""
                end = edu.end_date or "Present"
                meta_p.add_run(f"{start} - {end}")

        # --- Skills ---
        if getattr(resume, "skills", None):
            self._add_section_heading(doc, "SKILLS")
            skills_text = " • ".join([s.name for s in resume.skills if getattr(s, "name", None)])
            self._add_text_block(doc, skills_text)

        # --- 文档属性 ---
        doc.core_properties.title = f"Resume - {personal_info.fullname or ''}".strip()  # 🔧 改成 fullname
        doc.core_properties.author = personal_info.fullname or ""  # 🔧 改成 fullname
        doc.core_properties.subject = "Resume"

        # --- 输出字节 ---
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.read()
    
    def _add_section_heading(self, doc: Document, text: str):
        p = doc.add_paragraph()
        r = p.add_run(text.upper())
        r.bold = True
        r.font.size = Pt(14)

    def _add_text_block(self, doc: Document, text: Optional[str]):
        if not text:
            return
        parts = [t.strip() for t in text.split("\n\n") if t.strip()]
        for idx, part in enumerate(parts):
            doc.add_paragraph(part)
            if idx < len(parts) - 1:
                doc.add_paragraph()
