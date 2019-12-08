# RSD

## mysql setup for ubuntu[$ == ShellCmd, > == sqlCmd]

__1: install mysql-server__
```
    sudo apt-get update
    sudo apt-get install mysql-server
```

__2: start mysql and login to the mysql and go through the installation. Make sure not to install password verification addon.__
```
$   sudo systemctl start mysql
$   mysql -u root -p
```

__3: Create the db rsd2018:__
```
>   CREATE DATABASE rsd2018
```

__4: Grant priviliges to the rsd user which is used in the python file:__
```
>   GRANT ALL PRIVILEGES ON *.* TO 'rsd'@'localhost' IDENTIFIED BY 'rsd2018';
```

__5: Login as rsd and use rsd2018 as password:__
```
>   mysql -u rsd -p
```

__6: Source the rsd_2019_app_public to setup the database:__
```
>   source /home/kasper/Downloads/rsd_2019_app_public.py
```

__7: You should now be able to run the python script:__
```
$   python3 rsd_2019_app_public.py
```
## Install picamera
https://picamera.readthedocs.io/en/release-1.13/
install:
```
    sudo apt-get install python3-picamera
```

## Opencv Setup 
install:
```
    sudo apt-get install python3-opencv
```
Check that is was installed correctly by running "python" and then import cv:
```
    import cv2 as cv
    print(cv.__version__)
```

## PyModbus
__Install:__
```
    pip3 install -U pymodbus
```

__Dependencies:__

*Twisted*:
```
    pip3 install twisted
```

## Making a bash script run when pi starts:

https://www.instructables.com/id/Raspberry-Pi-Launch-Python-script-on-startup/

__References:__
https://pymodbus.readthedocs.io/en/latest/index.html
https://twistedmatrix.com/trac/
