from dataclasses import dataclass

@dataclass(eq=False)
class TelethonLog:
    api_id: int
    api_hash: str
    phone_number: str
    proxy: str | None

    def return_self(self):
        log = f'| api_id: {self.api_id} |\n| api_hash: {self.api_hash} |\n| phone_number: {self.phone_number} |\n| proxy: {self.proxy}'
        return log