import os
import sys


def dir_content(start_dir ="C:\\", space="    "):
    print(space+"|----" + start_dir)
    space += "|    "
    try:
        for file_name in os.listdir(start_dir):
            if os.path.isfile(start_dir + file_name):
                try:
                    print(space + "|----"+file_name+"\t"+str(os.path.getsize(start_dir + file_name)))
                except:
                    print("Ошибка", sys.exc_info()[0])
            elif os.path.isdir(start_dir + file_name):
                dir_content(start_dir+file_name+"\\", space)
    except:
        print("Ошибка", sys.exc_info()[0])

dir_content()
