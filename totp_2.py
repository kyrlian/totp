#!/usr/bin/python
import random
import math
import pygame
from pygame.locals import *

TITLE = "Typing Of The Python 2.0 (c) Kyrlian 2008-2020"

#sound can conflict with other music (xmms), set this to 1 to play without sound 
NOSOUND=0
#avoid multiple words starting with same letter 
NODUPS=1

LETTERSDICO="./dicos/letters.txt"
LANGS=[['FR','./dicos/words_fr.txt'],['EN','./dicos/words_en.txt']]

SCOREFILE="./scores.txt"
TEXTFONTSIZE=20
WORDFONTSIZE=20
MESSAGEFONTSIZE=14
TTFONT="./fonts/Superhelio Regular.TTF"

STARTTIME=10*1000
INITIALLETTERTIME=1*1000
DECREASELETTERTIME=100
MINWORDS=2
MAXWORDS=6
LETTERSROUND=5
MINLETTERS=4
MAXLETTERS=10
ROUNDSCORE=100
WORDSCORE=10

SCREEN = Rect(0, 0, 800,600)
WORDCOLOR=(255,255,255)
DONECOLOR=(0,255,0)

CURLANG=LANGS[0][0]
wordsfile=open(LANGS[0][1], 'r')
wordslist=wordsfile.readlines()
wordsfile.close()

lettersfile=open(LETTERSDICO, 'r')
letterslist=lettersfile.readlines()
lettersfile.close()

class Word(pygame.sprite.Sprite):
    def __init__(self, i,nbwords, word):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font(TTFONT, WORDFONTSIZE)
        msg = self.font.render(word, 1, WORDCOLOR)
        self.image = pygame.Surface(msg.get_size())
        self.image.set_colorkey((0, 0, 0), RLEACCEL)
        self.image.blit(msg, (0, 0))
        pos = (int(random.randrange(SCREEN.width-msg.get_width()-20)+10+msg.get_width()/2),int(SCREEN.height*(i+1)/(nbwords+1)))
        self.rect = self.image.get_rect(center = pos)
        self.word=word
        self.progress=0
        self.nextletter=self.word[self.progress].lower()
        self.moreletters=len(self.word)-self.progress
        self.pos=pos
    def consume(self):
        global score
        global multiplier
        self.progress+=1        
        self.moreletters=len(self.word)-self.progress
        msg = self.font.render(self.word[0:self.progress], 1, DONECOLOR)
        self.image.blit(msg, (0, 0))
        if self.moreletters==0:
            if multiplier==1:
                msg="+"+str(WORDSCORE*len(self.word))
            else:
                msg="+"+str(WORDSCORE*len(self.word))+"x"+str(multiplier)
            Message(self.rect.midtop,msg,"green")
            score+=WORDSCORE*len(self.word)*multiplier
            multiplier+=1
            if NOSOUND==0:
                dingsnd = pygame.mixer.Sound("sounds/typewriterding.ogg")
                dingsnd.play()
            self.kill()
        else:
            self.nextletter=self.word[self.progress].lower()

class Message(pygame.sprite.Sprite):
    def __init__(self, pos, msg, color='black'):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font(TTFONT, MESSAGEFONTSIZE)
        self.font.set_bold(1)
        msg = self.font.render(msg, 1, Color(color))
        self.image = pygame.Surface(msg.get_size())
        self.image.set_colorkey((0, 0, 0), RLEACCEL)
        self.image.blit(msg, (0, 0))
        self.rect = self.image.get_rect(center = pos)
        self.trans = 255
    def update(self):
        self.trans -= 5
        if self.trans <= 0:
            self.kill()
        self.image.set_alpha(self.trans, RLEACCEL)

def GameMode(screen):
    paused=0
    sprites = pygame.sprite.RenderUpdates()
    words = pygame.sprite.Group()
    Word.containers = sprites, words
    Message.containers = sprites
    clock = pygame.time.Clock()
    global score
    global multiplier
    global lettertime
    global roundnb
    roundnb=1
    score=0
    timeleft=STARTTIME
    multiplier=1
    scrolletters="          "
    lettertime=INITIALLETTERTIME
    if NOSOUND==0:
        keysnd = pygame.mixer.Sound("sounds/typewriter.ogg")
        buzsnd = pygame.mixer.Sound("sounds/buzzer.ogg")
    while 1:
        if random.randrange(LETTERSROUND)==1:
            nbwords=random.randrange(MAXLETTERS-MINLETTERS)+MINLETTERS
            curlist=letterslist
        else:
            nbwords=random.randrange(MAXWORDS-MINWORDS)+MINWORDS
            curlist=wordslist
        fls=[]
        for i in range(nbwords):
            randword=""
            while randword=="" or (NODUPS==1 and randword[0:1] in fls):
                randword=curlist[random.randrange(len(curlist))][0:-1]
            fls.append(randword[0:1])
            nbl=len(randword)
            Word(i,nbwords,randword)
            timeleft+=nbl*lettertime
        currentword=0
        while timeleft>0 and len(words.sprites())>0:
            timeleft-=clock.tick(50)
            event = pygame.event.poll()
            if event.type == QUIT:
                pygame.quit()
                return 0
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return 0
                elif event.key == K_PAUSE:
                    paused ^= 1
                else:
                    hit=0
                    scrolletters=(scrolletters+event.unicode)[1:11]
                    if currentword not in words.sprites():
                        for candidate in words.sprites():
                            if event.unicode==candidate.nextletter:
                                currentword=candidate
                                currentword.consume()
                                hit=1
                                if NOSOUND==0:
                                    keysnd.play()
                                break
                    elif event.unicode==currentword.nextletter:
                        currentword.consume()
                        if NOSOUND==0:
                            keysnd.play()
                        hit=1
                    if hit==0:
                        multiplier=1
                        if NOSOUND==0:
                            buzsnd.play()
                        Message((SCREEN.centerx,SCREEN.centery),"!"+event.unicode.upper()+"!","red")
            screen.fill(Color("black"))
            sprites.draw(screen)
            sprites.update()
            font = pygame.font.Font(TTFONT, MESSAGEFONTSIZE)
            font.set_bold(1)
            ren = font.render("Round "+str(roundnb)+" - "+str(timeleft/1000)+" seconds left", 1, Color("white"))
            screen.blit(ren, (10, SCREEN.height-ren.get_height()-10))
            ren = font.render(scrolletters, 1, Color("white"))
            screen.blit(ren, (int((SCREEN.width-ren.get_width())/2), SCREEN.height-ren.get_height()-10))
            ren = font.render("Score "+str(score)+" (mult x"+str(multiplier)+")", 1, Color("white"))
            screen.blit(ren, (SCREEN.width-ren.get_width()-10, SCREEN.height-ren.get_height()-10))
            pygame.display.flip()
        if timeleft<=0:
            return score
        else:
            score+=ROUNDSCORE*multiplier
            lettertime-=DECREASELETTERTIME
            if lettertime<0:
                lettertime=0
            roundnb+=1

def EnterNameMode(screen,score):
    font = pygame.font.Font(TTFONT, TEXTFONTSIZE)
    name=''
    while 1:
        screen.fill(Color("black"))
        ren = font.render("Score %d" % score, 1, Color("green"))
        screen.blit(ren, (int(SCREEN.centerx-ren.get_width()/2),int( SCREEN.height/4*1-ren.get_height()/2)))
        ren = font.render("Enter your name and press Enter", 1, Color("white"))
        screen.blit(ren, (int(SCREEN.centerx-ren.get_width()/2),int( SCREEN.height/4*2-ren.get_height()/2)))
        ren = font.render(name, 1, Color("green"))
        screen.blit(ren, (int(SCREEN.centerx-ren.get_width()/2),int( SCREEN.height/4*3-ren.get_height()/2)))
        event = pygame.event.poll()
        if event.type == QUIT:
            pygame.quit()
            return
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                return 'TOTP'
            elif event.key == K_RETURN:
                if len(name) == 0:
                    name='TOTP'
                return name
            elif event.key == K_BACKSPACE:
                name=name[0:-1]
            else:
                name+=event.unicode
        if len(name)>20:
            return name
        pygame.display.flip()

def mrevsort(x,y):
    a=x.split(' - ')[0]
    b=y.split(' - ')[0]
    try:
        return int(b)-int(a)
    except:
        return cmp(b,a)
    
def ShowScoresMode(screen):
    font = pygame.font.Font(TTFONT, TEXTFONTSIZE)
    titleren = font.render("High-Scores", 1, Color("white"))
    scorefile=open(SCOREFILE,'r')
    scorelist=scorefile.readlines()
    scorefile.close()
    #scorelist.sort(mrevsort)
    scorelist.sort()
    nbl=min(len(scorelist),SCREEN.height/titleren.get_height()-1)
    nbs=nbl+2
    while 1:
        screen.fill(Color("black"))
        screen.blit(titleren, (int(SCREEN.centerx-titleren.get_width()/2), int(SCREEN.height/nbs*1-titleren.get_height()/2)))
        font = pygame.font.Font(TTFONT, MESSAGEFONTSIZE)
        for i in range(nbl):
            ren = font.render(scorelist[i][0:-1], 1, Color("white"))
            screen.blit(ren, (int(SCREEN.centerx-ren.get_width()/2), int(SCREEN.height/nbs*(i+2)-ren.get_height()/2)))
        event = pygame.event.poll()
        if event.type == QUIT:
            pygame.quit()
            return
        if event.type == KEYDOWN:
            return 0
        pygame.display.flip()

def MenuMode(screen):
    global NOSOUND, CURLANG, wordslist
    score=0
    while 1:
        if NOSOUND:
            soundonoff = "off"
        else:
            soundonoff = "on"
        screen.fill(Color("black"))
        font = pygame.font.Font(TTFONT, TEXTFONTSIZE)
        ren = font.render(TITLE, 1, Color("white"))
        screen.blit(ren, (int(SCREEN.centerx-ren.get_width()/2), int(SCREEN.height/6*1-ren.get_height()/2)))
        if score>0:
            ren = font.render("Score %d" % score, 1, Color("green"))
            screen.blit(ren, (int(SCREEN.centerx-ren.get_width()/2), int(SCREEN.height/6*1-ren.get_height()/2)))
        ren = font.render("Press Space to start - h for high-scores - Esc to quit", 1, Color("white"))
        screen.blit(ren, (int(SCREEN.centerx-ren.get_width()/2), int(SCREEN.height/6*3-ren.get_height()/2)))
        ren = font.render("Sound "+soundonoff+" (press s to toggle)", 1, Color("white"))
        screen.blit(ren, (int(SCREEN.centerx-ren.get_width()/2), int(SCREEN.height/6*4-ren.get_height()/2)))
        ren = font.render("Language: "+CURLANG+" (press l to change)", 1, Color("white"))
        screen.blit(ren, (int(SCREEN.centerx-ren.get_width()/2), int(SCREEN.height/6*5-ren.get_height()/2)))
        event = pygame.event.poll()
        if event.type == QUIT:
            pygame.quit()
            return
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE or event.key == K_q:
                pygame.quit()
                return
            if event.key == K_SPACE or event.key == K_RETURN:
                once=1
                score=GameMode(screen)
                if score>0:
                    name=EnterNameMode(screen,score)
                    scorefile=open(SCOREFILE,'a')
                    scorefile.write(str(score)+' - '+name+' - Round '+str(roundnb)+' - '+CURLANG+'\n')
                    scorefile.close()
                    ShowScoresMode(screen)                
            if event.key == K_h:
                ShowScoresMode(screen)
            if event.key == K_s:
                NOSOUND ^= 1
            if event.key == K_l:
                for i in range(len(LANGS)):
                    if LANGS[i][0]==CURLANG:
                        j=i+1
                        if j>=len(LANGS):
                            j=0
                CURLANG=LANGS[j][0]
                wordsfile=open(LANGS[j][1], 'r')
                wordslist=wordsfile.readlines()
                wordsfile.close()
        pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption(TITLE)
    pygame.mouse.set_visible(0)
    screen = pygame.display.set_mode(SCREEN.size)
    #    screen = pygame.display.set_mode(SCREEN.size, FULLSCREEN)
    MenuMode(screen)
