import colorama  #type:ignore

colorama.init()

# Convenient colour constants...
W = colorama.Style.RESET_ALL  # bright white has problems in some terminals (and in light themes)
R = colorama.Style.BRIGHT + colorama.Fore.RED
Y = colorama.Style.BRIGHT + colorama.Fore.YELLOW
C = colorama.Style.BRIGHT + colorama.Fore.CYAN
G = colorama.Style.BRIGHT + colorama.Fore.GREEN
Gy = colorama.Style.DIM + colorama.Fore.WHITE
DY = colorama.Style.DIM + colorama.Fore.YELLOW
_ = colorama.Style.RESET_ALL
