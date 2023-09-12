from flask import Flask, jsonify
import csv
import re

app = Flask(__name__)


# Словарь со значениями часовых поясов UTC
# Уникальные значения часовых поясов спарсил из RU.txt.
# Из словаря получаем значения UTC по ключу. 
timezone_utc = {
    'Europe/Kaliningrad': 2, 'Europe/Warsaw': 2,
    'Asia/Ulaanbaatar': 8, 'Asia/Yakutsk': 9,
    'Europe/Astrakhan': 4, 'Asia/Novosibirsk': 7,
    'Asia/Magadan': 11, 'Europe/Minsk': 3,
    'Asia/Anadyr': 12, 'Asia/Aqtobe': 5,
    'Europe/Helsinki': 3, 'Europe/Vilnius': 3,
    'Europe/Ulyanovsk': 4, 'Europe/Volgograd': 3,
    'Europe/Oslo': 2, 'Europe/Monaco': 2,
    'Asia/Tokyo': 9, 'Asia/Shanghai': 8,
    'Asia/Krasnoyarsk': 7, 'Asia/Omsk': 6,
    'Europe/Simferopol': 3, 'Asia/Vladivostok': 10,
    'Asia/Qyzylorda': 6, 'Asia/Tomsk': 7,
    'Europe/Riga': 3, 'Asia/Barnaul': 7,
    'Asia/Ashgabat': 5, 'Asia/Tashkent': 5,
    'Asia/Tbilisi': 4, 'Europe/Paris': 2,
    'Europe/Saratov': 4, 'Asia/Srednekolymsk': 11,
    'Asia/Khandyga': 9, 'Europe/Moscow': 3,
    'Asia/Almaty': 6, 'Asia/Hovd': 7,
    'Asia/Kamchatka': 12, 'Europe/Kyiv': 3,
    'Asia/Irkutsk': 8, 'Asia/Ust-Nera': 10,
    'Europe/Kirov': 3, 'Europe/Samara': 4,
    'Asia/Novokuznetsk': 7, 'Asia/Baku': 4,
    'Asia/Chita': 9, 'Asia/Sakhalin': 11,
    'Asia/Yekaterinburg': 5
}


data = [] # Данные храним в     
with open('GEO.txt', 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        data.append({
            "geonameid": int(row[0]),
            "name": row[1],
            "asciiname": row[2],
            "alternatenames": row[3],
            "latitude": float(row[4]),
            "longitude": float(row[5]),
            "feature_class": row[6],
            "feature_code": row[7],
            "country_code": row[8],
            "cc2": row[9],
            "admin1_code": row[10],
            "admin2_code": row[11],
            "admin3_code": row[12],
            "admin4_code": row[13],
            "population": int(row[14]),
            "elevation": row[15],
            "dem": row[16],
            "timezone": row[17],
            "modification_date": row[18]
        })


# Подсказка, возвращающая возможные варианты предложений
def find_similar_cities(city_name, data):
    """Функция, возвращающая подсказки если город по запросу не найден.
    
        Описание:
            Функция ищет все города из массива data, название которых содержит подстроку, заданную аргументом city_name
            (регистр букв не учитывается), и возвращает список этих городов в виде массива строк.
            Если совпадений не найдено, функция вернет пустой список

        Аргументы:
            city_name - строка с названием города / id города
            data - массив в котором хранятся значения
    """
    similar_cities = []
    for city in data:
        try:
            if isinstance(city_name, str): 
                if re.search(city_name, city['alternatenames'], re.IGNORECASE):
                    similar_cities.append(city['alternatenames'])
            elif isinstance(city_name, int):
                if re.search(str(city_name), str(city["geonameid"])):
                    similar_cities.append(city["alternatenames"])
        except:
            return "Неверный запрос. Посмотрите документацию :)  "
    return similar_cities[:20]


@app.route('/city/<int:geonameid>', methods=['GET'])
def city(geonameid):
    """Функция, принимающая уникальный номер города (geonameid).

        Описание:
            Если город найден, то возвращается информация о нем в формате JSON.
            Если же город не найден, то возвращаются подсказки с возможными именами городов.

        Пример обращения:
            .../city/479560

        Аргументы:
            geonameid - geonameid города
    """
    for city in data:
        if city["geonameid"] == geonameid:
            return jsonify(city)
    codes_aproximate = find_similar_cities(geonameid, data) # Если город не найден, совершаем поиск по этому id
    response = {f"Город по коду {geonameid} не найден. Возможно, вы имели ввиду": codes_aproximate}
    return jsonify(response) # если город не найден



@app.route('/cities/<int:page>/<int:on_page>', methods=['GET'])
def cities(page, on_page):
    """Функция, принимающая страницу и кол-во отображаемых сттаниц.

        Описание:
            На каждой странице отображается on_page городов, начиная с индекса (page-1)*on_page.
            Возвращаемый список содержит только необходимую информацию о городах
            (geonameid, name, country_code, population) и представлен в формате JSON.

        Пример обращения:
            .../cities/1/25

        Аргументы:
            page - номер страницы
            on_page - количество отображаемых элементов на странице 
    """
    start_idx = (page-1) * on_page
    end_idx = start_idx + on_page
    cities_list = []
    for city in data[start_idx:end_idx]:
        cities_list.append({
            "geonameid": city["geonameid"],
            "name": city["name"],
            "asciiname": city["asciiname"],
            "alternatenames": city["alternatenames"],
            "latitude": city["latitude"],
            "longitude": city["longitude"],
            "feature_class": city["feature_class"],
            "feature_code": city["feature_code"],
            "country_code": city["country_code"],
            "cc2": city["cc2"],
            "population": city["population"],
            "elevation": city["elevation"],
            "dem": city["dem"],
            "timezone": city["timezone"]
        })
    return jsonify(cities_list)


@app.route('/city-compare/<rus_city1>/<rus_city2>', methods = ['GET'])
def city_compare(rus_city1, rus_city2):
    """Функция, принимающая названия двух городов на русском и показывающий информацию о них

        Описание: 
            При обращении к эндпоинту city-compare/<str:rus_city1>/<str:rus_city2>
            выводится информация о двух городах, название самого северного города, 
            информация о схожих часовых зонах (True/False) и разница в часовых поясах.

        Пример обращения:
            .../city-compare/Уфа/Санкт Петербург

        Аргументы:
            rus_city1 - название города на русском
            rus_city2 - название города на русском
    """
    # Лямбда, производящая поиск по столбцу alternatenames
    find_city = lambda city_name: next((city for city in data if city_name.lower() in city['alternatenames'].lower().split(',')), None)
    

    city1_info = find_city(rus_city1)
    city2_info = find_city(rus_city2)

    # Лямбда, которая меняет ссылку на объект, если названия одинаковые
    same_name_exception = lambda city_name, p_id: next((city for city in data if city_name.lower() in city['alternatenames'].lower().split(',') and (city1_info != None) and p_id != city["geonameid"] ), None)
    
    # Проверка на идентичность имен
    if city1_info == city2_info:
        if city1_info != None:
            city2_info = same_name_exception(rus_city2, city1_info["geonameid"])
        pass


    if city1_info is None:
        probable_name = find_similar_cities(rus_city1, data)
        response = {f"Город {rus_city1} не найден. Возможно, вы имели ввиду": probable_name}
        return jsonify(response)
    
    if city2_info is None:
        probable_name = find_similar_cities(rus_city2, data)
        response = {f"Город {rus_city2} не найден. Возможно, вы имели ввиду": probable_name}
        return jsonify(response)
    
    
    if city1_info['latitude'] > city2_info['latitude']:
        northern_city = city1_info['name']
    elif city1_info['latitude'] < city2_info['latitude']:
        northern_city = city2_info['name']
    else:
        northern_city = 'Нет данных'
    
    if city1_info['timezone'] == city2_info['timezone']:
        same_timezone = True
    else:
        same_timezone = False
    
    # Дополнительное задание (вычислить разницу часовых поясов).
    difference_timezone = timezone_utc[city2_info["timezone"]] - timezone_utc[city1_info["timezone"]]

    response = {
        'Город 1': city1_info,
        'Город 2': city2_info,  
        'Самый северный': northern_city,
        'Равновеликие ли временные зоны': same_timezone,
        'Разница часовых поясов (в часах)': difference_timezone
    }
    return jsonify(response)
    

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=8000) # перед деплоем снять debug - мод
