import wikipedia

title = "Nissan Skyline GT-R"

page = wikipedia.page(title=title, auto_suggest=False)

print(page.content)