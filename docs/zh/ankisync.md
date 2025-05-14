# Anki本地同步服务器

使用LunaTranslator内置的制卡模板在添加过多卡片时，有超出anki.web同步体积的可能。这时可以选择使用anki内置的本地同步服务器功能。

1. ## 开启本地同步服务器

    在cmd中，运行以下代码：

    ```bat
    set SYNC_PORT=8080
    set SYNC_USER1=user:pass
    set MAX_SYNC_PAYLOAD_MEGS=10000000
    %LOCALAPPDATA%\Programs\Anki\anki.exe --syncserver
    pause
    ```

    ::: tip
    其中，`8080`是同步服务器占用的默认端口号。如果运行失败，可能是端口号被占用，修改成其他端口号，**修改后后续也应做出对应的修改**。

    `user:pass`分别是自定义的用户名和密码，并随时可以更改，**后续登录时都需要填写这个内容**。

    `%LOCALAPPDATA%\Programs\Anki\anki.exe`是anki的路径，这里是默认的安装路径，如果你的电脑上的anki路径不是这个，那么自行修改即可。
    :::

    为了更方便的运行，可以将这段代码保存为`XXX.bat`，即可双击运行。

    ::: details 启动成功&失败
    启动成功
    ![img](https://image.lunatranslator.org/zh/anki/startsuccess.png)

    启动失败，可能是端口号被占用
    ![img](https://image.lunatranslator.org/zh/anki/startfailed.png)
    :::
    
    ::: details 隐藏控制台窗口在后台运行

    如果想要隐藏控制台窗口在后台运行同步服务器，可以再创建一个`YYY.vbs`，其中写入以下内容：

    ```vbs
    Set objShell = WScript.CreateObject("WScript.Shell")
    objShell.Run "XXX.bat", 0, False
    ```
    其中，`YYY.vbs`中的`XXX.bat`必须和保存的bat文件名相同。
    
    双击`YYY.vbs`即可后台运行，但会看不到错误信息，建议先用bat版本调式好后再用vbs运行。
    :::

1. ## 将电脑上的数据上传到本地同步服务器

    首次启动本地同步服务器后，其中内容是空白的，需要首先将电脑上的数据上传到本地同步服务器之后，手机上才能从本地服务器下载数据。

    1. 首先，在`设置`->`同步`中修改`自托管同步服务器`，修改为`http://127.0.0.1:8080`。如果前面修改了端口号(SYNC_PORT)，则这里8080也要修改为同样的值。

        ![img](https://image.lunatranslator.org/zh/anki/ankiset1.png)

    1. 关闭anki，然后重新打开，使上述修改生效

    1. 使用前面设置的用户名和密码(`user:pass`)进行登录，然后按照anki的提示同步数据到本地同步服务器即可。
        ::: details 图例
        ![img](https://image.lunatranslator.org/zh/anki/login.png)
        :::

1. ## 在手机上从本地同步服务器下载数据

    1. 确保手机和电脑处于同一个局域网内，例如链接到同一个路由器等。

        如果同时连接到校园网等，可能仍无法通信，可以在电脑上开启移动热点，然后让手机连接电脑的热点。

    1. 获取电脑的ip地址。在cmd中输入以下内容，可以获取可能的ip地址。若有多个候选的ip地址，在后续中对其一一进行测试即可。
        ```bat
        for /f "tokens=2 delims=:" %A in ('ipconfig ^| findstr /i "IPv4"') do @for /f "tokens=*" %B in ("%A") do @echo %B
        ```

    1. 在`设置`->`同步`中修改`自定义同步服务器`。同步地址为`http://电脑的ip地址:8080`，其中电脑的ip地址为上一步获取的ip地址，8080为前面设置端口号(SYNC_PORT)。
        ::: details 图例
        ![img](https://image.lunatranslator.org/zh/anki/ankiandr1.jpg)
    
        ![img](https://image.lunatranslator.org/zh/anki/ankiandr2.jpg)
        :::

    1. 设置好后，使用前面设置的用户名和密码(`user:pass`)进行登录，然后按照anki的提示同步数据即可。

        如果同步失败，可能是前面设置的ip地址错误，修改ip地址后，再次测试登录即可。
        ::: details 图例
        ![img](https://image.lunatranslator.org/zh/anki/ankiandr3.jpg)
        :::