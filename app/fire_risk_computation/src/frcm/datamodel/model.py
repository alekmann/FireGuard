from __future__ import annotations
from pathlib import Path
import datetime
from pydantic import BaseModel


class WeatherDataPoint(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    timestamp: datetime.datetime

    @classmethod
    def csv_header(cls) -> str:
        return "timestamp,temperature,humidity,wind_speed"

    def csv_line(self) -> str:
        return f"{self.timestamp.isoformat()},{self.temperature},{self.humidity},{self.wind_speed}"

    @classmethod
    def from_csv_line(cls, line: str) -> WeatherDataPoint:
        split_line = line.split(',')
        if len(split_line) != 4:
            raise ValueError("Given line has unexpexted format! Expects <timestamp:datetime,temperature:float,humidity:float,wind_speed:float> ")
        ts = datetime.datetime.fromisoformat(split_line[0])
        temp = float(split_line[1])
        hum = float(split_line[2])
        ws = float(split_line[3])
        return WeatherDataPoint(timestamp=ts, temperature=temp, humidity=hum, wind_speed=ws)

class WeatherData(BaseModel):
    data: list[WeatherDataPoint]

    def to_json(self):
        return self.model_dump_json()

    def write_csv(self, target: Path):
        handle = open(target, "w+")
        handle.write(WeatherDataPoint.csv_header())
        handle.write('\n')
        for d in self.data:
            handle.write(d.csv_line())
            handle.write('\n')
        handle.close()

    @classmethod
    def read_csv(cls, src: Path) -> WeatherData:
        result = []
        handle = open(src, "rt")
        for line in handle.readlines()[1:]:
            result.append(WeatherDataPoint.from_csv_line(line))
        handle.close()
        return WeatherData(data=result)



class FireRisk(BaseModel):
    timestamp: datetime.datetime
    ttf: float

    @classmethod
    def csv_header(cls) -> str:
        return "timestamp,ttf"

    def csv_line(self) -> str:
        return f"{self.timestamp.isoformat()},{self.ttf}"




class FireRiskPrediction(BaseModel):
    firerisks: list[FireRisk]

    def __str__(self) -> str:
        return "\n".join([FireRisk.csv_header()] + [r.csv_line() for r in self.firerisks])

    def write_csv(self, target: Path):
        handle = open(target, "w+")
        handle.write(FireRisk.csv_header())
        handle.write('\n')
        for r in self.firerisks:
            handle.write(r.csv_line())
            handle.write('\n')
        handle.close()

