#core
from winpty import PtyProcess #pywinpty
import os, sys, time, re, threading, logging
from functools import partial
#Kivy core
import kivy
from kivy.config import Config
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '400')
Config.set('graphics', 'resizable', False)
from kivy.app import App
from kivy.lang import Builder
from kivy.resources import resource_add_path, resource_find
#Kivy widgets
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.clock import Clock

class Caster():
    adr = None #current game IP
    playing = False #TODO True when Netplaying
    rf = -1 #user rollback frames
    df = -1 #user delay frames
    rs = -1 #suggested rollback frames
    ds = -1 #suggested delay frames
    p1 = None #TODO p1 side name 
    p2 = None #TODO p2 side name
    aproc = None #active caster

    #TODO for some reason it doesnt always return complete caster output.
    def host(self,sc): #sc is active screen to trigger frame delay select
        proc = PtyProcess.spawn('cccaster.v3.0.exe -n 0')
        self.aproc = proc
        while proc.isalive():
            ip = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{,5}',proc.readline()) #find IP and port combo for host
            if ip != []:
                self.adr = str(ip[0])
                break
        while proc.isalive():
            con = str(proc.read())
            if "rollback:" in con and "[?25h" in con: #looks for rollback set dialogue
                n = [i for i in re.findall('[0-9]+', con) if int(i) < 15 and str(i) != '0'] #find all numbers 1-15 for caster set suggestion
                self.ds =  int(n[-5]) - int(n[-3])
                self.rs =  int(n[-3])
                r = []
                namecheck = False #try to read names from caster output
                for x in con.split():
                    if x == '\x1b[0m*' and namecheck == False:
                        namecheck = True
                    if x != '\x1b[0m*' and namecheck == True:  
                        if x == '\x1b[0K*':
                            r.pop()
                            break
                        else:
                            r.append(x)
                p = re.findall('\d+\.\d+',con) #find all floats in caster output and use the last one [-1] to make sure we get caster text
                sc.frameset(' '.join(r),p[-1])
                while True:
                    if self.rf != -1 & self.df != -1:
                        proc.write('\x08') #two backspace keys for edge case of >9 frames
                        proc.write('\x08')
                        proc.write(str(self.rf))
                        proc.write('\x0D')
                        time.sleep(0.5) #slight delay to let caster refresh screen
                        proc.write('\x08')
                        proc.write('\x08')
                        proc.write(str(self.df))
                        proc.write('\x0D')
                        #self.playing = True #set netplaying to avoid caster being killed
                        break

    def join(self,ip,sc,*args):
        proc = PtyProcess.spawn('cccaster.v3.0.exe -n %s' % ip)
        self.aproc = proc
        while proc.isalive():
            con = str(proc.read())
            if "rollback:" in con and "[?25h" in con:
                n = [i for i in re.findall('[0-9]+', con) if int(i) < 15 and str(i) != '0']
                self.ds =  int(n[-5]) - int(n[-3])
                self.rs =  int(n[-3])
                r = []
                namecheck = False
                for x in con.split():
                    if x == 'to' and namecheck == False:
                        namecheck = True
                    if x != 'to' and namecheck == True:  
                        if x == '\x1b[0K*':
                            break
                        else:
                            r.append(x)
                p = re.findall('\d+\.\d+',con)
                sc.frameset(' '.join(r),p[-1])
                while True:
                    if self.rf != -1 & self.df != -1:
                        proc.write('\x08')
                        proc.write('\x08')
                        proc.write(str(self.rf))
                        proc.write('\x0D')
                        time.sleep(0.5)
                        proc.write('\x08')
                        proc.write('\x08')
                        proc.write(str(self.df))
                        proc.write('\x0D')
                        #self.playing = True
                        break

    def watch(self,ip,*args):
        proc = PtyProcess.spawn('cccaster.v3.0.exe -n -s %s' % ip)
        self.aproc = proc
        while proc.isalive():
            con = str(proc.read())
            if "fast-forward)" in con and "[?25h" in con: #in testing it seems the later caster output text gives better accuracy
                n = con.split()
                i = 0
                r = []
                for x in n:
                    if i < 13:
                        i = i + 1
                    else:
                        if x == '\x1b[0K*':
                            break
                        else:
                            r.append(x)
                CApp.DirectScreen.activePop.modalTxt.text = ' '.join(r) #replace connecting text with match name in caster
                proc.write('1')
                break
    
    def training(self):
        proc = PtyProcess.spawn('cccaster.v3.0.exe')
        self.aproc = proc
        while proc.isalive():
            if "Offline" in proc.read():
                proc.write('4') #4 is offline
                time.sleep(0.1)
                proc.write('1')
                break

    def local(self):
        proc = PtyProcess.spawn('cccaster.v3.0.exe')
        self.aproc = proc
        while proc.isalive():
            if "Offline" in proc.read():
                proc.write('4')
                time.sleep(0.1)
                proc.write('2')
                break

    def tournament(self):
        proc = PtyProcess.spawn('cccaster.v3.0.exe')
        self.aproc = proc
        while proc.isalive():
            if "Offline" in proc.read():
                proc.write('4')
                time.sleep(0.1)
                proc.write('4')
                break
    
    def replays(self):
        proc = PtyProcess.spawn('cccaster.v3.0.exe')
        self.aproc = proc
        self.playing = True
        while proc.isalive():
            if "Offline" in proc.read():
                proc.write('4')
                time.sleep(0.1)
                proc.write('5')
                break

class GameModal(ModalView):
    modalTxt = ObjectProperty(None)
    closeBtn = ObjectProperty(None)

class FrameModal(ModalView):
    frameTxt = ObjectProperty(None)
    r_input = ObjectProperty(None)
    d_input = ObjectProperty(None)
    startBtn = ObjectProperty(None)
    closeBtn = ObjectProperty(None)

class DirectScreen(Screen):
    userIP = ObjectProperty(None) #IP input field
    activePop = None #active popup on the screen

    def host(self, *args):
        caster = threading.Thread(target=CApp.game.host,args=[self],daemon=True)
        caster.start()
        while True:
            if CApp.game.adr is not None:
                popup = GameModal()
                popup.modalTxt.text = 'Hosting to IP: %s\nAddress copied to clipboard.' % CApp.game.adr
                popup.closeBtn.text = 'Stop Hosting'
                popup.closeBtn.bind(on_release=partial(self.dismiss,t=caster,p=popup))
                self.activePop = popup
                popup.open()
                break

    def join(self, *args):
        caster = threading.Thread(target=CApp.game.join,args=[self.userIP.text,self],daemon=True)
        caster.start()
        popup = GameModal()
        popup.modalTxt.text = 'Connecting to IP: %s' % self.userIP.text
        popup.closeBtn.text = 'Stop Playing'
        popup.closeBtn.bind(on_release=partial(self.dismiss,t=caster,p=popup))
        self.activePop = popup
        popup.open()
    
    def frameset(self,name,ping):
        fpopup = FrameModal()
        fpopup.frameTxt.text = 'Connected to: %s\nPing: %s, Suggested: Rollback %s,  Delay %s' % (name, ping, CApp.game.rs, CApp.game.ds)
        fpopup.r_input.text = str(CApp.game.rs)
        fpopup.d_input.text = str(CApp.game.ds)
        fpopup.startBtn.bind(on_release=partial(self.confirm,p=fpopup,r=fpopup.r_input,d=fpopup.d_input))
        fpopup.closeBtn.bind(on_release=partial(self.dismiss,t=CApp.game.aproc,p=fpopup))
        fpopup.open()
    
    def confirm(self,obj,r,d,p,*args):
        CApp.game.rf = int(r.text)
        CApp.game.df = int(d.text)
        p.dismiss()

    def training(self, *args):
        caster = threading.Thread(target=CApp.game.training,daemon=True)
        caster.start()
        popup = GameModal()
        popup.modalTxt.text = 'Training mode started.'
        popup.closeBtn.text = 'Close game'
        popup.closeBtn.bind(on_release=partial(self.dismiss,t=caster,p=popup))
        self.activePop = popup
        popup.open()

    def replays(self, *args):
        caster = threading.Thread(target=CApp.game.replays,daemon=True)
        caster.start()
        popup = GameModal()
        popup.modalTxt.text = 'Replay Theater started.'
        popup.closeBtn.text = 'Close game'
        popup.closeBtn.bind(on_release=partial(self.dismiss,t=caster,p=popup))
        self.activePop = popup
        popup.open()

    def local(self, *args):
        caster = threading.Thread(target=CApp.game.local,daemon=True)
        caster.start()
        popup = GameModal()
        popup.modalTxt.text = 'Local VS started.'
        popup.closeBtn.text = 'Close game'
        popup.closeBtn.bind(on_release=partial(self.dismiss,t=caster,p=popup))
        self.activePop = popup
        popup.open()

    def tournament(self, *args):
        caster = threading.Thread(target=CApp.game.tournament,daemon=True)
        caster.start()
        popup = GameModal()
        popup.modalTxt.text = 'Tournament Local VS started.'
        popup.closeBtn.text = 'Close game'
        popup.closeBtn.bind(on_release=partial(self.dismiss,t=caster,p=popup))
        self.activePop = popup
        popup.open()

    def watch(self, *args):
        popup = GameModal()
        self.activePop = popup
        caster = threading.Thread(target=CApp.game.watch,args=[self.userIP.text],daemon=True)
        caster.start()
        popup.modalTxt.text = 'Watching IP: %s' % self.userIP.text
        popup.closeBtn.text = 'Close game'
        popup.closeBtn.bind(on_release=partial(self.dismiss,t=caster,p=popup))
        popup.open()

    #TODO prevent players from dismissing caster until MBAA is open to avoid locking issues
    def dismiss(self,obj,t,p,*args):
        CApp.game.adr = None
        CApp.game.rs = -1
        CApp.game.ds = -1
        CApp.game.rf = -1
        CApp.game.df = -1
        os.system('start /min taskkill /f /im cccaster.v3.0.exe')
        del(t)
        p.dismiss()
        CApp.game.aproc = None
        CApp.game.playing = False

class Concerto(App):
    def __init__(self,c,**kwargs):
        super(Concerto, self).__init__(**kwargs)
        self.sm = ScreenManager()
        self.game = c #expects Caster object

    def build(self):
        self.DirectScreen = DirectScreen()
        self.sm.add_widget(self.DirectScreen)
        return self.sm

    def checkPop(self,*args):
        while True:
            if self.game.aproc != None:
                if self.game.aproc.isalive():
                    pass
                else:
                    self.DirectScreen.activePop.dismiss()
                    self.DirectScreen.activePop = None
                    CApp.game.adr = None
                    CApp.game.rs = -1
                    CApp.game.ds = -1
                    CApp.game.rf = -1
                    CApp.game.df = -1
                    os.system('start /min taskkill /f /im cccaster.v3.0.exe')
                    CApp.game.aproc = None
            time.sleep(1) #checks for netplaying every 1 second by polling isalive() from game.aproc
   
CApp = Concerto(Caster())

if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'): #necessary for pyinstaller to work
        resource_add_path(os.path.join(sys._MEIPASS))
    Builder.load_file("Concerto.kv") #concerto.kv defines UI
    netwatch = threading.Thread(target=CApp.checkPop,daemon=True) #netplay watchdog
    netwatch.start()
    CApp.run()