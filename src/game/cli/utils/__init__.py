import os

class Cli_Utils:
  def clear():
    os.system('cls' if os.name=='nt' else 'clear')

cli_utils = Cli_Utils()
