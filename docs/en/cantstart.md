## Can't Start the Software?

1. #### Missing Important Components

  <img src="https://image.lunatranslator.org/zh/cantstart/2.jpg"> 

  Solution: Close antivirus software. If it cannot be closed (such as Windows Defender), add it to the trust list and then re-download.

  Note: To achieve HOOK extraction of game text, it is necessary to inject Dll into the game. Files such as shareddllproxy32.exe/LunaHost32.dll implement this, and therefore are particularly likely to be considered as viruses. The software is currently automatically built by [Github Actions](https://github.com/HIllya51/LunaTranslator/actions). Unless the Github server is infected, it is impossible to contain viruses, so it can be safely added to the trust list.

  <details>
    <summary>For Windows Defender, the method is: “Virus & threat protection” -> “Exclusions” -> “Add or remove exclusions” -> “Add an exclusion” -> “Folder”, add Luna's folder to it</summary>
    <img src="https://image.lunatranslator.org/zh/cantstart/4.png"> 
    <img src="https://image.lunatranslator.org/zh/cantstart/3.png"> 
  </details>

1. #### Error/PermissionError

  If the software is placed in special folders such as `Program Files`, it may not have read and write permissions. Please run with administrator privileges.

  <img src="https://image.lunatranslator.org/zh/cantstart/6.png"  width=400>
