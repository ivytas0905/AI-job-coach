"""
PDF Generator
Generates PDF files from resume data using reportlab
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO
from ...domain.models import Resume
from .base import ResumeGenerator


class PDFGenerator(ResumeGenerator):
    """PDF file generator"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
    
    def generate(self, resume: Resume, template: str) -> bytes:
        """
        Generate PDF file from resume data
        
        Args:
            resume: Resume domain model
            template: Template name
            
        Returns:
            PDF file content as bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Add contact information
        personal_info = resume.personal_info
        story.append(Paragraph(
            f"<b><font size=20>{personal_info.fullname}</font></b>",  # 🔧 改成 fullname
            self.styles['Title']
        ))
        
        if personal_info.title:
            story.append(Paragraph(
                f"<font size=12>{personal_info.title}</font>",
                self.styles['Normal']
            ))
        
        story.append(Paragraph(
            f"{personal_info.email} | {personal_info.phone} | {personal_info.location or ''}",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.3 * inch))
        
        # Add summary section
        if resume.summary:
            story.append(Paragraph("<b>SUMMARY</b>", self.styles['Heading2']))
            story.append(Paragraph(resume.summary, self.styles['Normal']))
            story.append(Spacer(1, 0.2 * inch))
        
        # Add experience section
        if resume.experiences:
            story.append(Paragraph("<b>EXPERIENCE</b>", self.styles['Heading2']))
            for exp in resume.experiences:
                story.append(Paragraph(
                    f"<b>{exp.title}</b> - {exp.company}",
                    self.styles['Normal']
                ))
                story.append(Paragraph(
                    f"{exp.start_date} - {exp.end_date or 'Present'} | {exp.location or ''}",
                    self.styles['Normal']
                ))
                if exp.description:
                    story.append(Paragraph(exp.description, self.styles['Normal']))
                story.append(Spacer(1, 0.1 * inch))
            story.append(Spacer(1, 0.2 * inch))
        
        # Add education section
        if resume.education:
            story.append(Paragraph("<b>EDUCATION</b>", self.styles['Heading2']))
            for edu in resume.education:
                story.append(Paragraph(
                    f"<b>{edu.degree}</b> - {edu.school}",  # 🔧 改成 school
                    self.styles['Normal']
                ))
                story.append(Paragraph(
                    f"{edu.start_date} - {edu.end_date or 'Present'}",
                    self.styles['Normal']
                ))
                story.append(Spacer(1, 0.1 * inch))
            story.append(Spacer(1, 0.2 * inch))
        
        # Add skills section
        if resume.skills:
            story.append(Paragraph("<b>SKILLS</b>", self.styles['Heading2']))
            skills_text = ' • '.join([skill.name for skill in resume.skills])
            story.append(Paragraph(skills_text, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
