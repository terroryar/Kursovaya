
import requests
import json
from tqdm import tqdm
import webview
import urllib.parse
from pprint import pprint

#  данные приложения VK
client_id = '51774213'
redirect_uri = 'https://oauth.vk.com/blank.html'
scope = 'status,photos'


# страница авторизации VK
window = webview.create_window(
    title='VK Auth',
    url=f'https://oauth.vk.com/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type=token'
)

class vk_token():
    def __init__(self,token):
        self.token=''



# функция обработки изменения URL-адреса
def handle_url(window):

    current_url = window.get_current_url()

    if current_url.startswith(redirect_uri):

        url_params = urllib.parse.urlparse(current_url)
        fragment_params = urllib.parse.parse_qs(url_params.fragment)
        access_token = fragment_params.get('access_token', [''])[0]
        expires_in = fragment_params.get('expires_in', [''])[0]
        token_vk.token = access_token
        window.destroy()


def get_vk_photos(user_id, access_token):
    url = f"https://api.vk.com/method/photos.get?owner_id={user_id}&access_token={access_token}&album_id=298389765&extended=1&v=5.131"
    response = requests.get(url)
    photos = response.json()["response"]["items"]
    #print(photos)
    return photos


def filter_photos(photos):
    filtered_photos = filter(lambda photo: "sizes" in photo, photos)
    return filtered_photos


def create_yandex_disk_folder(folder_name, access_token):
    url = f"https://cloud-api.yandex.net/v1/disk/resources?path={folder_name}"
    headers = {"Authorization": f"OAuth {access_token}"}
    response = requests.put(url, headers=headers)
    print(response.status_code)



def save_photo_to_yandex_disk(photo_url, folder_name,photo_name, access_token):
    url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = {"Authorization": access_token}
    params={'path':f'{folder_name}/{photo_name}.jpg'}
    response = requests.get(url, headers=headers, params=params)
    r = requests.get(photo_url)
    requests.put(url= response.json().get('href',''), data = r)


def save_photos(user_id, access_token,access_token_vk,folder_name="Photos"):
    photos = get_vk_photos(user_id, access_token_vk)
    filtered_photos = filter_photos(photos)
    dict_out=[]
    a={}
    photo_name = ''
    photo_likes=[]
    for photo in photos:
        photo_likes.append(photo['likes']['count'])
    #print(photo_likes)
    for photo in tqdm(filtered_photos, bar_format="{l_bar}{bar:20}{r_bar}", desc="Saving photos"):
        if photo_likes.count(photo['likes']['count']) >= 2:
            photo_name=f"{photo['likes']['count']}_{photo['id']}"
        max_size = max(photo["sizes"], key=lambda size: size["width"] * size["height"])
        save_photo_to_yandex_disk(max_size["url"], folder_name,photo_name, access_token)
        a['file_name'] =  photo_name
        a['size'] = max_size['type']
        dict_out.append(a)
    #pprint(dict_out)
    with open("photos.json", "w") as file:
        json.dump(dict_out, file)







if __name__ == "__main__":
    token_vk = vk_token('')
    window.events.loaded += lambda: handle_url(window)
    user_id = input("Enter VK user id: ")
    yandex_token = input("Enter Yandex.Disk access token: ")
    webview.start()
    save_photos(user_id, yandex_token, token_vk.token,folder_name="Photos")


