import os, tempfile, threading, requests       
from just_playback import Playback         
from customtkinter import *           

set_appearance_mode("light")       

app = CTk()    
app.title("Audio Streaming app with python")    
app.geometry("400x300")       


# now we will make a class AudioStream to stream audio       

class AudioStream:          
    def __init__(self):       
        self.player = Playback()        
        self.songs = []      
        self.urls = []      
        self.current_index = 0     
        self._temp_files = []           
        self._lock = threading.Lock()             

    def _download(self, url):      
        # this will download a temproary mp3 file form github repo       
        try:     
            response = requests.get(url, timeout=15, stream=True) 
            response.raise_for_status()  

            fd, path = tempfile.mkstemp(suffix="mp3")  
            os.close(fd)  

            with open(path, "wb") as file:  
                for chunk in response.iter_content(chunk_size=8192):   
                    if chunk:  
                        file.write(chunk)   

                self._temp_files.append(path)  
                return path         
        except Exception as e:  
            print(f"Failed : {e}")  
            return None   

    def load_single(self, url):  
        #  this fucntion will load a single mp3 songs form online  
        self.stop()   
        self.urls = [url]    
        self.current_index = 0  

        local = self._download(url)  
        if local:  
            self.songs = [local]  
            self.player.load_file(local)  
        else:  
            self.songs = []  

    def play(self):  
        if self.songs: 
            self.player.play()   

    def pause(self):   
        self.player.pause()   

    def resume(self):   
        self.player.resume()   

    def stop(self):   
        try:   
            self.player.stop()   
        except:   
            pass           
        self.current_index = 0   

    def get_duration(self):  
        try:  
            return int(self.player.duration * 1000)   
        except:   
            return 0  
        
    def get_current_time(self):    
        try:   
            return int(self.player.curr_pos * 1000)  
        except:    
            return 0   
  
    def format_time(self, ms):  
        if ms < 0:  
            return "00:00"  
        total_seconds = ms // 1000  
        minutes = total_seconds // 60  
        seconds = total_seconds % 60   
        return f"{minutes:02d}:{seconds:02d}"  

    def seek(self, ms):   
        try:  
            self.player.seek(ms /1000.0)  
        except:  
            pass   
    def cleanup(self):  
        # this function will be called after we end teh program to clean teh temp files   
        self.stop()  
        for f in self._temp_files:  
            try:  
                if os.path.exists(f):  
                    os.remove(f)     
            except:   
                pass          
        self._temp_files.clear()   

    def __del__(self):   
        self.cleanup()   
 
stream = AudioStream()  
 
stream.load_single("https://raw.githubusercontent.com/SarthakTools/music/main/songs/Last%20Summer%20by%20Ikson.mp3") # here we will put github link 

# before inserting link make sure to make some changes like remove blob and instaead of github.com put raw.githubusercontent.com  

is_playing = False   

def toggle_music():  
    global is_playing  
    if is_playing:  
        stream.pause()  
        button_play.configure(text="Play")   
        is_playing = not is_playing  
    else:  
        stream.play()  
        button_play.configure(text="Pause")  
        is_playing = not is_playing  
    

def extract_song_name(url):   
    return url.split("/")[-1] if url else "Unknown"   

def update_progressbar(progressbar, stream):  
    if stream.songs:  
        duration = stream.get_duration()   
        start_time_label.configure(text=stream.format_time(stream.get_current_time()))  
        end_time_label.configure(text=stream.format_time(duration))  
        current_time = stream.get_current_time()  
        if duration > 0:  
            progress = current_time / duration  
            progressbar.set(progress)  
    app.after(1000, lambda: update_progressbar(progressbar, stream))  


button_play = CTkButton(app, text="Play", command=toggle_music,  font=("consolas", 18, "bold"))  
button_play.pack(pady=24)    

bottom_frame = CTkFrame(app)    

start_time_label= CTkLabel(bottom_frame, text="00:00", font=("monospace", 14, "bold"))   
start_time_label.pack(side=LEFT, padx=10)

end_time_label = CTkLabel(bottom_frame, text="00:00", font=("monospace", 14, "bold"))   
end_time_label.pack(side=RIGHT, padx=10)  

song_label = CTkLabel(bottom_frame, text=f"Now Playing : {extract_song_name(stream.urls[0]) if stream.urls else 'None'}")   
song_label.pack(pady=5)  
 
progressbar = CTkProgressBar(bottom_frame, width=300)  
progressbar.pack(pady=5)  
progressbar.set(0)  
 
app.after(1000, lambda:update_progressbar(progressbar, stream))  

bottom_frame.pack(side=BOTTOM, fill=X, pady=10)  

app.mainloop()    