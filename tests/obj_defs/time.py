class Time:
    
    def __init__(self, hours : int, minutes : int = 0, seconds : int = 0):
        self._hours : int = hours
        self._minutes : int = minutes
        self._seconds : int = seconds
        
    @property
    def hours(self):
        return self._hours

    @hours.setter
    def hours(self, value):  
        self._hours = value % 24
        
    @property
    def minutes(self):
        return self._minutes
    
    @minutes.setter
    def minutes(self, value):
        hours = int(value / 60)
        self._minutes = value % 60
        
        if hours > 0:
            self.hours = self.hours + hours
            
    @property
    def seconds(self):
        return self._seconds
    
    @seconds.setter
    def seconds(self, value):
        minutes = int(value / 60)
        self._seconds = value % 60
        if minutes > 0:
            self.minutes = self.minutes + minutes
        
    def __format__(self, format_spec) -> str:
        return f"{str(self.hours).zfill(2)}:{str(self.minutes).zfill(2)}:{str(self.seconds).zfill(2)}"
    
    @classmethod
    def parse(cls, time_string : str):
        if not isinstance(time_string, str): raise TypeError("You can only parse strings")
        time_strings = time_string.split(":")
        if len(time_strings) == 0:
            return cls(0, 0, 0)
        elif len(time_strings) == 1:
            return cls(int(time_strings[0]), 0, 0)
        elif len(time_strings) == 2:
            return cls(int(time_strings[0]), int(time_strings[1]), 0)
        elif len(time_strings) == 3:
            return cls(int(time_strings[0]), int(time_strings[1]), int(time_strings[2]))
        else:
            raise ValueError("Couldn't parse the timestring")