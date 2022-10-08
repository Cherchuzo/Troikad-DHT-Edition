class Utils():
    
    @staticmethod
    def humansizeBytes(nbytes):
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        i = 0
        while nbytes >= 1024 and i < len(suffixes)-1:
            nbytes /= 1024.
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return '%s %s' % (f, suffixes[i])

    @staticmethod
    def toTime(total, tmp, time = 60):
        totalSeconds = 0
        if tmp != 0:
            totalSeconds = total / tmp
        days = hours = minutes = seconds = 0
        while totalSeconds > 0:
            if totalSeconds - 60 >= 0:
                seconds += totalSeconds - 60
            else:
                seconds = totalSeconds
                totalSeconds = 0
            if seconds == 60:
                minutes += 1
                seconds = 0
            if minutes == 60:
                hours += 1
                minutes = 0
            if hours == 24:
                days += 1
                hours = 0
            totalSeconds -= 60

        if 10 > days > 0:
            days = "0" + str(int(days))
        elif days >= 10:
            days = str(int(days))
        else:
            days = "00"

        if 10 > hours > 0:
            hours = "0" + str(int(hours))
        elif hours >= 10:
            hours = str(int(hours))
        else:
            hours = "00"

        if 10 > minutes > 0:
            minutes = "0" + str(int(minutes))
        elif minutes >= 10:
            minutes = str(int(minutes))
        else:
            minutes = "00"

        if 10 > seconds > 0:
            seconds = "0" + str(int(seconds))
        elif seconds >= 10:
            seconds = str(int(seconds))
        else:
            seconds = "00"
        return days + ":" + hours + ":" + minutes + ":" + seconds + " rimanenti"