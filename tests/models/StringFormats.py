from pydantic import BaseModel, Field

class StringFormats(BaseModel):
    email: str = Field(format='email')
    hostname : str = Field(format='hostname')
    ip4address: str = Field(format='ipv4')
    ip6address: str = Field(format='ipv6')
    uri: str = Field(format='uri')
    uuid: str = Field(format='uuid')

    @classmethod
    def valid_cases(cls):
        return [
            {
                "email": "example@test.com",
                "hostname": "example.com",
                "ip4address": "192.168.1.1",
                "ip6address": "2001:0000:130F:0000:0000:09C0:876A:130B",
                "uri": "https://example.com",
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
            }
        ]

    @classmethod
    def invalid_cases(cls):
         return [
            {
                "email": "exampletest.com",
                "hostname": "exa_mple.com",
                "ip4address": "192.168.1.1000",
                "ip6address": "::1000",
                "uri": "https://example.com",
                "uuid": "550e8400-e29b-41d4-a716-446655440000XXXXXX",
            }
        ]