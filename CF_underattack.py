import requests
import time
from fail import Fail
from cfapikey import CfApiKey
from CF_geoip import SwitchGeo

account, QQ, QQ2 = CfApiKey()

while True:
    # 存放輸入的domain
    domain = {}

    #選擇要開啟防禦模式or允許國家
    while True:
        choice = input(
            '輸入1設定 Under_Attack_Mode\n'
            '         Bot_Fight_Mode\n'
            '         HTTP_DDoS_attack_protection\n'
            '\n'
            '輸入2設定 地區限制\n'
            '\n'
            )
        choice = choice.strip(' \t\n\r')

        if choice == '1' or choice == '2':
            end = 1
            break
        
        else:
            print('輸入錯誤')
            end = input('按enter繼續，或按0離開：')
            print()
            if end == '0':
                break

    if end == '0':
        break

    #選擇帳號
    while True:
        select = input(
            '輸入0為自家域名(network@368media.com帳號),\n'
            '輸入1為自家域名(network2@368media.com帳號),\n'
            '輸入2為客戶域名(whitelabel@368media.com帳號),\n'
            '輸入3為客戶域名(whitelabel2@368media.com帳號),\n'
            '輸入4為客戶域名(whitelabel3@368media.com帳號),\n'
            '輸入5為客戶域名(whitelabel4@368media.com帳號),\n'
            '輸入6為客戶域名(whitelabel5@368media.com帳號),\n'
            '輸入7為客戶域名(whitelabel6@368media.com帳號),\n'
        )
        select = select.strip(' \t\n\r')
        try:
            a = QQ[select]
            end = 1
            break
        except:
            print('輸入錯誤')
            end = input('按enter繼續，或按0離開：')
            print()
            if end == '0':
                break
    
    if end == '0':
        break


    #設定 headers
    header = {
        'x-auth-email': a,
        'X-Auth-Key': account[a],    
        'Content-Type': 'application/json'
    }


    #輸入域名
    print('請輸入主域名domain:\n輸入0結束輸入')
    while True:
        temp = input()
        temp = str(temp.strip(' \t\n\r'))
        # 跳過空的行
        if temp == '':
            pass
        elif temp == '0':
            break
        else:
            domain[temp] = None





    if choice == '1':
    
        while True:
            switch = input('開啟防禦請輸入 1，關閉請輸入 2 : ')
            switch = switch.strip(' \t\n\r')
            
            if switch == '1' or switch == '2':
                end = 1
                break
            
            else:
                print('輸入錯誤')
                end = input('按enter繼續，或按0離開：')
                print()
                if end == '0':
                    break
        
        if end == '0':
            break
        
        for d in domain:
        
            response = requests.get('https://api.cloudflare.com/client/v4/zones?&name=' + d, headers = header)
            result = response.json()
            
            if result['result'] == []:
                print(d + ' 已被移除，不在帳號 ' + QQ2[a] +' 底下')
                print()
            
            elif result['success']:                    
                url = 'https://api.cloudflare.com/client/v4/zones/' + result['result'][0]['id'] 
                
                #Under Attack Mode
                
                if switch == '1':
                    data = '{"value":"under_attack"}'
                    
                if switch == '2':
                    data = '{"value":"medium"}'
                    
                response = requests.patch(url + '/settings/security_level', headers = header, data = data)
                result = response.json()
                
                if result['success']:
                    if switch == '1':
                        print(d + '  Under_Attack_Mode 已開啟')
                        
                    if switch == '2':
                        print(d + '  Under_Attack_Mode 已關閉')
                    
                else:
                    Fail(d + ' Under Attack Mode',result)
                
    
    
                #Bot Fight Mode
                
                if switch == '1':
                    data = '{"fight_mode":true}'
                    
                if switch == '2':
                    data = '{"fight_mode":false}'
                    
                response = requests.put(url + '/bot_management', headers = header, data = data)
                result = response.json()
                
               
                if switch == '1':
                    if result['result']['fight_mode'] == True:
                        print(d + '  Bot_Fight_Mode 已開啟')
                    else:
                        Fail(d + ' Bot_Fight_Mode',result)
                    
                if switch == '2':
                    if result['result']['fight_mode'] == False:
                        print(d + '  Bot Fight Mode 已關閉')
                    else:
                        Fail(d + ' Bot_Fight_Mode',result)
                    
    
    
                #HTTP DDoS attack protection
                response = requests.get(url + '/rulesets', headers = header)
                result = response.json()
    
                for i in range(len(result['result'])):
                    if result['result'][i]['phase'] == 'ddos_l7':
                        m_id = result['result'][i]['id']
                        break
    
                if switch == '1':
                    data = '{ "rules": [{"action": "execute", "action_parameters": {"id": "'+m_id+'","overrides": { "sensitivity_level": "medium", "action": "challenge"}},"expression": "true"}]}'
                    response = requests.put(url + '/rulesets/phases/ddos_l7/entrypoint', headers = header, data = data)
                    result = response.json() 
                    if result['success']:
                        print(d + '  HTTP_DDoS_attack_protection 已開啟')
    
                    else:
                        Fail(d + ' HTTP_DDoS_attack_protection',result)
                    
                if switch == '2':
                    response = requests.get(url + '/rulesets/phases/ddos_l7/entrypoint', headers = header)
                    result = response.json()
                    del_ddos_id = result['result']['id']
                    response = requests.delete(url + '/rulesets/' + del_ddos_id, headers = header)
                    if response.text == '':
                        print(d + '  HTTP_DDoS_attack_protection 已關閉')
                    else:
                        result = response.json() 
                        Fail(d + ' HTTP_DDoS_attack_protection',result)
                

    if choice == '2':
        while True:
            geoswitch = input('開啟特定地區限制請輸入 1，關閉請輸入 2 : ')
            geoswitch = geoswitch.strip(' \t\n\r')
            
            if geoswitch == '1' or geoswitch == '2':
                end = 1
                break
            
            else:
                print('輸入錯誤')
                end = input('按enter繼續，或按0離開：')
                print()
                if end == '0':
                    break
        if end == '0':
            break               
        
        
                
        SwitchGeo(geoswitch, domain, header, a)        

    end = input('按enter繼續，或按0離開：')
            
    if end == '0':
        break
    print('----------------------分隔線----------------------')
