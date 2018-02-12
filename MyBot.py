#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import discord
import asyncio
import json
import struct
import time
import giphy_client
import codecs
import urllib.request
from giphy_client.rest import ApiException
from random import randint

data = json.load(open('auth.json')) #import key's

with open("banned.txt", "r") as text_file:
    BannedUsers = text_file.read().split(',')


# create an instance of the API class
api_instance = giphy_client.DefaultApi()
api_key = data["Giphy"] # str | Giphy API Key.
q = 'fail' # str | Search query term or prhase defult if nothing is specifyd.

limit = 10 # int | The maximum number of records to return. (optional) (default to 25)
#offset = 0 # int | An optional results offset. Defaults to 0. (optional) (default to 0)
#rating = 'g' # str | Filters results by specified rating. (optional)
#lang = 'en' # str | Specify default country for regional content; use a 2-letter ISO 639-1 country code. See list of supported languages <a href = \"../language-support\">here</a>. (optional)
#fmt = 'json' # str | Used to indicate the expected response format. Default is Json. (optional) (default to json)

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in')
    print("Im called " + client.user.name)
    print("With the ID " + client.user.id)
    print('------')
    await client.change_presence(game=discord.Game(name='Im ready, !help'))

@client.event
async def on_message(message):
    global BannedUsers     
    args = message.content.split(' ', 1)
    if message.author.id in BannedUsers:
        if message.content.startswith('!updateban'):
            with open("banned.txt", "r") as text_file:
                BannedUsers = text_file.read().split(',')
            
            BannedList = ", ".join(["<@%s>" % (k) for k in BannedUsers])           
            if not BannedList:
                BannedList = "listan är tom"
            
            await client.send_message(message.channel, BannedList)
        elif message.content.startswith('!'):
            await client.send_message(message.channel, '<@' + message.author.id + '> you are banned')
    else:
        if message.content.startswith('!help'):
            await client.send_message(message.channel, 'Try: !settimer, !links, !crypto, !miun, !addcitat, !editcitat, !allcitat !gif or !rgif')

        elif message.content.startswith('!rgif'):       
            try:
                if len(args) < 2:
                    Q = q
                else:
                    Q = args[1]
                api_response = api_instance.gifs_random_get(api_key, tag=Q)
                if not api_response.data.url:
                    Rgifurl = 'Sry i cant find a random gif with the tag: ' + args[1]
                else:
                    Rgifurl = api_response.data.url
            except ApiException as e:
                print("Exception when calling DefaultApi->gifs_random_get: %s\n" % e)

            await client.send_message(message.channel, Rgifurl)

        elif message.content.startswith('!gif'):       
            try:
                if len(args) < 2:
                    Q = q
                else:
                    Q = args[1]
                api_response = api_instance.gifs_search_get(api_key, Q, limit=limit)
                if api_response.pagination.count == 0:
                    Rgifurl = 'Sry i cant find a random gif with the tag: ' + args[1]
                else:
                    randomValue = randint(0, api_response.pagination.count - 1)
                    Rgifurl = api_response.data[randomValue].embed_url
            except ApiException as e:
                print("Exception when calling DefaultApi->gifs_random_get: %s\n" % e)

            await client.send_message(message.channel, Rgifurl)

        elif message.content.startswith('!miun'):
            with open('citat.json', 'r', encoding='utf-8-sig') as f:
                citat = json.load(f)
            randomValue = randint(0, len(citat["general"]) - 1)
            printText = citat["general"][str(randomValue)]
            await client.send_message(message.channel, printText)

        elif message.content.startswith('!addcitat'):
            if len(args) < 2:
                TextToPrint = "Du måste ange ett citat"
            else:
                TextToPrint = "Detta citat har nu lagts till: **" + args[1] + "**"
                with open("citat.json", "r", encoding='utf-8-sig') as jsonFile:
                    DataToAdd = json.load(jsonFile)

                x = len(DataToAdd["general"])
                tmp = DataToAdd["general"]
                DataToAdd["general"][x] = args[1]

                with open('citat.json', 'w', encoding='utf-8-sig') as outfile:  
                    json.dump(DataToAdd, outfile)
            
            await client.send_message(message.channel, TextToPrint)

        elif message.content.startswith('!allcitat'):
            with open("citat.json", "r", encoding='utf-8-sig') as jsonFile:
                DataToAdd = json.load(jsonFile)

            parsedData = json.dumps(DataToAdd, indent=4, sort_keys=True, ensure_ascii=False).encode('utf-8')

            await client.send_message(message.channel,'```json\n' + parsedData.decode('utf-8') + '```')

        elif message.content.startswith('!editcitat'):
            if len(args) < 2:
                TextToChange = "Du måste ange argument: nummret du vill ändra, mellanslag, det du vill ändra till"
            else:
                EditArgs = args[1].split(' ', 1)       
                if (len(EditArgs) < 2):
                    TextToChange = "Du måste ange argument i formatet [int_du_vill_modifiera] [NyText]"
                else:
                    with open("citat.json", "r") as jsonFile:
                        DataToAdd = json.load(jsonFile)

                    x = EditArgs[0]
                    tmp = DataToAdd["general"]
                    DataToAdd["general"][str(x)] = EditArgs[1]

                    with open('citat.json', 'w') as outfile:  
                        json.dump(DataToAdd, outfile)
                        
                    TextToChange = "Nu är " + EditArgs[0] + " ändrat till: " + EditArgs[1]

            await client.send_message(message.channel, TextToChange)
            
        elif message.content.startswith('!links'):
            with open("links.txt", "r") as text_file:
                linkText = text_file.read()
            await client.send_message(message.channel, linkText)

        elif message.content.startswith('!settimer'):
            if (len(args) < 2):             
                TimerText = "Du måste ange en tid"           
            else:
                timerMessage = args[1].split(' ', 1)
                if (float(timerMessage[0]) >= 480):
                    TimerText = "Maxtid för timern är 8 timmar / 480 minuter"
                else:
                    await client.send_message(message.channel, "Timer is set for " + timerMessage[0] + " Min")                      
                    await asyncio.sleep(float(timerMessage[0])*60)
                    if (len(timerMessage) < 2):                       
                        TimerText = '<@' + message.author.id + '> piip piip piip'
                    else:
                        TimerText = '<@' + message.author.id + '> ' + timerMessage[1]
            
            await client.send_message(message.channel, TimerText)

        elif message.content.startswith('!ban'):
            if(message.author.id == data["MyDid"]):
                if (len(args) < 2):
                    banned = "Ange ett id"
                else:
                    BannedUsers
                    BannedUsers.append(args[1])
                    BannedList = ','.join(BannedUsers)
                    with open("banned.txt", "w") as text_file:
                        text_file.write(str(BannedList))

                    banned = '<@' + args[1] + '> ' + 'bannad'             
            else:
                banned = "Du har inte rättigheter för detta enbart min skapare göra"
            
            await client.send_message(message.channel, banned)

        elif message.content.startswith('!uban'):
            if(message.author.id == data["MyDid"]):
                if (len(args) < 2):
                    ubanned = "Ange ett id"
                else:
                    BannedUsers.remove(args[1])
                    BannedList = ','.join(BannedUsers)
                    with open("banned.txt", "w") as text_file:
                        text_file.write(str(BannedList)) 

                    ubanned = '<@' + args[1] + '> ' + 'unbannad'                          
            else:
                ubanned = "Du har inte rättigheter för detta enbart min skapare göra"
            
            await client.send_message(message.channel, ubanned)

        elif message.content.startswith('!updateban'):
            with open("banned.txt", "r") as text_file:
                BannedUsers = text_file.read().split(',')
                    
            BannedList = ", ".join(["<@%s>" % (k) for k in BannedUsers])           
            if len(BannedUsers) < 2:
                BannedList = "listan är tom"
                    
            await client.send_message(message.channel, BannedList)
        
        elif message.content.startswith('!crypto'):
            if (len(args) < 2):
                    cryptoText = "Ange en valuta"
            else:
                cryptoName = str(args[1])
                url = "https://api.coinmarketcap.com/v1/ticker/"+ cryptoName +"/?convert=EUR"

                try: urllib.request.urlopen(url)
                except urllib.error.URLError as e:
                    cryptoText = cryptoName + " is " + e.reason
                else:
                    with urllib.request.urlopen(url) as url:
                        cryptoValue = json.loads(url.read().decode())

                    cryptoText = cryptoName + ' är just nu värd ' +  cryptoValue[0]['price_eur'] + ' EUR och senaste förendringen under 24 timmar är ' + cryptoValue[0]['percent_change_24h'] + '%'

                    
            await client.send_message(message.channel, cryptoText)

client.run(data["Dtoken"])
