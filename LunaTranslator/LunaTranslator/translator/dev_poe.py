 
 
from urllib.parse import quote
from translator.basetranslator_dev import basetransdev
import time
 
class TS(basetransdev): 
    target_url='https://poe.com/'
    def inittranslator(self):
        list(self.translate('Please help me translate the following text into: '+self.tgtlang))
    def langmap(self):
        return {'zh': 'Simplified Chinese', 'ja': 'Japanese', 'en': 'English', 'ru': 'Russian', 'es': 'Spanish', 'ko': 'Korean', 'fr': 'French', 'cht': 'Traditional Chinese', 'vi': 'Vietnamese', 'tr': 'Turkish', 'pl': 'Polish', 'uk': 'Ukrainian', 'it': 'Italian', 'ar': 'Arabic', 'th': 'Thai'}
    def translate(self,content):
        try:
            self.num=self.Runtime_evaluate('''document.querySelector("#__next > div > div.AnnouncementWrapper_container__Z51yh > div.SidebarLayout_layoutWrapper__mPYi4.SidebarLayout_layoutWrapperOverflow__0hyZ4 > main > div > div > div > div.InfiniteScroll_container__PHsd4.ChatMessagesView_infiniteScroll__vk3VX").children.length''')['result']['value']
        except:
            self.num=2
        print(self.num)
        self.Runtime_evaluate('''document.querySelector("#__next > div > div.AnnouncementWrapper_container__Z51yh > div.SidebarLayout_layoutWrapper__mPYi4.SidebarLayout_layoutWrapperOverflow__0hyZ4 > main > div > div > div > div.ChatHomeMain_container__l4uRf > div.ChatHomeMain_inputContainer__9mgRh > div > div > textarea").click()''')
        self.Runtime_evaluate('''document.querySelector("#__next > div > div.AnnouncementWrapper_container__Z51yh > div.SidebarLayout_layoutWrapper__mPYi4.SidebarLayout_layoutWrapperOverflow__0hyZ4 > main > div > div > div > footer > div > div > div > textarea")''')
        self.send_keys(content)
        self.Runtime_evaluate('''document.querySelector("#__next > div > div.AnnouncementWrapper_container__Z51yh > div.SidebarLayout_layoutWrapper__mPYi4.SidebarLayout_layoutWrapperOverflow__0hyZ4 > main > div > div > div > div.ChatHomeMain_container__l4uRf > div.ChatHomeMain_inputContainer__9mgRh > div > button.Button_buttonBase__Bv9Vx.Button_primary__6UIn0.ChatMessageSendButton_sendButton__4ZyI4.ChatMessageInputContainer_sendButton__dBjTt").click()''')
        self.Runtime_evaluate('''document.querySelector("#__next > div > div.AnnouncementWrapper_container__Z51yh > div.SidebarLayout_layoutWrapper__mPYi4.SidebarLayout_layoutWrapperOverflow__0hyZ4 > main > div > div > div > footer > div > div > button.Button_buttonBase__Bv9Vx.Button_primary__6UIn0.ChatMessageSendButton_sendButton__4ZyI4.ChatMessageInputContainer_sendButton__dBjTt").click()''')
        if self.config['流式输出']==False:
            self.wait_for_result('''document.querySelector("#__next > div > div.AnnouncementWrapper_container__Z51yh > div.SidebarLayout_layoutWrapper__mPYi4.SidebarLayout_layoutWrapperOverflow__0hyZ4 > main > div > div > div > div.InfiniteScroll_container__PHsd4.ChatMessagesView_infiniteScroll__vk3VX > div:nth-child({}) > section.ChatMessageActionBar_actionBar__gyeEs").innerHTML'''.format(self.num+1))
            yield self.wait_for_result('''document.querySelector("#__next > div > div.AnnouncementWrapper_container__Z51yh > div.SidebarLayout_layoutWrapper__mPYi4.SidebarLayout_layoutWrapperOverflow__0hyZ4 > main > div > div > div > div.InfiniteScroll_container__PHsd4.ChatMessagesView_infiniteScroll__vk3VX > div:nth-child({}) > div:nth-child(2) > div.ChatMessage_messageRow__DHlnq").textContent'''.format(self.num+1))
        else:
            currtext=''
            while True:
                time.sleep(0.1)
                newcurr=self.wait_for_result('''document.querySelector("#__next > div > div.AnnouncementWrapper_container__Z51yh > div.SidebarLayout_layoutWrapper__mPYi4.SidebarLayout_layoutWrapperOverflow__0hyZ4 > main > div > div > div > div.InfiniteScroll_container__PHsd4.ChatMessagesView_infiniteScroll__vk3VX > div:nth-child({}) > div:nth-child(2) > div.ChatMessage_messageRow__DHlnq").textContent'''.format(self.num+1))
                if newcurr=='...':continue
                yield newcurr[len(currtext):]
                currtext=newcurr
                if (self.Runtime_evaluate('''document.querySelector("#__next > div > div.AnnouncementWrapper_container__Z51yh > div.SidebarLayout_layoutWrapper__mPYi4.SidebarLayout_layoutWrapperOverflow__0hyZ4 > main > div > div > div > div.InfiniteScroll_container__PHsd4.ChatMessagesView_infiniteScroll__vk3VX > div:nth-child({}) > section.ChatMessageActionBar_actionBar__gyeEs")'''.format(self.num+1)))['result']['subtype']=='node':
                    newcurr=self.wait_for_result('''document.querySelector("#__next > div > div.AnnouncementWrapper_container__Z51yh > div.SidebarLayout_layoutWrapper__mPYi4.SidebarLayout_layoutWrapperOverflow__0hyZ4 > main > div > div > div > div.InfiniteScroll_container__PHsd4.ChatMessagesView_infiniteScroll__vk3VX > div:nth-child({}) > div:nth-child(2) > div.ChatMessage_messageRow__DHlnq").textContent'''.format(self.num+1))
                    yield newcurr[len(currtext):]
                    break