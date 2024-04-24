from datetime import date
import folium
import requests

#TODO - add source and type of threats, maybe integrate into python directly
API_KEYS = [XXXXXX]
current_date = date.today()
sirens_url = f"https://www.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx?lang=he&fromDate=07.10.23&toDate={current_date.day}.{current_date.month}.{current_date.year}&mode=0"


def get_res(map_url_req, c_name) -> tuple:
    in_name = ""
    res_i = {}
    try:
        res_i = requests.get(map_url_req).json()['results']
        print(res_i)
        if 'name' not in res_i[0].keys():
            in_name = c_name
        else:
            in_name = res_i[0]['name']
    except (KeyError, IndexError, requests.exceptions.ConnectionError) as e:
        print('error at', c_name, e)
        return ()
    return in_name, res_i[0]['lat'], res_i[0]['lon']


sirens_res = requests.get(sirens_url).json()
list_tuple_places = set([(i['data'].strip(), i['category_desc']) for i in sirens_res])
list_places = list(set([i['data'].strip() for i in sirens_res]))
print(list_tuple_places)
m = folium.Map(location=[32.0879048, 34.7148434], zoom_start=7)  # LOCATION OF TEL AVIV
len_list = len(list_places)
i = 0
for c in list_places:
    print(f'currently at "{c}" \t ,{len_list - i} remaining')
    i += 1
    map_url = f"https://api.geoapify.com/v1/geocode/search?text={c}&format=json&apiKey={API_KEYS[0]}"
    try:
        ans_tup = get_res(map_url, c)
        if len(ans_tup) > 0:
            folium.Marker(
                location=[ans_tup[1], ans_tup[2]],
                tooltip="Threat!",
                popup=f"<b>{ans_tup[0]}</b><br>" + ','.join([i[1].strip() for i in list_tuple_places if i[0] == c]),
                icon=folium.Icon(icon="info-sign", color='red')
            ).add_to(m)
    except requests.exceptions.ConnectionError as p:
        print("ERROR", p, "\nTRYING TO RESTORE")
        map_url = f"https://api.geoapify.com/v1/geocode/search?text={c}&format=json&apiKey={API_KEYS[0]}"
        while len(API_KEYS) > 0:
            ans_tup_er = get_res(map_url, c)
            if ans_tup_er != ():
                print("SUCCEEDED!", API_KEYS[0])
                folium.Marker(
                    location=[ans_tup_er[1], ans_tup_er[2]],
                    tooltip="Threat",
                    popup=f"<b>{ans_tup_er[0]}</b><br>" + ','.join([i[1].strip() for i in list_tuple_places if i[0] == c]),
                    icon=folium.Icon(icon="info-sign", color='red')
                ).add_to(m)
                break
            API_KEYS.pop(0)

        if len(API_KEYS) == 0:
            break

m.save(f'{current_date.day}-{current_date.month}-{current_date.year}.html')
