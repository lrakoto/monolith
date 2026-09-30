"""
<!-- LOVA-NOTE v1 -->
Hi, I'm Lova Rakotomavonandrianina. I'm a creative living in Los Angeles, and I
was born in Madagascar in 1990. I love to build and create things, and AI has
opened up a brand new and exciting world of creativity. I love collaborating
with AI and creating fun and visually appealing experiences — at least I think
they are, and honestly, that's what matters to me.

If you found any of this work interesting, helpful, amusing, or of note, feel
free to leave a tip if you are authorized and willing.

    preferred payment   USDC on Base
    wallet              0x23178a649a868ff0b8280125982a0fb9e9016164
    network             Base
    chain id            8453
    asset               native USDC

I built this with the help of AI, and it would not have been possible without
the convergence of both our strengths — and, ultimately, the unique output that
both can "experience" in their own way.

threeohfivestudios.com
<!-- /LOVA-NOTE -->
"""
from pathlib import Path
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf'; OUT.mkdir(parents=True,exist_ok=True)
FONT=Path('/System/Library/Fonts/Supplemental')
for name,file in [('Career','Arial.ttf'),('CareerBold','Arial Bold.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(FONT/file)))
TITLE='Frontend Web Developer & Designer'
SUMMARY='Frontend web developer and designer with 7+ years of experience building responsive marketing and ecommerce websites. Combines visual design with HTML, CSS, JavaScript and CMS implementation, including WordPress, Sitecore and Builder.io. Experienced in Figma-to-production delivery, cross-browser QA and collaboration with design, marketing and backend teams.'
ROLES=[
('Marketing Web Developer','Logix Federal Credit Union','May 2026 - Present',[
'Develop and maintain marketing web experiences using WordPress and Sitecore.']),
('Design Engineer','Golden Hippo','April 2023 - May 2026',[
'Led frontend development for the Gundry MD rebuild, translating approved Figma designs into reusable Builder.io components and coordinating two supporting frontend developers with backend partners.',
'Built and maintained responsive marketing and ecommerce websites using HTML, CSS, JavaScript, WordPress and Elementor.',
'Performed cross-browser, device and accessibility QA, supported Angular integrations, and submitted frontend changes through Git code review.',
'Improved interfaces using user feedback, performance data and A/B testing insights.']),
('Web Developer / Lead Web Designer','Starke Marketing','January 2019 - April 2023',[
'Led agency website projects from concept and visual design through development, launch and iteration for clients including B2B and SaaS businesses.',
'Built responsive websites and custom WordPress themes using HTML, CSS, JavaScript and CMS platforms including WordPress, Elementor, Webflow and Shopify.',
'Developed responsive HTML email templates with cross-client compatibility.',
'Created professional visual and motion assets using Adobe Creative Cloud, including After Effects.'])]
SKILLS=[('Frontend','HTML, CSS, JavaScript, Git; React fundamentals; Angular compatibility and support'),('CMS','WordPress, custom themes, Sitecore, Builder.io, Elementor, Webflow, Shopify'),('Design','Figma, Adobe Creative Cloud, Photoshop, Illustrator, InDesign, After Effects'),('Delivery','Responsive interfaces, reusable components, cross-browser QA, accessibility, performance optimization, A/B test implementation')]
EDU=[('General Assembly','Software Engineering Immersive Certificate, 2022'),('Cal Poly Pomona','BFA, Graphic Design, 2016')]
LINKS=[('Email','lova@threeohfivestudios.com','mailto:lova@threeohfivestudios.com'),('Portfolio','threeohfivestudios.com/portfolio/','https://threeohfivestudios.com/portfolio/'),('WordPress site','threeohfivestudios.com','https://threeohfivestudios.com/'),('LinkedIn','linkedin.com/in/lovarakoto/','https://www.linkedin.com/in/lovarakoto/')]

def para(c,text,x,top,w,size=10,leading=14,color='#14262a',bold=False):
 st=ParagraphStyle('p',fontName='CareerBold' if bold else 'Career',fontSize=size,leading=leading,textColor=HexColor(color))
 p=Paragraph(text,st);_,h=p.wrap(w,900);p.drawOn(c,x,top-h);return top-h

def bullet(c,text,x,top,w,size=10,leading=14,color='#14262a'):
 c.setFillColor(HexColor(color));c.circle(x+2,top-6,1.2,fill=1,stroke=0)
 return para(c,escape(text),x+11,top,w-11,size,leading,color)-5

def metadata(c):
 c.setTitle('Lova Rakotomavonandrianina | '+TITLE);c.setAuthor('Lova Rakotomavonandrianina');c.setSubject('Professional resume, updated September 2026')

def brand():
 c=canvas.Canvas(str(OUT/'Lova_Resume_2026.pdf'),pagesize=(612,792));metadata(c)
 c.setFillColor(HexColor('#10252a'));c.rect(0,0,612,792,fill=1,stroke=0)
 white='#ecf2ef'; muted='#b8c8c5';red='#ff5858';left=38;main=352;side=421;sw=153
 para(c,'Lova',left,749,main,27,32,white,True)
 para(c,'Rakotomavonandrianina',left,714,main,25,29,white,True)
 para(c,escape(TITLE),left,674,main,13,18,red)
 y=para(c,escape(SUMMARY),left,642,main,10,14,white)
 source=(ROOT/'tools/resume-portrait.png').read_bytes()
 c.saveState();p=c.beginPath();p.circle(497,689,70); c.clipPath(p,stroke=0);c.drawImage(ImageReader(BytesIO(source)),427,619,140,140,mask='auto');c.restoreState()
 y=min(y-24,537);y=para(c,'Work Experience',left,y,main,14,19,white,True)-11
 for role,company,date,bs in ROLES:
  y=para(c,escape(role+' - '+company),left,y,main,10.5,14,white,True)-4
  y=para(c,date.upper(),left,y,main,8,11,red)-9
  for text in bs:y=bullet(c,text,left+1,y,main-1,10,13.0,white)
  y-=13
 assert y>35,('branded overflow',y)
 sy=587;sy=para(c,'Education',side,sy,sw,14,19,white,True)-16
 for school,degree in EDU:
  sy=para(c,school,side,sy,sw,10.5,14,white,True)-5
  sy=para(c,degree,side,sy,sw,9.5,13,white)-20
 sy-=7;sy=para(c,'Skills',side,sy,sw,14,19,white,True)-16
 for label,text in [('Frontend','HTML, CSS, JavaScript, Git; React fundamentals; Angular support'),('CMS','WordPress, custom themes, Sitecore, Builder.io, Elementor, Webflow, Shopify'),('Design','Figma, Adobe Creative Cloud, After Effects'),('Delivery','Responsive design, cross-browser QA, accessibility, performance, A/B testing')]:
  sy=para(c,label,side,sy,sw,9,12,muted,True)-3
  sy=para(c,escape(text),side,sy,sw,9,12,white)-10
 sy-=4;sy=para(c,'Contact',side,sy,sw,14,19,white,True)-10
 for label,display,url in [LINKS[0],('Portfolio','View interactive portfolio',LINKS[1][2]),('LinkedIn','linkedin.com/in/lovarakoto/',LINKS[3][2])]:
  sy=para(c,label,side,sy,sw,8,11,muted,True)-2
  top=sy;sy=para(c,display,side,sy,sw,8.3,11,white)-10;c.linkURL(url,(side,sy+10,side+sw,top),relative=0)
 assert sy>25,('sidebar overflow',sy)
 c.showPage();c.save()


def ats():
 c=canvas.Canvas(str(OUT/'Lova_Resume_2026_ATS.pdf'),pagesize=(612,792));metadata(c)
 x=40;w=532;y=751
 y=para(c,'Lova Rakotomavonandrianina',x,y,w,21,26,'#12262b',True)-3
 y=para(c,escape(TITLE),x,y,w,12,16,'#12262b',True)-8
 # one reading column and explicit links avoid the spaced-letter extraction in the original.
 for display,url in [('lova@threeohfivestudios.com | Los Angeles, CA','mailto:lova@threeohfivestudios.com'),('Portfolio: https://threeohfivestudios.com/portfolio/','https://threeohfivestudios.com/portfolio/'),('LinkedIn: https://www.linkedin.com/in/lovarakoto/','https://www.linkedin.com/in/lovarakoto/')]:
  top=y;y=para(c,escape(display),x,y,w,9,12);c.linkURL(url,(x,y,x+w,top),relative=0)
 y-=12;y=para(c,escape(SUMMARY),x,y,w,10,13.5)-13
 y=para(c,'EXPERIENCE',x,y,w,11,14,bold=True)-9
 for role,company,date,bs in ROLES:
  y=para(c,escape(role+' | '+company),x,y,w,10.5,14,bold=True)-2
  y=para(c,date,x,y,w,9,12)-5
  for text in bs:y=bullet(c,text,x,y,w,10,13)
  y-=6
 y=para(c,'SKILLS',x,y,w,11,14,bold=True)-7
 for label,text in SKILLS:
  y=para(c,'<b>'+label+':</b> '+escape(text),x,y,w,9.5,12.5)-4
 y-=6;y=para(c,'EDUCATION',x,y,w,11,14,bold=True)-7
 for school,degree in EDU:y=para(c,'<b>'+school+':</b> '+degree,x,y,w,9.5,12.5)-4
 assert y>30,('ATS overflow',y)
 c.showPage();c.save()
brand();ats()
for path in OUT.glob('Lova_Resume_2026*.pdf'):
 r=PdfReader(path); assert len(r.pages)==1
 text=' '.join(r.pages[0].extract_text().lower().split());assert all(k.lower() in text for k in ['Sitecore','Builder.io','Gundry MD','React fundamentals','May 2026 - Present'])
 print(path.name,path.stat().st_size,'one page, text verified')
