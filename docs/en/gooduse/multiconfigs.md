# Creating Multiple Configuration Files

Previously, if you wanted to open the software with different configurations simultaneously, the only way was to duplicate the entire software, which wasted a lot of space.

Recently, this has been optimized. The software can now read configuration files from a specified directory, allowing you to use different configurations simply by specifying the configuration directory at runtime.

Here’s how:

1. Create a shortcut for the main program.

    ![img](https://image.lunatranslator.org/zh/multiconfigs.png)

1. Modify the shortcut’s Properties -> Target by adding ` --userconfig=XXXX` at the end, where `XXXX` is the name of the folder you want to use as the new configuration. Then, launch the software using this shortcut.

    If `XXXX` is a non-existent folder, the software will start with default settings and create this folder.

    If `XXXX` is an existing folder, the software will launch using the configuration files in that folder. You can copy the old userconfig folder and specify `XXXX` as the name of the copied folder, allowing you to fork a new configuration from the previous one.

    ![img](https://image.lunatranslator.org/zh/multiconfigs2.png)

    ![img](https://image.lunatranslator.org/zh/multiconfigs3.png)
