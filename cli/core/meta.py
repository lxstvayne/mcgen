import tomllib
import pydantic


class PackageMetadataInfo(pydantic.BaseModel):
    name: str
    version: str

    @classmethod
    def from_poetry_config_file(cls, path: str):
        with open(path, 'rb') as f:
            data = tomllib.load(f)

        config = {
            'name': data['tool']['poetry']['name'],
            'version': data['tool']['poetry']['version'],
        }

        return cls(**config)
