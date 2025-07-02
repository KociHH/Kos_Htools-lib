from datetime import datetime, timedelta
import pytz
from pytz.tzinfo import StaticTzInfo, DstTzInfo, BaseTzInfo

moscow_time = pytz.timezone('Europe/Moscow')

class DateTemplate:
    def __init__(self, selected_time: BaseTzInfo | StaticTzInfo | DstTzInfo | None = None):
        """
        Инициализирует экземпляр класса для работы с датами и временем.

        Args:
            selected_time: Объект часового пояса pytz, который будет использоваться
                           для всех расчетов времени. Например: `pytz.timezone('Europe/Berlin')`.
                           Если не указан, по умолчанию используется `pytz.timezone('Europe/Moscow')`.
        """

        self.selected_time = selected_time if selected_time else moscow_time
        self.now = datetime.now(self.selected_time)
    
    def conclusion_date(self, option: str) -> str | int:
        if option == 'date':
            timed = self.now.date()
        
        elif option == 'time_info_style_str':
            timed = self.now.strftime(
                f"Дата: {f'%d.%m.%Y'}\n"
                f"Время: {'%H:%M'}"
                )
        elif option == 'time_and_date_str':
            timed = self.now.strftime(f'%d.%m.%Y %H:%M')
        
        elif option == 'time_now':
            timed = self.now.replace(microsecond=0)
            
        elif option == 'fromtimestamp':
            timed = int(self.now.timestamp())
    
        else:
            raise ValueError('Такого объекта не представленно в функции.')
        return timed
    
    def custom_date(self, add_time: dict | None):   
        new_time = self.now
        
        if add_time:
            years = add_time.get('year', 0)
            months = add_time.get('moth', 0)
            days = add_time.get('day', 0)
            hours = add_time.get('hour', 0)
            minutes = add_time.get('minute', 0)
            seconds = add_time.get('second', 0)
            new_time = self.now + timedelta(
                year = years,
                month = months,
                days = days,
                hours = hours,
                minutes = minutes,
                seconds = seconds
            )
            
        timed = {
            "year": new_time.year,
            "month": new_time.month,
            "day": new_time.day,
            "hour": new_time.hour,
            "minute": new_time.minute,
            "second": new_time.second,
        }

        return timed
    