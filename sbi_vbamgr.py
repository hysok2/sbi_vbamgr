from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import sys
import toml
import datetime
import PySimpleGUI as sg
import copy


class virtual_accounts:
    def __init__(self,title):
        # load vba
        with open(title) as f:
            vba = toml.load(f)
            self.date = vba['date']
            self.names = vba['vba']['names']
            self.assets_list = vba['vba']['assets_list']

    def add_asset(self,aname,name,num):
        for i in range(len(self.assets_list[self.names.index(aname)])):
            if self.assets_list[self.names.index(aname)][i][0] == name:
                self.assets_list[self.names.index(aname)][i]= \
                    [name,str(round(float(self.assets_list[self.names.index(aname)][i][1])+num,2))]
                return        
        self.assets_list[self.names.index(aname)].append([name,str(num)])

    def add_name(self,aname):
        self.names.append(aname)
        self.assets_list.append([])

    def get_all_assets_list(self,assets_list):
        dc = {}
        for i in range(len(assets_list)):
            for j in range(len(assets_list[i])):
                if assets_list[i][j][0] in dc:
                    dc[assets_list[i][j][0]]=round(dc[assets_list[i][j][0]]+float(assets_list[i][j][1]),2)
                else:
                    dc[assets_list[i][j][0]]=float(assets_list[i][j][1])
        return(dc)

    def check_eq(self,assets_list):
        dc_input = self.get_all_assets_list(assets_list)
        dc_va = self.get_all_assets_list(self.assets_list)
        if len(dc_input) != len(dc_va):
            return(False)
        for k in dc_input:
            if not (k in dc_va):
                return(False)
            if dc_input[k]!=dc_va[k]:
                return(False)
        return(True)

    def output_toml(self,file):
        with open(file,"w") as f:
            dc = {
                'date' : datetime.date.today(),
                'vba' : {
                    'names' : self.names,
                    'assets_list' : self.assets_list,
                },
            }
            toml.dump(dc,f)
    
    def mk_assets_summary(self,assets_list):
        dc = {}
        dc_input = {}
        for i in range(len(assets_list)):
            dc_input.update(assets_list[i].mk_dict())
        for i in range(len(self.names)):
            a = assets()
            for j in range(len(self.assets_list[i])):
                a.add(self.assets_list[i][j][0],self.assets_list[i][j][1], \
                    round(dc_input[self.assets_list[i][j][0]][1] \
                    *(float(self.assets_list[i][j][1])/dc_input[self.assets_list[i][j][0]][0])))
            dc[self.names[i]] = a
        return(dc)

    def show_assets_summary(self,assets_list):
        summary = self.mk_assets_summary(assets_list)

        layout = []
        assets_total = 0

        for k in summary:
            onecol = []
            for i in range(len(summary[k].assets_list)):
                onecol.append([sg.Text(f'{summary[k].assets_list[i][0]} : {summary[k].assets_list[i][1]} : {summary[k].assets_list[i][2]} ???')])
            onecol.append([sg.Text(f'----------\n?????? : {summary[k].total//1} ???')])
            assets_total+=round(summary[k].total)
            layout.append([sg.Frame(k, onecol)])
        
        layout.append([sg.Frame('??????',[[sg.Text(f'{assets_total} ???')]])])
        layout.append([sg.Button('??????')])

        window = sg.Window('??????', layout)

        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == '??????':
                break

        window.close()
    
    def mk_and_classify_diff(self,assets_list):

        al = []
        for i in range(len(assets_list)):
            al.append(assets_list[i].assets_list)
        
        if not (self.check_eq(al)):
            dc_va = self.get_all_assets_list(self.assets_list)
            dc_new = self.get_all_assets_list(al)

            dc_all_keys = {}
            dc_all_keys.update(dc_va)
            dc_all_keys.update(dc_new)

            # diff : list [str,float]
            diff = []

            for k in dc_all_keys:
                if (k in dc_va) and (k in dc_new):
                    if dc_new[k] != dc_va[k]:
                        diff.append([k,round(dc_new[k]-dc_va[k],2)])
                elif (k in dc_va) and (not (k in dc_new)):
                    diff.append([k,-dc_va[k]])
                elif (not (k in dc_va)) and (k in dc_new):
                    diff.append([k,dc_new[k]])

            # ????????????????????????????????????
            original_names=copy.deepcopy(self.names)
            original_al=copy.deepcopy(self.assets_list)
            original_diff=copy.deepcopy(diff)

            window_reconst_loop=True

            while window_reconst_loop:

                summary = self.mk_assets_summary(assets_list)

                layout = []
                assets_total = 0

                for k in summary:
                    onecol = []
                    for i in range(len(summary[k].assets_list)):
                        onecol.append([sg.Text(f'{summary[k].assets_list[i][0]} : {summary[k].assets_list[i][1]} : {summary[k].assets_list[i][2]} ???')])
                    onecol.append([sg.Text(f'----------\n?????? : {summary[k].total//1} ???')])
                    assets_total+=round(summary[k].total)
                    layout.append([sg.Frame(k, onecol)])

                layout.append([sg.Text("??????????????? : "), sg.InputText(key="-bname-"),sg.Button('??????????????????')])
                
                onecol = []
                radio_dc = {}
                for i in range(len(self.names)):
                    radio_dc[f'{i}']=self.names[i]
                radio_dc[f'{len(self.names)}']='?????????????????????'
                
                for i in range(len(diff)):
                    oneline=[]
                    oneline.append(sg.Text(f'{diff[i][0]} : {diff[i][1]} : '))
                    if i==0:
                        for item in radio_dc.items():
                            oneline.append(sg.Radio(item[1], key=f'{item[0]}+g{i}', group_id=f'g{i}'))
                        oneline.append(sg.Text(': ???????????????'))
                        oneline.append(sg.InputText(key='-amount-'))
                    onecol.append(oneline)
                    if i==0:
                        onecol.append([sg.Button('???????????????')])

                layout.append([sg.Frame('**??????**',onecol)])
                
                # layout.append([sg.Frame('??????',[[sg.Text(f'{assets_total} ???')]])])
                layout.append([sg.Button('???????????????'),sg.Button('??????')])

                window = sg.Window('????????????????????????????????????', layout)

                while True:
                    event, values = window.read()
                    if event == sg.WIN_CLOSED or event == '??????':
                        window_reconst_loop=False
                        break
                    if event == '???????????????':
                        self.names=copy.deepcopy(original_names)
                        self.assets_list=copy.deepcopy(original_al)
                        diff=copy.deepcopy(original_diff)
                        break
                    if event == '??????????????????' and values["-bname-"]!='' and not(values["-bname-"] in summary):
                        self.add_name(values["-bname-"])
                        window["-bname-"].Update('')
                        break
                    if event == '???????????????' and len(diff)!=0:
                        # print(values)
                        for i in radio_dc:
                            if values[f'{i}+g0']:
                                if int(i)<len(self.names):
                                    self.add_asset(self.names[int(i)],diff[0][0],diff[0][1])
                                    del diff[0]
                                elif int(i)==len(self.names) and values['-amount-']!='':
                                    diff[0][1]=round(diff[0][1]-float(values['-amount-']),2)
                                    diff.append([diff[0][0],float(values['-amount-'])])
                                    window['-amount-'].Update('')
                                break
                        break

                window.close()


class assets:
    def __init__(self):
        self.assets_list = []
        self.total = 0
    def add(self,name,num,val):
        self.assets_list.append([name,num,val])
        self.total += val
    def mk_dict(self):
        dc = {}
        for i in range(len(self.assets_list)):
            dc[self.assets_list[i][0]]=[self.assets_list[i][1],self.assets_list[i][2]]
        return(dc)

def replace_nbsp_sp(str):
    return(str.replace('\u3000',' ').replace('\xa0',' '))

def get_yen_assets(driver):

    yen_assets = assets()

    # ?????????????????????
    driver.find_element(By.XPATH, "//*[@id='link02M']/ul/li[3]/a").click()
    driver.find_element(By.XPATH, \
        "/html/body/div[1]/table/tbody/tr/td[1]/table/tbody/tr[2]/td/table[1]/tbody/tr/td/form/table[2]/tbody/tr[1]/td[2]/table[4]/tbody/tr/td[3]/table[3]/tbody/tr/td/a[2]").click()

    # ???????????????
    soup = BeautifulSoup(driver.page_source.encode('utf-8'), "html.parser")
    table_data = soup.find_all("table", border="0", cellpadding="1", cellspacing="1", width="400")

    df = pd.read_html(str(table_data))
    for i in range(len(df)):
        for j in range(len(df[i])//2-1):
            yen_assets.add(replace_nbsp_sp(df[i].at[2*(j+1),0]),float(df[i].at[2*(j+1)+1,0]),int(df[i].at[2*(j+1)+1,3]))
    
    # ???????????????
    yen = float(driver.find_element(By.XPATH, \
        "/html/body/div[1]/table/tbody/tr/td[1]/table/tbody/tr[2]/td/table[1]/tbody/tr/td/form/table[2]/tbody/tr[1]/td[2]/table[4]/tbody/tr/td[1]/table[4]/tbody/tr[3]/td[2]/div/font").text.replace(',',''))
    yen_assets.add('??????(???)',yen,yen)
    
    yen_all_asset = float(driver.find_element(By.XPATH, \
        "/html/body/div[1]/table/tbody/tr/td[1]/table/tbody/tr[2]/td/table[1]/tbody/tr/td/form/table[2]/tbody/tr[1]/td[2]/table[4]/tbody/tr/td[1]/table[4]/tbody/tr[8]/td[2]/div/b").text.replace(',',''))

    if (yen_assets.total != yen_all_asset):
        print("Error in get_yen_assets")
    
    return(yen_assets)

def get_dollar_assets(driver):

    dollar_assets = assets()

    # ??????????????????????????????
    driver.find_element(By.XPATH, "//*[@id='link02M']/ul/li[3]/a").click()
    driver.find_element(By.XPATH, "//*[@id='navi02P']/ul/li[2]/div/a").click()
    driver.find_element(By.XPATH, \
        "/html/body/div[1]/table[2]/tbody/tr/td[1]/table/tbody/tr/td[2]/table[2]/tbody/tr[1]/td[2]/table[5]/tbody/tr/td[3]/table[2]/tbody/tr/td[5]/a").click()

    # ???????????????
    soup = BeautifulSoup(driver.page_source.encode('utf-8'), "html.parser")
    table_data = soup.find_all("table", border="0", cellspacing="1", cellpadding="1", width="100%")

    df = pd.read_html(str(table_data))
    for i in range(len(df)):
        for j in range(len(df[i])//2):
            dollar_assets.add(replace_nbsp_sp(df[i].at[2*j+1,0]),float(df[i].at[2*j+1+1,0]),int(df[i].at[2*j+1+1,3])) 

    # ??????????????????
    dollar = float(driver.find_element(By.XPATH, \
        "/html/body/div[1]/table[2]/tbody/tr/td[1]/table/tbody/tr/td[2]/table[2]/tbody/tr[1]/td[2]/table[5]/tbody/tr/td[1]/form/table/tbody/tr[2]/td[3]").text.replace(',',''))
    yenusd = float(driver.find_element(By.XPATH, \
        "/html/body/div[1]/table[2]/tbody/tr/td[1]/table/tbody/tr/td[2]/table[2]/tbody/tr[1]/td[2]/table[5]/tbody/tr/td[1]/table[1]/tbody/tr[2]/td[2]").text.replace(',',''))
    dollar_assets.add('??????(??????)',dollar,round(dollar*yenusd))

    #print(yenusd)

    # ????????????????????????????????????
    dollar_all_asset = float(driver.find_element(By.XPATH, \
        "//*[@id='summary_USD']/td[3]/table/tbody/tr[2]/td[2]/b").text.replace(',',''))
    
    #if (dollar_assets.total != dollar_all_asset):
    #    print("Error in get_dollar_assets")
    #    print(dollar_all_asset)
    #    print(dollar_assets.total)

    return(dollar_assets)


if __name__ == "__main__":

    if (len(sys.argv)!=5):
        print('??????????????????????????????')
        print('python3 sbi_vbamgr.py sbi_user_id sbi_password input_vba_file output_vba_file')
        exit()
    
    # load data in sbi
    ## chrome driver????????????????????????
    options = Options()
    options.add_argument("-headless")
    options.add_argument("-no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    ## URL??????
    driver.get('https://site2.sbisec.co.jp/ETGate/')

    ## ????????????ID??????????????????????????????????????????????????????
    username = sys.argv[1]
    password = sys.argv[2]

    ## ????????????
    driver.find_element(By.NAME, "user_id").send_keys(username)
    driver.find_element(By.NAME,"user_password").send_keys(password)
    driver.find_element(By.NAME,"ACT_login").click()

    # ?????????????????????????????????
    da = get_dollar_assets(driver)
    ya = get_yen_assets(driver)

    driver.close()

    print("SBI?????????????????????????????????")

    # load data in vba
    ## ?????????vba????????????????????????????????????
    input_vba = sys.argv[3]
    output_vba = sys.argv[4]

    va = virtual_accounts(input_vba)

    print("?????????????????????????????????????????????")
    
    if(va.check_eq([ya.assets_list,da.assets_list])):
        va.show_assets_summary([ya,da])
    else:
        # ??????????????????
        va.mk_and_classify_diff([ya,da])
        va.show_assets_summary([ya,da])
    # ??????????????????
    va.output_toml(output_vba)
        

