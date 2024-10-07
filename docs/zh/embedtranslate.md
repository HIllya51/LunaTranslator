## 如何使用内嵌翻译？

> 首先，不是所有游戏都支持内嵌。其次，内嵌有一定可能会导致游戏崩溃


<details>
  <summary>如果选择文本中没有内嵌这一行，就说明不支持内嵌</summary>
  <img src="https://image.lunatranslator.org/zh/embed/noembed.png">
  <img src="https://image.lunatranslator.org/zh/embed/someembed.png">
</details>

对于支持内嵌的游戏，选择支持内嵌的文本条目，激活内嵌即可

![img](https://image.lunatranslator.org/zh/embed/select.png)

对于支持内嵌的条目，**显示**和**内嵌**可以随意选择是否同时激活。当同时激活时，既会在游戏中嵌入翻译，也会在软件窗口中显示更多翻译；若只激活内嵌，则只会在游戏中显示嵌入的翻译，软件窗口则不会显示任何内容。

当开始内嵌翻译后，经常会出现乱码的情况。游戏乱码一般会是**字符集**和**字体**两种问题。对于英文游戏，通常是因为游戏缺少中文**字体**导致的，例如：

![img](https://image.lunatranslator.org/zh/embed/luanma.png)

这时，你需要在**内嵌设置**中，激活**修改游戏字体**，并选择一个适当的字体，以显示中文字符

![img](https://image.lunatranslator.org/zh/embed/ziti.png)

修改完毕字体后，中文可以正确的显示了：

![img](https://image.lunatranslator.org/zh/embed/okembed.png)

但会发现内嵌的文字是繁体中文，可以在**内嵌设置**中取消**将汉字转换成繁体/日式汉字**。

>这是因为**对于许多古早日本galgame，他们使用自己内置的shift-jis字符集处理，无法正确处理中文字符，通过将汉字翻译转换成型近的繁体/日式汉字，可以减少乱码的出现，因此默认是会自动将简体中文转换成繁体中文的**。如果取消这一设置后乱码，请恢复这一设置。
对于一些较新的游戏引擎和大部分英文游戏，一般使用utf-8或utf-16等Unicode字符集（如**KiriKiri**，**Renpy**，**TyranoScript**，**RPGMakerMV**等），即使出现乱码一般也是字体的问题，而不是字符集的问题。

![img](https://image.lunatranslator.org/zh/embed/fanti.png)

取消这一设置后，可以正常显示简体中文了。但对于一些无法正常显示简体中文的游戏，可以尝试激活这一选择来看看能不能正常显示。

![img](https://image.lunatranslator.org/zh/embed/good.png)

** **

## 一些其他设置

**1. 保留原文** 

![img](https://image.lunatranslator.org/zh/embed/keeporigin.png)

由于游戏能显示的文本行数的限制，所以默认没有在翻译和原文中间添加换行。如果确定可以容纳，可以通过在**翻译优化**->**翻译结果修正**中添加一条正则来在翻译前面添加一个换行来实现。

![img](https://image.lunatranslator.org/zh/embed/addspace.png)

**2. 翻译等待时间**

内嵌翻译的原理是在游戏显示文本前，在某个函数中停住游戏，把其中要显示的文本发送给翻译器，等待到翻译后把文本内存修改从翻译的文本，然后让游戏继续运行来显示翻译。因此**当使用的翻译速度较慢时，是一定会导致游戏卡顿的**。可以通过限制等待的时间，来避免翻译过慢导致长时间卡顿。

**3. 使用指定翻译器**

当激活多个翻译源时，可以选择内嵌某个指定的效果最好的翻译。若不激活，或指定的翻译器未被激活，则会使用速度最快的翻译，来减少游戏卡顿

**4. 将汉字转换成繁体/日式汉字**

略

**5. 在重叠显示的字间插入空格**

对于SiglusEngine等部分古早日本游戏引擎，无法正确处理中文字符的宽度，会把中文字符按照英文字符的宽度来显示，导致内嵌的中文出现字符之间重叠。可以尝试调整这一设置来解决这一问题。

**6. 限制每行字数**

有时某些游戏每行能显示的字符数是有限的，超出长度的内容会显示到文本框右边的更外边而无法显示。可以通过这一设置来手动分行来避免这一情况。

![img](https://image.lunatranslator.org/zh/embed/limitlength.png)

**7. 修改游戏字体**

略

**8. 内嵌安全性检查**

对于Renpy等游戏，提取的文本经常会包括`{` `}` `[` `]`等语法元素的字符，如果翻译源没有正确处理这些内容导致破坏了语法，会导致游戏崩溃。因此软件默认会通过正则匹配来**跳过翻译**某些可能会导致游戏的字符组合。如果不担心游戏崩溃，可以取消这一设置，或者手动更换一些更细粒度的正则匹配来减少不必要的跳过。

![img](https://image.lunatranslator.org/zh/embed/safeskip.png)