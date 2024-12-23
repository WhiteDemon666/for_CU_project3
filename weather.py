# Класс, который оценивает погоды и хранит в себе данные о погоде
class WeatherAssessment:
    def __init__(self, loc, day, day_part, temp, wind_speed, rain_prob, humidity):
        self.location = loc
        self.day = day
        self.day_part = day_part
        self.temperature = temp
        self.wind_speed = wind_speed
        self.rain_probability = rain_prob
        self.humidity = humidity
        self.message = None
        self.check_bad_weather()

    def check_bad_weather(self):
        # Оцениваем благоприятность погоды по выделенным критериям
        if self.temperature < 0:
            self.message = 'Слишком низкая температура, ниже 0°C'
        elif self.temperature > 35:
            self.message = 'Слишком высокая температура, выше 35°C'

        elif self.wind_speed > 50:
            self.message = 'Слишком большая скорость ветра, выше 50 км/ч'

        elif self.rain_probability > 70:
            self.message = 'Высокая вероятность осадков, свыше 70%'

        elif self.humidity < 20:
            self.message = 'Слишком низкая влажность воздуха, ниже 20%'
        elif self.humidity > 95:
            self.message = 'Слишком высокая влажность воздуха, выше 95%'

        else:
            self.message =  'Погодные условия - благоприятные'
