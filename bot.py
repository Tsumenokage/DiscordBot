import discord
import asyncio
import re
import pafy
import downloader
import threading
import youtube_dl
from enum import Enum
from discord import opus

print(discord.opus.is_loaded())

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '/music_cache/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

class MusicPlayerState(Enum):
    STOPPED = 0  # When the player isn't playing anything
    PLAYING = 1  # The player is actively playing music.
    PAUSED = 2   # The player is paused on a song.
    WAITING = 3  # The player has finished its song but is still downloading the next one


client = discord.Client()
master = "Tsumenokage"
playlist = []
prefix = '!'
playState = MusicPlayerState.STOPPED
botName = 'GLaDOS'
voice = None
player = None;


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    patternSalut = re.compile("^[B-b]onjour$")
    if message.content.startswith(prefix + 'dc'):
        if(message.author.name == "Tsumenokage"):
            await client.logout()
        else:
            await client.send_message(message.channel, message.author.mention + " je suis désolée, mes protocoles de sécurité m'interdisent de vous laisser utiliser cette commande")
    elif patternSalut.match(message.content):
        print("Bonjour je m'apelle machin")
        await client.send_message(message.channel,"Salut " + message.author.mention)
    elif (message.content.startswith(prefix + 'playlist')):
        if(len(playlist) == 0):
            await client.send_message(message.channel, "Aucune musique ne se trouve actuellement dans la playlist")
        else:
            if len(playlist)>10:
                max = 10
            else:
                max = len(playlist)            
            i = 1
            description = ''
            while i<max+1:
                description += str(i) + " : " + playlist[i-1][0] + '\n\r'
                i = i+1
            em = discord.Embed(title='Playlist : ', description=description, colour=0xDEADBF)
            em.set_author(name=botName, icon_url=client.user.default_avatar_url)
            await client.send_message(message.channel, embed=em)
    elif(message.content.startswith(prefix + 'add')):
        data = message.content.split()
        url = data[1]
        t1 = threading.Thread(target=download_info, args=[url])
        t1.start()
        t1.join()
    elif(message.content.startswith(prefix + 'play')):
        if client.is_voice_connected(message.server) == False:
            voice = await client.join_voice_channel(message.author.voice.voice_channel)
            if playState == MusicPlayerState.STOPPED or playState == MusicPlayerState.PAUSED : 
                player = await voice.create_ytdl_player(playlist[0][1],ytdl_options = ydl_opts,after=my_after)
                player.start()

async def next_song():
    playlist.pop(0)
    if(len(playlist) != 0):
        print('Musique suivante')
        player = await voice.create_ytdl_player(playlist[0][1],ytdl_options = ydl_opts,after=next_song)
        player.start()
    else:
        print('Playlist vide')


def my_after(): 
    playlist.pop(0)
    if(len(playlist) != 0):
        print('Musique suivante')
        coro = voice.create_ytdl_player(playlist[0][1],ytdl_options = ydl_opts,after=my_after)
        fut = asyncio.run_coroutine_threadsafe(coro, client.loop)
        try:
            fut.result()
            coro.start()
        except:
            # an error happened sending the message
            pass
    else:
        print('Playlist vide')


def download_info(url):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        meta = ydl.extract_info(
        url, download=False) 
        playlist.append([meta['title'],meta['url']])
        

print('Connecting');
client.run('MTkyNzI0Nzc1NTczOTEzNjAx.C5BElg.HiH_WE2-8Lfg8CI0rfpAEvrLb7c')
