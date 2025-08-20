# 创建多份配置文件

在此之前，如果想让软件同时以不同的配置打开多个，只能通过整个将软件复制复制多份才能实现，这会浪费很多空间。

近期，对此进行了优化，可以让软件读取指定目录的配置文件，从而只需在运行时指定使用的配置文件目录，即可使用不同的配置文件。

方法是：

1. 为主程序创建快捷方式

    ![img](https://image.lunatranslator.org/zh/multiconfigs.png)

1. 修改快捷方式的属性->目标，在最后添加` --userconfig=XXXX`，其中，将`XXXX`替换为你想使用作为新的配置项的文件夹的名字。然后使用这个快捷键方式启动软件即可。

    如果`XXXX`是一个不存在的文件夹，那么会使用默认设置启动软件，并创建这个文件夹。

    如果`XXXX`是一个已经存在的文件夹，那么会使用这个文件夹中的配置文件启动软件。你可以复制旧的userconfig文件夹，然后指定`XXXX`为复制的文件夹的名字，这样就可以从之前的配置之上，分叉出新的配置。

    ![img](https://image.lunatranslator.org/zh/multiconfigs2.png)

    ![img](https://image.lunatranslator.org/zh/multiconfigs3.png)
