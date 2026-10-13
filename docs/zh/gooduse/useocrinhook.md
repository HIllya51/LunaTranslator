
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css">

<style>
    i{
        color:blue;
        width:20px;
    }
    .fa-icon {
  visibility: hidden;
}
.btnstatus2{
    color:deeppink;
}
</style>

# 在HOOK模式下临时使用OCR

有时，HOOK模式不会捕获游戏中的菜单、选择肢等文字，而为此切换到OCR模式进行识别再切换回HOOK模式又很麻烦。

其实，对于这种情况，早已有了内置的解决方案，即使用`进行一次OCR`按钮<i class="fa fa-crop"></i>或快捷键。

这个按钮和OCR模式下选取识别范围的按钮的默认图标是相同的，并且现在已经默认激活使用该按钮。

这个按钮在选取完范围后，只会进行一次OCR，然后退出OCR，然后无缝继续使用HOOK自动提取文本，完美解决了HOOK模式的一些缺漏。



