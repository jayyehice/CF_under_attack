import requests
import time
from fail import Fail
from cfapikey import CfApiKey

account, QQ, QQ2 = CfApiKey()

def create_domain_filters(domain, zone_id, filters_setting, header):
    data = '[{"expression": "' + filters_setting + '"}]'
    try:
        # create filters
        cf = requests.post('https://api.cloudflare.com/client/v4/zones/' + zone_id + '/filters', data=data,
                           headers=header, timeout=(10, 60))
        temp = cf.json()
        # print(temp)
        # create filters or get existence filters ID
        if temp['success']:
            filters_id = temp['result'][0]['id']
        else:
            if str(temp['errors'][0]['message']) == 'config duplicates an already existing config':
                filters_id = temp['errors'][0]['meta']['id']
            else:
                print(domain + ' 建立filters失敗。請參考cloudflare的錯誤訊息 ', end='')
                print(temp)
                filters_id = 'fail'
        return filters_id
    except:
        print(domain + ' 建立filter規則失敗。10秒後重試')
        time.sleep(10)
        create_domain_filters(domain, zone_id, filters_setting, header)

def create_domain_firewall_rules(domain, zone_id, filters_id, firewall_rules_action, firewall_rules_name,
                                 filters_switch, header):
    data = '[{"filter": {"id": "' + filters_id + '"},"action": "' + firewall_rules_action + '","description": "' + firewall_rules_name + '","paused":' + filters_switch + '}]'
    # print(data)
    try:
        # create firewall rules
        cf = requests.post('https://api.cloudflare.com/client/v4/zones/' + zone_id + '/firewall/rules', data=data,
                           headers=header, timeout=(10, 60))
        temp = cf.json()
        # print(temp)
        # create firewall rules
        if temp['success']:
            print(domain + ' 建立firewall rules: ' + firewall_rules_name + ' 成功')
        else:
            if str(temp['errors'][0]['message']).startswith('config duplicates an already existing config'):
                # print(domain+' 重複建立firewall rules name: '+firewall_rules_name+' 下面是cloudflare的回應',end=' ')
                # print(temp)
                firewall_rules_id = temp['errors'][0]['meta']['id']
                update_domain_firewall_rules(domain, zone_id, firewall_rules_id, filters_id, firewall_rules_action,
                                             firewall_rules_name, filters_switch, header)
            else:
                print(domain + ' 建立firewall rules失敗。請參考cloudflare的錯誤訊息')
                print(temp)
    except:
        print('建立firewall Rules規則失敗。10秒後重試')
        time.sleep(10)
        create_domain_firewall_rules(domain, zone_id, filters_id, firewall_rules_action, firewall_rules_name,
                                     filters_switch, header)

def update_domain_firewall_rules(domain, zone_id, firewall_rules_id, filters_id, firewall_rules_action,
                                 firewall_rules_name, filters_switch, header):
    data = '[{"id": "' + firewall_rules_id + '","filter": {"id": "' + filters_id + '"},"action": "' + firewall_rules_action + '","description": "' + firewall_rules_name + '","paused":' + filters_switch + '}]'
    try:
        # create firewall rules
        cf = requests.put('https://api.cloudflare.com/client/v4/zones/' + zone_id + '/firewall/rules', data=data,
                          headers=header, timeout=(10, 60))
        temp = cf.json()
        # print(temp)
        # create firewall rules
        if temp['success']:
            print(domain + ' 修改firewall rules: ' + firewall_rules_name + ' 狀態成功')
        else:
            print(domain + ' 修改firewall rules。請參考cloudflare的錯誤訊息')
            print(temp)
    except:
        print('更新firewall Rules規則失敗。10秒後自動重試')
        time.sleep(10)
        update_domain_firewall_rules(domain, zone_id, firewall_rules_id, filters_id, firewall_rules_action,
                                     firewall_rules_name, filters_switch, header)
        
def SwitchGeo(geoswitch, domain, header, a):
    if geoswitch == '1':

        while True:
            country_list = {'0':'"CN" ', '1':'"ID" ', '2':'"KP" "KR" ', '3':'"MY" ', '4':'"TH" ', '5':'"US" "CA" ', '6':'"VN" '}
            print('中國(0)、印尼(1)、韓國(2)、馬來西亞(3)、泰國(4)、美國(5)、越南(6)')
            print('請輸入國別代號，並用逗號分隔，ex:0,1,2,3,4,5,6')
            countrycode=input('請輸入代號 : ')
            countrycode=countrycode.split(',')
            
            countrystring = ''
            
            try:
                for i in countrycode:
                    countrystring += country_list[i]
                    country_list.pop(i)
                
                break
            
            except:
                input('輸入錯誤，按Enter 重新輸入')
        
        filters_setting = '(not ip.geoip.country in {' + countrystring + '})'
        filters_setting = filters_setting.replace('"', '\\"') 


        for d in domain:
            response = requests.get('https://api.cloudflare.com/client/v4/zones?&name=' + d, headers = header)
            result = response.json()
            
            if result['result'] == []:
                print(d + ' 已被移除，不在帳號 ' + QQ2[a] +' 底下')
                print()
            
            elif result['success']:                    
                #url = 'https://api.cloudflare.com/client/v4/zones/' + result['result'][0]['id'] 
                d_id = result['result'][0]['id']

        
                # create filters
                filters_id = create_domain_filters(d, d_id, filters_setting, header)
                firewall_rules_action = str('block')
                firewall_rules_name = str('under attack allow conutry')
                geo_country_rules_status = str('false')
                
                # create domain firewall filters
                if not filters_id == 'fail':
                    create_domain_firewall_rules(d, d_id, filters_id, firewall_rules_action, firewall_rules_name, geo_country_rules_status, header)
                
                else:
                    print(d + '添加失敗 下面是cloudflare的回應')
                    print('將會繼續添加剩下的域名')
    
    if geoswitch == '2':

        for d in domain:
            response = requests.get('https://api.cloudflare.com/client/v4/zones?&name=' + d, headers = header)
            result = response.json()
            
            if result['result'] == []:
                print(d + ' 已被移除，不在帳號 ' + QQ2[a] +' 底下')
                print()
            
            elif result['success']:                    
                url = 'https://api.cloudflare.com/client/v4/zones/' + result['result'][0]['id']         


            georulecheck = 0#判斷是否有該條規則，1為有
            
            #url = 'https://api.cloudflare.com/client/v4/zones/' + d_id
            
            zones = {'/firewall/rules':'Firewall Rules-under attack allow conutry'}
            
            for zone in zones:
                response = requests.get( url + zone, headers = header)
                result = response.json()
               
                if result['success']:
                    if result['result'] == []:
                        print(d + ' 底下沒有 ' + zones[zone])
                        
                    elif result['result'] != []:
                        for i in result['result']:   
                            #print(i['description'])
                            
                            if i['description'] == 'under attack allow conutry':
                                response = requests.delete( url + zone + '/' + i['id'], headers = header)
                                result = response.json()
                                georulecheck = 1
                                print(d + ' ' + zones[zone] + ' 刪除成功')
                                
                                
                        if georulecheck == 0:
                            print(d + ' 底下沒有設定 under attack allow conutry')
                    
                    else:
                        Fail(d + ' ' + zones[zone],result)
                else:
                    Fail(d + ' ' + zones[zone],result)




if __name__ == '__main__':
    header = {
        'x-auth-email': 'jayyehice@gmail.com',
        'X-Auth-Key': '9948bde0a2e7dae659e5cc0509c093cf342a6',    
        'Content-Type': 'application/json'
    }
      
    d = 'jayyehice.tk'
    domain = {'jayyehice.tk':'89c700ad601724a4b0f5fba6d5e0d0ed'}
    d_id = domain[d]
    
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
            
    SwitchGeo(geoswitch, d, d_id, header)



