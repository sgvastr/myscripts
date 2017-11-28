import os
import configparser

path = "C:\\Users\\1\\Desktop\\2\\"
for file in os.listdir(path):
    config = configparser.ConfigParser(strict=False)
    config.sections()
    config.read(path+file)
    pcname = config["Имя компьютера"]["Имя NetBIOS|Имя компьютера"]
    soft = set()
    for f in config["Установленные программы"]:
        if f.find("установленные программы") != -1:
            s = config["Установленные программы"][f]
            soft.add(s)

    with open("C:\\Users\\1\\Desktop\\result.txt", "a") as res:
        for s in soft:
            res.write(pcname+";"+s+"\r\n")