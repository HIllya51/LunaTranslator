
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

# Temporarily Using OCR in HOOK Mode  

Sometimes HOOK mode doesn't capture text in game menus, options, etc., and switching to OCR mode for recognition and then back to HOOK mode is troublesome.  

In fact, there's already a built-in solution for this situation: using the "Perform OCR Once" button <i class="fa fa-crop"></i> or a shortcut key.  

This button shares the same default icon as the button for selecting recognition areas in OCR mode, and it is now enabled by default.  

After selecting an area with this button, it performs OCR only once, then exits OCR and seamlessly continues using HOOK for automatic text extraction, perfectly addressing some gaps in HOOK mode.  

**Due to this button's icon, many users who originally wanted to use OCR mistakenly think this is the OCR button and end up using it while still in HOOK mode. After selecting an area, automatic translation doesn't occur. In reality, the OCR mode button only appears after switching to OCR mode.**  

For fixed-position options where you don't want to reselect the area each time, you can use the "Perform OCR Again" button <i class="fa fa-spinner"></i> or a shortcut key to perform OCR using the previously selected area.  
