from telegram.ext import CommandHandler
from bot.helper.mirror_utils.upload_utils import gdriveTools
from bot.helper.telegram_helper.message_utils import *
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.mirror_utils.status_utils.clone_status import CloneStatus
from bot import dispatcher, LOGGER, CLONE_LIMIT, STOP_DUPLICATE, download_dict, download_dict_lock, Interval
from bot.helper.ext_utils.bot_utils import get_readable_file_size, check_limit
import random
import string
#জিডিটট ও এপড্রাইভ ইম্পোর্ট'স
import requests
import random
import re
from base64 import b64decode
from urllib.parse import urlparse, parse_qs

#জিডিটট ও এপড্রাইভ মডিউল 

APPDRIVE_ACCOUNTS = [
  {
    "email":"gdtot1@brccollege.edu.in",
    "password":"gdtot1@brccollege.edu.in"
  },

  {
    "email":"gdtot2@brccollege.edu.in",
    "password":"gdtot2@brccollege.edu.in"
  },

  {
    "email":"gdtot3@brccollege.edu.in",
    "password":"gdtot3@brccollege.edu.in"
  },

  {
    "email":"gdtot4@brccollege.edu.in",
    "password":"gdtot4@brccollege.edu.in"
  },

  {
    "email":"gdtot5@brccollege.edu.in",
    "password":"gdtot5@brccollege.edu.in"
  },
  
]


class AppDrive:
  def __init__(self, baseURL:str = "https://appdrive.in") -> None:
    self.loginData = random.choice(APPDRIVE_ACCOUNTS)
  
    self.keyRegex = '"key",\s+"(.*?)"'
    self.BaseURL = baseURL
    self.reqSes = requests.Session()
    self.headers = {
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
      'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
      'referer': self.BaseURL,
  }
    self.reqSes.headers.update(self.headers)
  
  def login(self) -> bool:
    login_ = self.reqSes.post(f'{self.BaseURL}/login', data=self.loginData)
    if login_.cookies.get("MD"):
      return True
    return False
  
  def download(self, url:str) -> str:

    if not self.login():
      raise Exception("Falied to login Please try again")

    try:
      res = self.reqSes.get(url)
      key = re.findall(self.keyRegex, res.text)[0]
    except:
      raise Exception("URl is Inavalid or Failed to get Key Value")

    data = {
        'type': 1,
        'key': key,
        'action': 'original'
    }
    while data['type'] <= 3:
        try:
            res = self.reqSes.post(url, data=data).json()
            break
        except: data['type'] += 1
    
    if res.get('url'):
      return res.get('url')
    else:
      raise Exception(str(res))


if __name__ == "__main__":
  print(AppDrive().download("https://appdrive.in/file/feff0b041a15d41fa714"))

GDTOT_COOKIES = [
    "NkVjQ0p1VFJ5cWFsdmZDOWI4bCszTjFVVHloU052Mm9pNGdyeUd4alJGWT0%3D",
    "Z0o0anBxemZUQUxJekQ4eWhBZ21VT25tdjNSYnFTYlUxb2V2cWZaVjY0ST0%3D",
    "Rnp2NWtkRURiZzJ3UEdEMm93MHRRSk12T0NNaExQVzcvb1pGa2lUNzZOQT0%3D",
    "TW94QVNXMUNMZjdqa3JXQi8vNFdUTW8vcUZNNHp0enJOSGVZZUh2bm5rcz0%3D",
    "TDVpOWtjR2RGSDFDVmxlMDFKZElvV1pUUGJYL24zeHJXK3lNY1lOcXQzVT0%3D",
]

class GdTot:
    def __init__(self, baseURL = "https://new.gdtot.nl") -> None:
        self.loginData = random.choice(GDTOT_COOKIES)
        self.gdRegex = 'gd=(.*?)&'
        self.BaseURL = baseURL
        self.reqSes = requests.Session()
        self.headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'referer': self.BaseURL,
        'crypt':self.loginData
        }
        self.reqSes.headers.update(self.headers)
        self.reqSes.cookies.update({'crypt': self.loginData})

    def login(self) -> bool:
        login_ = self.reqSes.post(f'{self.BaseURL}')
        if "/login.php?action=logout" in login_.text:
            self.reqSes.cookies.update({"PHPSESSID":login_.cookies.get('PHPSESSID')})
            return True
        return False

    def download(self, url: str) -> str:

        self.baseURL = "https://{domain}".format(domain=urlparse(url).netloc)
        self.reqSes.headers.update({"referer":url})
        # Extracting Domain base url from URL path itself so we don't have to edit it again

        if not self.login():
            raise Exception("Falied to login Please try again")
        try:
            id = url.split('/')[-1]
            res = self.reqSes.get(f"{self.BaseURL}/dld?id={id}")
            urll = re.findall('URL=(.*?)\"', res.text)[0]
            qs = parse_qs(urlparse(urll).query)
            # getGDUrl = re.findall(self.gdRegex, res.text)
            # print(getGDUrl)
            if qs['gd'][0] == 'false':
                err_msg = qs['msgx'][0]
                raise Exception(err_msg)
            else:
                gdUrl = b64decode(str(qs['gd'])).decode('utf-8')
                return f'https://drive.google.com/file/d/{gdUrl}/view'
        except Exception as err:
            raise Exception(f"Failed to get download url Please try again - {str(err)}")
                    
if __name__ == "__main__":
    print(GdTot().download("https://new.gdtot.nl/file/161529855"))
    # print(GdTot().download("https://new.gdtot.nl/file/20395706860"))
#জিডিটট ও এপড্রাইভ মডিউল শেষ এইখানে।

def cloneNode(update, context):
    args = update.message.text.split(" ", maxsplit=1)
    if len(args) > 1:
        link = args[1]
        
        if 'new.gdtot' in link:
            try:
                msg = sendMessage(f"Detected GdTtot Link Please Wait:- \n<code>{link}</code>", context.bot, update)
                link = GdTot().download(link)
                deleteMessage(context.bot, msg)
            except Exception as e:
                deleteMessage(context.bot, msg)
                return sendMessage(str(e), context.bot, update)

        if 'appdrive' in link:
            try:
                msg = sendMessage(f"Detected Appdrive Link Please Wait:- \n<code>{link}</code>", context.bot, update)
                link = AppDrive().download(link)
                deleteMessage(context.bot, msg)
            except Exception as e:
                deleteMessage(context.bot, msg)
                return sendMessage(str(e), context.bot, update)

        msg = sendMessage(f"Cloning: <code>{link}</code>",context.bot,update)        
        gd = gdriveTools.GoogleDriveHelper()
        res, size, name, files = gd.clonehelper(link)
        if res != "":
            sendMessage(res, context.bot, update)
            return
        if STOP_DUPLICATE:
            LOGGER.info(f"Checking File/Folder if already in Drive...")
            smsg, button = gd.drive_list(name)
            if smsg:
                msg3 = "𝐅𝐢𝐥𝐞/𝐅𝐨𝐥𝐝𝐞𝐫 𝐢𝐬 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐢𝐧 𝐃𝐫𝐢𝐯𝐞.\n𝐇𝐞𝐫𝐞 𝐀𝐫𝐞 𝐓𝐡𝐞 𝐑𝐞𝐬𝐮𝐥𝐭𝐬:"
                sendMarkup(msg3, context.bot, update, button)
                return
        if CLONE_LIMIT is not None:
            result = check_limit(size, CLONE_LIMIT)
            if result:
                msg2 = f'𝐅𝐚𝐢𝐥𝐞𝐝, 𝐂𝐥𝐨𝐧𝐞 𝐥𝐢𝐦𝐢𝐭 𝐢𝐬 {CLONE_LIMIT}.\n𝐘𝐨𝐮𝐫 𝐅𝐢𝐥𝐞/𝐅𝐨𝐥𝐝𝐞𝐫 𝐬𝐢𝐳𝐞 𝐢𝐬 {get_readable_file_size(clonesize)}.'
                sendMessage(msg2, context.bot, update)
                return
        if files < 15:
            msg = sendMessage(f"𝐂𝐥𝐨𝐧𝐢𝐧𝐠: <code>{link}</code>", context.bot, update)
            result, button = gd.clone(link)
            deleteMessage(context.bot, msg)
        else:
            drive = gdriveTools.GoogleDriveHelper(name)
            gid = ''.join(random.SystemRandom().choices(string.ascii_letters + string.digits, k=12))
            clone_status = CloneStatus(drive, size, update, gid)
            with download_dict_lock:
                download_dict[update.message.message_id] = clone_status
            sendStatusMessage(update, context.bot)
            result, button = drive.clone(link)
            with download_dict_lock:
                del download_dict[update.message.message_id]
                count = len(download_dict)
            try:
                if count == 0:
                    Interval[0].cancel()
                    del Interval[0]
                    delete_all_messages()
                else:
                    update_all_messages()
            except IndexError:
                pass
        if update.message.from_user.username:
            uname = f'@{update.message.from_user.username}'
        else:
            uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
        if uname is not None:
            cc = f'\n\ncc: {uname}'
            men = f'{uname} '
        if button in ("cancelled", ""):
            sendMessage(men + result, context.bot, update)
        else:
            sendMarkup(result + cc, context.bot, update, button)
    else:
        sendMessage('𝐏𝐫𝐨𝐯𝐢𝐝𝐞 𝐆-𝐃𝐫𝐢𝐯𝐞 𝐒𝐡𝐚𝐫𝐞𝐚𝐛𝐥𝐞 𝐋𝐢𝐧𝐤 𝐭𝐨 𝐂𝐥𝐨𝐧𝐞.', context.bot, update)

clone_handler = CommandHandler(BotCommands.CloneCommand, cloneNode, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(clone_handler)
