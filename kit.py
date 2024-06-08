import pdfkit
import wikipedia


page = wikipedia.page(title="DragonForce", auto_suggest=False)
html_content = f"<h1>{page.title}</h1>\n{page.content}"
pdfkit.from_string(html_content, f"{page.title}.pdf")
