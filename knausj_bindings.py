from talon import actions, cron, scope, speech_system
from user.talon_hud.state import hud_content

# Polls the current state using knausj bindings
# Used several bindings from the knausj repository like history
# TODO - Make this dynamic based on events
class KnausjStatePoller:
    
    job = None
    enabled = False
    current_lang_forced = False
    
    def enable(self):
        if (self.enabled != True):
            self.enabled = True
            speech_system.register("phrase", self.on_phrase)
            if (self.job is None):
                self.job = cron.interval('100ms', self.state_check)
                

    def disable(self):
        if (self.enabled != False):
            self.enabled = False        
            speech_system.unregister("phrase", self.on_phrase)
            if (self.job is not None):
                cron.cancel(self.job)
            self.job = None

    def state_check(self):
        content = {
            'mode': self.determine_mode(),
            'language': {
                'ext': self.get_lang_extension(self.determine_language()),
                'forced': self.current_lang_forced
            }
        }
        
        hud_content.update(content)
            
    def on_phrase(self, j):
        try:
            word_list = getattr(j["parsed"], "_unmapped", j["phrase"])
        except:
            word_list = j["phrase"]
        hud_content.append_to_log("command", " ".join(word.split("\\")[0] for word in word_list))
    
    # Determine three main modes - Sleep, command and dictation
    def determine_mode(self):
        active_modes = scope.get('mode')

        # If no mode is given, just show command
        mode = 'command'
        if ( active_modes is not None ):
            if ('sleep' in active_modes):
                mode = 'sleep'
            if ('dictation' in active_modes):
                mode = 'dictation'
            if ('user.czech' in active_modes):
                mode = 'czech'
            if ('user.german' in active_modes):
                mode = 'german'
            if ('user.intermediate' in active_modes):
                mode = 'intermediate'
        
        return mode
    
    # Language map added from knausj
    language_to_ext = {
        "assembly": ".asm",
        "batch": ".bat",
        "c": ".c",
        "cplusplus": ".cpp",
        "csharp": ".c#",
        "gdb": ".gdb",
        "go": ".go",
        "lua": ".lua",
        "markdown": ".md",
        "perl": ".pl",
        "powershell": ".psl",
        "python": ".py",
        "ruby": ".rb",
        "bash": ".sh",
        "snippets": "snip",
        "talon": ".talon",
        "vba": ".vba",
        "vim": ".vim",
        "javascript": ".js",
        "typescript": ".ts",
        "r": ".r",
        "tex": ".tex",
    }
    
    # Determine the forced or assumed language
    def determine_language(self): 
        lang = actions.code.language()
        if (not lang):
            active_modes = scope.get('mode')
            if (active_modes is not None):
                for index, active_mode in enumerate(active_modes):
                    if (active_mode.replace("user.", "") in self.language_to_ext):
                        self.current_lang_forced = True
                        return active_mode.replace("user.", "")
            return ""
        else:
            self.current_lang_forced = False
            return lang if lang else ""
        
    def get_lang_extension(self, language):
        if (language in self.language_to_ext):
            return self.language_to_ext[language]
        else:
            '' 
