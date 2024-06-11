import logging
import requests
import asyncio
import json
from datetime import datetime as rolex
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import os
from dotenv import load_dotenv


load_dotenv()
tokenKey = os.getenv('TOKEN_KEY')

queueURL = "http://localhost:8000"
dbURL = "http://localhost:8003"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = "I am KayuMerantiBot and I am capable of retrieving information from documents. My module status is:\n" + "\nBahasa Indonesia PrivateGPT: *OFFLINE*\n" + "English Haystack: *ONLINE*\n" + "\nType **/help** for instructions on how to use me!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='Markdown')


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bookList = "- *Emotional Intelligence* by Daniel Goleman\n- *Influence: The Psychology of Persuasion* by Robert B. Cialdini\n- *Nudge: Improving Decisions About Health, Wealth, and Happiness* by Richard H. Thaler and Cass R. Sunstein\n- *Predictably Irrational* by Dan Ariely\n- *The Social Animal* by Elliot Aronson\n- *Thinking, Fast and Slow* by Daniel Kahneman"
    message = "Hi, I am KayuMerantiBot! To ask a question, please type /prompt followed by your question. \n" + "\nExample: /prompt What changes do I need in my personality to make friends easily?\n" + "\nMy current vector database contains information on **human psychology**, I would be happy to help with any questions you have about the topic. Feel free to ask!\n" + "\nPlease note that I am a QA chatbot, meaning my answers will be based solely on your current question and will not take previous messages into account." + "\n\n List of documents in my database: \n" + bookList
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='Markdown')

async def prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    prompt = ' '.join(context.args)
    
    data = {
        "prompt": prompt,
        "chatID": update.effective_chat.id
    }

    dbInsertUrl = dbURL + "/insert_chat"
    response = requests.post(dbInsertUrl, json=data)

    if response.status_code == 200:
        startTime = rolex.now()
        notificationMessage = "*Processing prompt:* \n" + prompt + "\n\n" + "*Time start: " + startTime.strftime("%Y-%m-%d %H:%M:%S") + " (GMT +7)*"
        # Process the argument as needed
        # For demonstration, just echo back the argument
        await context.bot.send_message(chat_id=update.effective_chat.id, text=notificationMessage, parse_mode='Markdown')
        
        print("Data inserted successfully")
        insertData = response.json()
        responseId = insertData.get("id")
        print("Processing entry ID: ", responseId)
        
        while True:
            
            url = dbURL + "/get_flagA"
            headers = {"Content-Type": "application/json"}
            data = {"id": responseId}

            response = requests.get(url, headers=headers, json=data)
            response_data = response.json()
            flagA = response_data.get("flagA")
            
            if flagA == 1:
                break  
            
            
        
        url = dbURL + "/get_result"
        headers = {"Content-Type": "application/json"}
        data = {"id": responseId}
        response = requests.get(url, headers=headers, json=data)
        response_data = response.json()
        
        response = response_data.get("response")
        source1 = response_data.get("source1")
        source2 = response_data.get("source2")
        
        sourceList = []
        sourceList.append(source1)
        sourceList.append(source2)
        
        
        
        await send_results_to_user(context, update.effective_chat.id, prompt, response, sourceList, startTime, responseId)
        
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error processing the request!")

async def send_results_to_user(context, chat_id, argument, gptResult, gptSource, startTime, entryID):
    print(type(argument))
    print(type(gptResult))
    formattedResponse = "*Replying to:*\n" + argument + "\n" + "*Response:*\n" + gptResult + "\n"
    formattedSource = "*Source:*\n" + gptSource[0] + "\n" + gptSource[1] + "\n"
    endTime = rolex.now()
    
    stopTime = "*Time stop: " + endTime.strftime("%Y-%m-%d %H:%M:%S") + " (GMT +7)*"
    
    diffTime = endTime - startTime
    
    # Assuming diffTime is a timedelta object
    hours, remainder = divmod(diffTime.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format the time taken
    timeTaken = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
    timeTakenMessage = "*Time taken: " + timeTaken + " (HH:MM:SS)*"

    responseMessage = formattedResponse + "\n" + stopTime + "\n" + timeTakenMessage
    
    updateData = {
                    "id": entryID,
                    "flagB": 1,
                    "duration": timeTaken
    }
            
    requests.post(dbURL + "/update_flagb", json=updateData)
    
    await context.bot.send_message(chat_id=chat_id, text=responseMessage, parse_mode='Markdown')



if __name__ == '__main__':
    application = ApplicationBuilder().token(tokenKey).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler)
    
    prompt_handler = CommandHandler('prompt', prompt)
    application.add_handler(prompt_handler)

    
    application.run_polling()