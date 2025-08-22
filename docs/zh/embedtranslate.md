# 内嵌翻译

## 使用方法

::: danger
首先，不是所有游戏都支持内嵌。其次，内嵌有一定可能会导致游戏崩溃
:::

::: details 如果选择文本中没有内嵌这一行，就说明不支持内嵌 
![img](https://image.lunatranslator.org/zh/embed/noembed.png) 
![img](https://image.lunatranslator.org/zh/embed/someembed.png) 
:::

对于支持内嵌的游戏，选择支持内嵌的文本条目，激活内嵌即可

![img](https://image.lunatranslator.org/zh/embed/select.png)

对于支持内嵌的条目，**显示**和**内嵌**可以随意选择是否同时激活。当同时激活时，既会在游戏中嵌入翻译，也会在软件窗口中显示更多翻译；若只激活内嵌，则只会在游戏中显示嵌入的翻译，软件窗口则不会显示任何内容。

当开始内嵌翻译后，经常会出现乱码的情况。游戏乱码一般会是**字符集**和**字体**两种问题。对于英文游戏，通常是因为游戏缺少中文**字体**导致的，例如：

![img](https://image.lunatranslator.org/zh/embed/luanma.png)

这时，你需要激活**修改游戏字体**，并选择一个适当的字体，以显示中文字符

![img](https://image.lunatranslator.org/zh/embed/ziti.png)

修改完毕字体后，中文可以正确的显示了：

![img](https://image.lunatranslator.org/zh/embed/okembed.png)

对于许多古早日本galgame，他们使用自己内置的shift-jis字符集处理，无法正确处理中文字符，可以尝试**将汉字转换成繁体/日式汉字**，减少乱码的出现。

对于一些较新的游戏引擎和大部分英文游戏，一般使用utf-8或utf-16等Unicode字符集（如**KiriKiri**，**Renpy**，**TyranoScript**，**RPGMakerMV**等），即使出现乱码一般也是字体的问题，而不是字符集的问题。

![img](https://image.lunatranslator.org/zh/embed/fanti.png)

取消这一设置后，可以正常显示简体中文了。但对于一些无法正常显示简体中文的游戏，可以尝试激活这一选项来看看能不能正常显示。

![img](https://image.lunatranslator.org/zh/embed/good.png)

## 内嵌翻译设置

1. #### 显示模式

    ![img](https://image.lunatranslator.org/zh/embed/keeporigin.png)

    由于游戏能显示的文本行数的限制，所以默认没有在翻译和原文中间添加换行。如果确定可以容纳，可以通过在**翻译优化**->**翻译结果修正**中添加一条正则来在翻译前面添加一个换行来实现。

    ![img](https://image.lunatranslator.org/zh/embed/addspace.png)

1. #### 翻译等待时间

    内嵌翻译的原理是在游戏显示文本前，在某个函数中停住游戏，把其中要显示的文本发送给翻译器，等待到翻译后把文本内存修改成翻译的文本，然后让游戏继续运行来显示翻译。因此**当使用的翻译速度较慢时，是一定会导致游戏卡顿的**。可以通过限制等待的时间，来避免翻译过慢导致长时间卡顿。

1. #### 将汉字转换成繁体/日式汉字

    略

1. #### 限制每行字数

    有时某些游戏每行能显示的字符数是有限的，超出长度的内容会显示到文本框右边的更外边而无法显示。可以通过这一设置来手动分行来避免这一情况。

    ![img](https://image.lunatranslator.org/zh/embed/limitlength.png)

1. #### 修改游戏字体

    略

1. #### 内嵌安全性检查

    对于Renpy等游戏，提取的文本经常会包括`{` `}` `[` `]`等语法元素的字符，如果翻译源没有正确处理这些内容导致破坏了语法，会导致游戏崩溃。因此软件默认会通过正则匹配来**跳过翻译**某些可能会导致游戏崩溃的字符组合。如果不担心游戏崩溃，可以取消这一设置，或者手动更换一些更细粒度的正则匹配来减少不必要的跳过。

    ![img](https://image.lunatranslator.org/zh/embed/safeskip.png)
    
1. #### 清除游戏内显示的文字

    激活该选项后，游戏内要显示内嵌文本处的内容将被清空。

    该选项可能满足以下需要：

    1. 有时，内嵌翻译有无法解决的字符编码和字体无法显示的问题。开启该选项，然后将软件窗口覆盖到原本游戏中显示文字的地方，可以伪装成内嵌翻译的样子。

    1. 有时，我们并不是想要进行内嵌翻译，而是使用外挂翻译时，有可能觉得将窗口放在文字区会和原文本重叠，放在其他地方会遮挡画面。
    
    1. 有时，我们仅想要用来学习日语，然后游戏文本没有对文字加注音或双语对照的功能。
