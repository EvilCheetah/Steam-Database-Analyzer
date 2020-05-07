#Shortcut URL for SteamDB
STEAMDB_APP_URL = 'https://steamdb.info/app/'

#JSON that contains all game IDs
STEAM_GAMES_LIST_JSON = 'https://api.steampowered.com/ISteamApps/GetAppList/v2'

#Browser header to go around bot check
USER_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0'}

#Calculated using IEEE-754 Floating Point Converter
#https://www.h-schmidt.net/FloatConverter/IEEE754.html
#Keeps the exact value in the memory
NA_CONST = -99999.765625

#App ID to get currency list for initialization
#In this case it is Half-Life
CURRENCY_INIT_APP_ID = 70